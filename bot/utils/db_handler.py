"""
Database handler for Discord events - saves messages, attachments, and reactions
"""
import sys
from pathlib import Path
import discord

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from db.db_utils import (
    SessionLocal, get_or_create_user, save_message, 
    save_attachment, save_reaction, remove_reaction
)
from models.message import Message
from models.user import User
from bot.utils.file_manager import download_attachment

async def handle_message_save(message: discord.Message):
    """Save a message and its attachments to database"""
    if not message.author:
        return
    
    db = SessionLocal()
    try:
        user = get_or_create_user(
            db,
            discord_id=str(message.author.id),
            username=message.author.name,
            is_bot=message.author.bot,
            avatar_url=str(message.author.avatar.url) if message.author.avatar else None,
            discriminator=message.author.discriminator
        )
        
        saved_message = save_message(
            db,
            discord_message_id=message.id,
            user_id=user.id,
            channel_id=message.channel.id,
            guild_id=message.guild.id if message.guild else 0,
            content=message.content,
            is_bot_message=message.author.bot
        )
        
        for attachment in message.attachments:
            local_path, success = await download_attachment(
                attachment.url,
                attachment.filename,
                saved_message.id
            )
            
            save_attachment(
                db,
                discord_attachment_id=attachment.id,
                message_id=saved_message.id,
                filename=attachment.filename,
                url=attachment.url,
                content_type=attachment.content_type,
                size=attachment.size,
                local_path=local_path if success else None,
                is_downloaded=success
            )
    
    except Exception as e:
        print(f"Error saving message to database: {e}")
    
    finally:
        db.close()

async def handle_reaction_add(reaction: discord.Reaction, user: discord.User):
    """Save a reaction to database"""
    if user.bot:
        return
    
    db = SessionLocal()
    try:
        db_user = get_or_create_user(
            db,
            discord_id=str(user.id),
            username=user.name,
            is_bot=user.bot,
            avatar_url=str(user.avatar.url) if user.avatar else None,
            discriminator=user.discriminator
        )
        
        from models.message import Message
        db_message = db.query(Message).filter(
            Message.discord_message_id == reaction.message.id
        ).first()
        
        if db_message:
            save_reaction(
                db,
                message_id=db_message.id,
                user_id=db_user.id,
                emoji=str(reaction.emoji)
            )
    
    except Exception as e:
        print(f"Error saving reaction to database: {e}")
    
    finally:
        db.close()

async def handle_reaction_remove(reaction: discord.Reaction, user: discord.User):
    """Remove a reaction from database"""
    if user.bot:
        return
    
    db = SessionLocal()
    try:
        from models.user import User
        db_user = db.query(User).filter(User.discord_id == str(user.id)).first()
        
        if db_user:
            from models.message import Message
            db_message = db.query(Message).filter(
                Message.discord_message_id == reaction.message.id
            ).first()
            
            if db_message:
                remove_reaction(
                    db,
                    message_id=db_message.id,
                    user_id=db_user.id,
                    emoji=str(reaction.emoji)
                )
    
    except Exception as e:
        print(f"Error removing reaction from database: {e}")
    
    finally:
        db.close()
