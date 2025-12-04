import asyncio
import discord
import time
from sqlalchemy import func, String
from sqlalchemy.future import select
from db.connection import AsyncSessionLocal
from db.queries.user import upsert_user
from db.queries.messages import create_message, update_message, delete_message, get_message, batch_create_messages, batch_update_messages, get_messages_batch
from db.schema import User, Message, MessageType
from bot.utils.file_manager import download_attachment
from datetime import datetime
from .serialize_datetime import serialize_datetime
from .response_time import format_elapsed_time


def build_message_model(msg: discord.Message, msg_data: dict) -> Message:
    return Message(
        id=int(msg.id),
        channel_id=int(msg.channel.id),
        author_id=msg_data["saved_user"].id,
        content=msg.content,
        attachments=msg_data["attachments_list"],
        embeds=msg_data["embeds_list"],
        reactions=msg_data["emojis_list"],
        type=msg_data["message_type"],
        timestamp=getattr(msg, "created_at", datetime.utcnow()),
        message_reference=msg_data["message_reference"],
        referenced_message=msg_data["referenced_message"]
    )


async def user_helper_function(db, discord_user: discord.User) -> User:
    user_model = User(
        id=int(discord_user.id),
        username=getattr(discord_user, "name", None),
        discriminator=getattr(discord_user, "discriminator", None),
        global_name=getattr(discord_user, "global_name", None),
        avatar=str(discord_user.avatar.url) if getattr(discord_user, "avatar", None) else None,
        bot=bool(getattr(discord_user, "bot", False)),
        system=bool(getattr(discord_user, "system", False)),
    )
    saved_user = await upsert_user(db, user_model)
    return saved_user
    

def reaction_dict(emoji, users_list):
    emoji_id = str(emoji.id) if hasattr(emoji, 'id') and emoji.id else None
    emoji_name = str(emoji.name) if hasattr(emoji, 'name') else str(emoji)
    
    return {
        'count': len(users_list),
        'count_details': {'burst': 0, 'normal': len(users_list)},
        'me': False,
        'me_burst': False,
        'emoji': {'id': emoji_id, 'name': emoji_name},
        'burst_colors': [],
        'users': users_list
    }


# async def extract_attachments(message: discord.Message):
#     attachments_list = []
#     for attachment in message.attachments:
#         local_path, success = await download_attachment(
#             attachment.url,
#             attachment.filename,
#             message.id
#         )
#         attachments_list.append({
#             "id": attachment.id,
#             "filename": attachment.filename,
#             "url": attachment.url,
#             "content_type": getattr(attachment, "content_type", None),
#             "size": getattr(attachment, "size", None),
#             "local_path": local_path if success else None,
#             "is_downloaded": success,
#         })
#     return attachments_list


async def extract_attachments(message: discord.Message):
    async def download_attachments(attachment):
        local_path, success = await download_attachment(
            attachment.url,
            attachment.filename,
            message.id
        )
        return {
            "id": attachment.id,
            "filename": attachment.filename,
            "url": attachment.url,
            "content_type": getattr(attachment, "content_type", None),
            "size": getattr(attachment, "size", None),
            "local_path": local_path if success else None,
            "is_downloaded": success,
        }
    
    attachments_list = await asyncio.gather(*[download_attachments(att) for att in message.attachments])
    return attachments_list

async def build_referenced_message(message_reference_data, message: discord.Message):
    if not message_reference_data:
        return None, None
    
    message_reference = {
        "message_id": getattr(message_reference_data, "message_id", None),
        "channel_id": getattr(message_reference_data, "channel_id", None),
        "guild_id": getattr(message_reference_data, "guild_id", None),
        "fail_if_not_exists": getattr(message_reference_data, "fail_if_not_exists", True)
    }

    # Try getting full referenced message
    ref_msg = getattr(message, "referenced_message", None)
    if not ref_msg and message_reference.get("channel_id") and message_reference.get("message_id"):
        try:
            ref_channel = message.guild.get_channel(message_reference["channel_id"]) \
                or await message.guild.fetch_channel(message_reference["channel_id"])
            ref_msg = await ref_channel.fetch_message(message_reference["message_id"])
        except:
            ref_msg = None

    referenced_message = None
    if ref_msg:
        referenced_message = {
            "id": int(ref_msg.id),
            "channel_id": int(ref_msg.channel.id) if getattr(ref_msg, "channel", None) else None,
            "author": {
                "id": int(ref_msg.author.id),
                "username": getattr(ref_msg.author, "name", None),
                "discriminator": getattr(ref_msg.author, "discriminator", None),
                "global_name": getattr(ref_msg.author, "global_name", None),
                "avatar": str(ref_msg.author.avatar.url) if getattr(ref_msg.author, "avatar", None) else None,
                "bot": bool(getattr(ref_msg.author, "bot", False)),
                "system": bool(getattr(ref_msg.author, "system", False)),
            },
            "content": ref_msg.content,
            "attachments": [att.to_dict() for att in getattr(ref_msg, "attachments", [])],
            "embeds": [emb.to_dict() for emb in getattr(ref_msg, "embeds", [])],
            "timestamp": serialize_datetime(getattr(ref_msg, "created_at", None)),
            "edited_timestamp": serialize_datetime(getattr(ref_msg, "edited_at", None)),
            "type": getattr(ref_msg, "type", None).name if getattr(ref_msg, "type", None) else None
        }
    
    return message_reference, referenced_message

async def fetch_reaction_data(reaction):
        users = [u.id async for u in reaction.users()]
        return reaction_dict(reaction.emoji, users)

async def prepare_message_data(message: discord.Message, db):
    # 1) Upsert user
    saved_user = await user_helper_function(db, message.author)

    # 2) Save attachments
    attachments_list = await extract_attachments(message)

    # 3) Save embeds
    embeds_list = [embed.to_dict() for embed in message.embeds]

    # 4) Save reactions
    emojis_list = await asyncio.gather(*[fetch_reaction_data(reaction) for reaction in message.reactions])

    # 5) Detect message type
    raw_type = getattr(message, "type", None)
    if isinstance(raw_type, int):
        message_type = MessageType.DEFAULT
    else:
        try:
            message_type = MessageType[raw_type.name]
        except:
            message_type = MessageType.DEFAULT

    # 6) Handle message_reference and referenced_message
    message_reference_data = getattr(message, "reference", None)
    message_reference, referenced_message = await build_referenced_message(
        message_reference_data, message
    )

    return {
        "saved_user": saved_user,
        "attachments_list": attachments_list,
        "embeds_list": embeds_list,
        "emojis_list": emojis_list,
        "message_type": message_type,
        "message_reference": message_reference,
        "referenced_message": referenced_message,
    }


async def handle_message_save(message: discord.Message):
    if not message or not message.author:
        return

    async with AsyncSessionLocal() as db:
        try:
            # Prepare all message data
            msg_data = await prepare_message_data(message, db)

            # Build message model
            message_model = build_message_model(message, msg_data)

            await create_message(db, message_model)
            print(f"Message {message.id} saved successfully.")

        except Exception as e:
            print(f"Error saving message: {e}")


async def handle_message_update(message: discord.Message):
    if not message or not message.author:
        return

    async with AsyncSessionLocal() as db:
        try:
            # Prepare all message data
            msg_data = await prepare_message_data(message, db)

            updates = {
                "content": message.content,
                "edited_timestamp": getattr(message, "edited_at", datetime.utcnow()),
                "attachments": msg_data["attachments_list"],
                "embeds": msg_data["embeds_list"],
                "reactions": msg_data["emojis_list"],
            }

            if msg_data["message_reference"]:
                updates["message_reference"] = msg_data["message_reference"]
            if msg_data["referenced_message"]:
                updates["referenced_message"] = msg_data["referenced_message"]

            # Save updates
            await update_message(
                db,
                message_id=int(message.id),
                author_id=int(message.author.id),
                updates=updates
            )

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
            db_user = await user_helper_function(db, user)

            result = await db.execute(select(Message).filter(Message.id == reaction.message.id))
            db_message = result.scalar_one_or_none()
            if not db_message:
                print(f"No message found in DB with ID {reaction.message.id}")
                return

            emoji_id = str(reaction.emoji.id) if hasattr(reaction.emoji, 'id') and reaction.emoji.id else None
            emoji_name = str(reaction.emoji.name) if hasattr(reaction.emoji, 'name') else str(reaction.emoji)

            reactions = db_message.reactions or []

            existing_reaction = None
            for r in reactions:
                r_emoji = r.get('emoji', {})
                if (emoji_id and r_emoji.get('id') == emoji_id) or (not emoji_id and r_emoji.get('name') == emoji_name):
                    existing_reaction = r
                    break

            if existing_reaction:
                if 'users' not in existing_reaction:
                    existing_reaction['users'] = []
                if db_user.id not in existing_reaction['users']:
                    existing_reaction['users'].append(db_user.id)
                reactions[reactions.index(existing_reaction)] = reaction_dict(reaction.emoji, existing_reaction['users'])
            else:
                reactions.append(reaction_dict(reaction.emoji, [db_user.id]))

            db_message.reactions = reactions
            await db.commit()
            await db.refresh(db_message)

            print(f"Reaction added: emoji={emoji_name}, user={user.id}, message={reaction.message.id}")

        except Exception as e:
            print(f"Error adding reaction: {e}")


async def handle_reaction_remove(reaction: discord.Reaction, user: discord.User):
    if user.bot:
        return

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(Message).filter(Message.id == reaction.message.id))
            db_message = result.scalar_one_or_none()

            if not db_message:
                print(f"No message found with ID {reaction.message.id}. Cannot remove reaction.")
                return

            if not db_message.reactions:
                return

            # 2) EXTRACT EMOJI INFO
            emoji_id = str(reaction.emoji.id) if hasattr(reaction.emoji, 'id') and reaction.emoji.id else None
            emoji_name = str(reaction.emoji.name) if hasattr(reaction.emoji, 'name') else str(reaction.emoji)

            print(f"Emoji extracted: id={emoji_id}, name={emoji_name}")

            updated_reactions = []

            # 3) FIND AND UPDATE REACTION ENTRY
            for r in db_message.reactions:
                if r.get('emoji', {}).get('id') == emoji_id and r.get('emoji', {}).get('name') == emoji_name:

                    if 'users' in r and int(user.id) in r['users']:
                        print(f"[REMOVE] Removing user {user.id} from reaction...")
                        r['users'].remove(int(user.id))

                    r['count'] = len(r['users'])
                    r['count_details']['normal'] = r['count']

                    if r['count'] > 0:
                        updated_reactions.append(r)
                else:
                    updated_reactions.append(r)

            # 4) SAVE TO DB
            db_message.reactions = updated_reactions
            await db.commit()
            await db.refresh(db_message)

            print("Reaction removed and DB updated successfully.")

        except Exception as e:
            print(f"Error removing reaction: {e}")

async def filter_command(filters: dict):

    async with AsyncSessionLocal() as db:
        try:
            query = select(Message)
                        
            if filters.get("channels") and len(filters["channels"]) > 0:
                channel_ids = []
                for channel in filters["channels"]:
                    try:
                        channel_ids.append(int(channel))
                    except ValueError:
                        pass
                if channel_ids:
                    query = query.filter(Message.channel_id.in_(channel_ids))
            
            if filters.get("members") and len(filters["members"]) > 0:
                member_ids = []
                for member in filters["members"]:
                    try:
                        member_ids.append(int(member))
                    except ValueError:
                        pass
                if member_ids:
                    query = query.filter(Message.author_id.in_(member_ids))
            
            if filters.get("from_date"):
                query = query.filter(Message.timestamp >= filters["from_date"])
            if filters.get("to_date"):
                query = query.filter(Message.timestamp <= filters["to_date"])
            
            if filters.get("has_attachments") is True:
                query = query.filter(func.json_array_length(Message.attachments) > 0)
            
            if filters.get("attachment_name_contains"):
                search_term = filters["attachment_name_contains"]
                query = query.filter(
                    func.cast(Message.attachments, String).ilike(f"%{search_term}%")
                )
            
            sort_by = filters.get("sort_by", "desc")
            if sort_by == "asc":
                query = query.order_by(Message.timestamp.asc())
            elif sort_by == "reactions_desc":
                query = query.order_by(func.json_array_length(Message.reactions).desc())
            else:
                query = query.order_by(Message.timestamp.desc())
            
            limit = filters.get("limit", 20)
            
            if not (filters.get("reactions") and len(filters["reactions"]) > 0):
                query = query.limit(limit)
            
            result = await db.execute(query)
            messages = result.scalars().all()
            
            if filters.get("reactions") and len(filters["reactions"]) > 0:
                filtered_messages = []
                
                for msg in messages:
                    if msg.reactions:  
                        for emoji_input in filters["reactions"]:
                            emoji_found = False
                            
                            for reaction in msg.reactions:
                                reaction_emoji = reaction.get('emoji', {})
                                reaction_emoji_name = reaction_emoji.get('name', '')

                                if reaction_emoji_name == emoji_input:
                                    emoji_found = True
                                    break
                            
                            if emoji_found:
                                filtered_messages.append(msg)
                                break
                
                messages = filtered_messages[:limit]
            
            return messages
            
        except Exception as e:
            return []

async def get_latest_message_in_channel(channel_id: int) -> Message| None:
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Message)
                .where(Message.channel_id == channel_id)
                .order_by(Message.timestamp.desc())
                .limit(1)
            )
            message = result.scalar_one_or_none()
            if message:
                print('Latest message ID fetched from DB:', message.id)
                return message.id
            return None
        except Exception as e:
            print(f"Error fetching latest message in channel {channel_id}: {e}")
            return None

async def fetch_discord_history(channel, message_id=None, backfill=False):
    messages = []
    try:
        if backfill:
            print('fetching discord history before last message...')
            async for message in channel.history(limit=100, before=discord.Object(id=message_id) if message_id else None):
                messages.append(message)
            return messages
        
        print('fetching discord history after last message...')
        async for message in channel.history(limit=100, after=discord.Object(id=message_id) if message_id else None):
            messages.append(message)
        return messages
    except Exception as e:
        print(f"Error fetching discord history: {e}")
        return []

async def reconcile_channel(channel: discord.TextChannel, backfill: bool):
    try:
        start_time = time.time()
        latest_message_id = await get_latest_message_in_channel(channel.id)
        
        async with AsyncSessionLocal() as db:            
            while True:
                messages = await fetch_discord_history(channel, latest_message_id, backfill=backfill)

                if not messages:
                    break

                print(f"Fetched {len(messages)} messages from Discord")
                
                # Get all message IDs for batch lookup
                message_ids = [msg.id for msg in messages]
                existing_messages = await get_messages_batch(db, message_ids)
                
                # Separate into new messages and messages to update
                new_messages = []
                updates_list = []
                
                for msg in messages:
                    existing_msg = existing_messages.get(msg.id)
                    
                    if existing_msg:
                        # Check if message was edited
                        if msg.edited_at != existing_msg.edited_timestamp:
                            # Prepare message data
                            msg_data = await prepare_message_data(msg, db)
                            
                            updates = {
                                "content": msg.content,
                                "edited_timestamp": getattr(msg, "edited_at", datetime.utcnow()),
                                "attachments": msg_data["attachments_list"],
                                "embeds": msg_data["embeds_list"],
                                "reactions": msg_data["emojis_list"],
                            }
                            
                            if msg_data["message_reference"]:
                                updates["message_reference"] = msg_data["message_reference"]
                            if msg_data["referenced_message"]:
                                updates["referenced_message"] = msg_data["referenced_message"]
                            
                            updates_list.append((existing_msg, updates))
                            print(f"Updated message in DB: {msg.id}")
                    else:
                        # Prepare message data
                        msg_data = await prepare_message_data(msg, db)
                        
                        # Build and append new message model
                        new_messages.append(build_message_model(msg, msg_data))
                
                # Batch insert new messages
                if new_messages:
                    await batch_create_messages(db, new_messages)
                    print(f"Batch inserted {len(new_messages)} new messages")
                
                # Batch update existing messages
                if updates_list:
                    await batch_update_messages(db, updates_list)
                    print(f"Batch updated {len(updates_list)} messages")
                
                latest_message_id = messages[-1].id
                print('going to sleep')
                await asyncio.sleep(0.05)

            
            print(f'channel reconciled successfully. Time taken: {format_elapsed_time(start_time)}')
    except Exception as e:
        print(f"Error reconciling channel {channel.id}: {e}")


async def bulk_messages_create(messages_data: list[Message]):
    async with AsyncSessionLocal() as db:
        try:
            batch_size = 100
            total_inserted = 0
            
            for i in range(0, len(messages_data), batch_size):
                batch = messages_data[i:i + batch_size]
                await batch_create_messages(db, batch)
                total_inserted += len(batch)
                print(f"Inserted {total_inserted}/{len(messages_data)} messages")
            
            print(f"Bulk creation completed. Total messages inserted: {total_inserted}")
        except Exception as e:
            print(f"Error in bulk message creation: {e}")