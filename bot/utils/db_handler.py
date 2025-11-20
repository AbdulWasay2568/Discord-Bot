import sys
from pathlib import Path
import discord

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.future import select
from db.connection import AsyncSessionLocal
from db.queries.user import upsert_user
from db.queries.messages import create_message, update_message, delete_message
from models.models import User, Message, MessageType
from bot.utils.file_manager import download_attachment
from datetime import datetime

async def handle_message_save(message: discord.Message):
    """Save a message and its attachments to database."""
    if not message or not message.author:
        return

    async with AsyncSessionLocal() as db:
        try:
            # Upsert user
            user_model = User(
                id=int(message.author.id),
                username=getattr(message.author, "name", None),
                discriminator=getattr(message.author, "discriminator", None),
                global_name=getattr(message.author, "global_name", None),
                avatar=str(message.author.avatar.url) if getattr(message.author, "avatar", None) else None,
                bot=bool(getattr(message.author, "bot", False)),
                system=bool(getattr(message.author, "system", False)),
            )
            saved_user = await upsert_user(db, user_model)

            # Save attachments
            attachments_list = []
            for attachment in message.attachments:
                local_path, success = await download_attachment(
                    attachment.url,
                    attachment.filename,
                    message.id
                )
                attachments_list.append({
                    "id": attachment.id,
                    "filename": attachment.filename,
                    "url": attachment.url,
                    "content_type": getattr(attachment, "content_type", None),
                    "size": getattr(attachment, "size", None),
                    "local_path": local_path if success else None,
                    "is_downloaded": success,
                })

            message_type = getattr(message, "type", None)
            if isinstance(message_type, int):
                message_type = MessageType.DEFAULT
            elif isinstance(message_type, str):
                message_type = MessageType[message_type.upper()]
            else:
                message_type = MessageType.DEFAULT

            message_model = Message(
                id=int(message.id),
                channel_id=int(message.channel.id) if getattr(message, "channel", None) else None,
                author_id=saved_user.id,
                content=message.content,
                attachments=attachments_list,
                type=message_type,
                timestamp=getattr(message, "created_at", datetime.utcnow())
            )

            await create_message(db, message_model)

        except Exception as e:
            print(f"Error saving message: {e}")


async def handle_message_update(message: discord.Message):
    if not message or not message.author:
        return

    async with AsyncSessionLocal() as db:
        try:
            updates = {
                "content": message.content,
                "edited_timestamp": getattr(message, "edited_at", datetime.utcnow()),
            }

            # Update attachments if changed
            if message.attachments:
                attachments_list = []
                for attachment in message.attachments:
                    local_path, success = await download_attachment(
                        attachment.url,
                        attachment.filename,
                        message.id
                    )
                    attachments_list.append({
                        "id": attachment.id,
                        "filename": attachment.filename,
                        "url": attachment.url,
                        "content_type": getattr(attachment, "content_type", None),
                        "size": getattr(attachment, "size", None),
                        "local_path": local_path if success else None,
                        "is_downloaded": success,
                    })
                updates["attachments"] = attachments_list

            await update_message(db, message_id=int(message.id), author_id=int(message.author.id), updates=updates)
            print(f"Message {message.id} updated successfully.")

        except Exception as e:
            print(f"Error updating message: {e}")


async def handle_message_delete(message: discord.Message):
    if not message or not message.author:
        return

    async with AsyncSessionLocal() as db:
        try:
            await delete_message(db, message_id=int(message.id), author_id=int(message.author.id))
            print(f"Message {message.id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting message: {e}")

async def handle_reaction_add(reaction: discord.Reaction, user: discord.User):
    if user.bot:
        return

    async with AsyncSessionLocal() as db:
        try:
            # UPSERT USER
            db_user = await upsert_user(db, User(
                id=int(user.id),
                username=getattr(user, "name", None),
                discriminator=getattr(user, "discriminator", None),
                global_name=getattr(user, "global_name", None),
                avatar=str(getattr(user.avatar, "url", None)) if user.avatar else None,
                bot=bool(user.bot),
                system=bool(user.system),
            ))

            # FETCH MESSAGE
            result = await db.execute(select(Message).filter(Message.id == reaction.message.id))
            db_message = result.scalar_one_or_none()
            if not db_message:
                print(f"No message found in DB with ID {reaction.message.id}")
                return

            # EXTRACT EMOJI
            emoji_id = str(reaction.emoji.id) if hasattr(reaction.emoji, 'id') and reaction.emoji.id else None
            emoji_name = str(reaction.emoji.name) if hasattr(reaction.emoji, 'name') else str(reaction.emoji)

            reactions = db_message.reactions or []

            # CHECK IF THIS EMOJI ALREADY EXISTS IN REACTIONS
            existing_reaction = None
            for r in reactions:
                r_emoji = r.get('emoji', {})
                if (emoji_id and r_emoji.get('id') == emoji_id) or (not emoji_id and r_emoji.get('name') == emoji_name):
                    existing_reaction = r
                    break

            # UPDATE EXISTING OR ADD NEW REACTION
            if existing_reaction:
                if 'users' not in existing_reaction:
                    existing_reaction['users'] = []
                if db_user.id not in existing_reaction['users']:
                    existing_reaction['users'].append(db_user.id)
                existing_reaction['count'] = len(existing_reaction['users'])
                existing_reaction['count_details'] = {'burst': 0, 'normal': existing_reaction['count']}
            else:
                reactions.append({
                    'count': 1,
                    'count_details': {'burst': 0, 'normal': 1},
                    'me': False,
                    'me_burst': False,
                    'emoji': {'id': emoji_id, 'name': emoji_name},
                    'burst_colors': [],
                    'users': [db_user.id]
                })

            # IMPORTANT: Assign full list back to db_message.reactions
            db_message.reactions = reactions
            await db.commit()
            await db.refresh(db_message)

            print(f"Reaction added: emoji={emoji_name}, user={user.id}")

        except Exception as e:
            print(f"Error adding reaction: {e}")


async def handle_reaction_remove(reaction: discord.Reaction, user: discord.User):
    print(f"[REMOVE] Reaction removal triggered by user={user.id}, message={reaction.message.id}")

    if user.bot:
        print("[REMOVE] Ignored because user is a bot")
        return

    async with AsyncSessionLocal() as db:
        try:
            # 1) FETCH MESSAGE
            print(f"[REMOVE] Fetching message {reaction.message.id}...")
            result = await db.execute(select(Message).filter(Message.id == reaction.message.id))
            db_message = result.scalar_one_or_none()

            if not db_message:
                print(f"[REMOVE] ❌ No message found with ID {reaction.message.id}. Cannot remove reaction.")
                return

            print(f"[REMOVE] Message found: {db_message.id}")

            if not db_message.reactions:
                print("[REMOVE] Message has no reactions stored.")
                return

            # 2) EXTRACT EMOJI INFO
            emoji_id = str(reaction.emoji.id) if hasattr(reaction.emoji, 'id') and reaction.emoji.id else None
            emoji_name = str(reaction.emoji.name) if hasattr(reaction.emoji, 'name') else str(reaction.emoji)

            print(f"[REMOVE] Emoji extracted: id={emoji_id}, name={emoji_name}")

            updated_reactions = []

            # 3) FIND AND UPDATE REACTION ENTRY
            for r in db_message.reactions:
                if r.get('emoji', {}).get('id') == emoji_id and r.get('emoji', {}).get('name') == emoji_name:
                    print("[REMOVE] Matching reaction found.")

                    if 'users' in r and int(user.id) in r['users']:
                        print(f"[REMOVE] Removing user {user.id} from reaction...")
                        r['users'].remove(int(user.id))

                    r['count'] = len(r['users'])
                    r['count_details']['normal'] = r['count']

                    if r['count'] > 0:
                        updated_reactions.append(r)
                    else:
                        print("[REMOVE] Reaction count = 0 → removing reaction entry completely.")
                else:
                    updated_reactions.append(r)

            # 4) SAVE TO DB
            db_message.reactions = updated_reactions
            await db.commit()
            await db.refresh(db_message)

            print("[REMOVE] ✅ Reaction removed and DB updated successfully.")

        except Exception as e:
            print(f"[REMOVE] ❌ Error removing reaction: {e}")
