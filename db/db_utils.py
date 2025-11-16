import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.base import Base
from models.user import User
from models.message import Message
from models.attachment import Attachment
from models.reaction import Reaction

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

# ==================== USER OPERATIONS ====================
def get_or_create_user(db: Session, discord_id: str, username: str, is_bot: bool = False, avatar_url: str = None, discriminator: str = None) -> User:
    """Get existing user or create new one"""
    user = db.query(User).filter(User.discord_id == discord_id).first()
    if not user:
        user = User(
            discord_id=discord_id,
            username=username,
            is_bot=is_bot,
            avatar_url=avatar_url,
            discriminator=discriminator
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# ==================== MESSAGE OPERATIONS ====================
def save_message(db: Session, discord_message_id: int, user_id: int, channel_id: int, guild_id: int, 
                content: str = None, is_bot_message: bool = False) -> Message:
    """Save a message to database"""
    existing = db.query(Message).filter(Message.discord_message_id == discord_message_id).first()
    if existing:
        return existing
    
    message = Message(
        discord_message_id=discord_message_id,
        user_id=user_id,
        channel_id=channel_id,
        guild_id=guild_id,
        content=content,
        is_bot_message=is_bot_message
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_user_messages(db: Session, user_id: int, limit: int = 100) -> list:
    """Get all messages from a specific user"""
    return db.query(Message).filter(Message.user_id == user_id).order_by(Message.created_at.desc()).limit(limit).all()

def get_channel_messages(db: Session, channel_id: int, limit: int = 100) -> list:
    """Get all messages from a specific channel"""
    return db.query(Message).filter(Message.channel_id == channel_id).order_by(Message.created_at.desc()).limit(limit).all()

# ==================== ATTACHMENT OPERATIONS ====================
def save_attachment(db: Session, discord_attachment_id: int, message_id: int, filename: str, 
                   url: str, content_type: str = None, size: int = None, local_path: str = None, 
                   is_downloaded: bool = False) -> Attachment:
    """Save an attachment to database"""
    existing = db.query(Attachment).filter(Attachment.discord_attachment_id == discord_attachment_id).first()
    if existing:
        return existing
    
    attachment = Attachment(
        discord_attachment_id=discord_attachment_id,
        message_id=message_id,
        filename=filename,
        url=url,
        content_type=content_type,
        size=size,
        local_path=local_path,
        is_downloaded=is_downloaded
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment

def get_message_attachments(db: Session, message_id: int) -> list:
    """Get all attachments for a message"""
    return db.query(Attachment).filter(Attachment.message_id == message_id).all()

# ==================== REACTION OPERATIONS ====================
def save_reaction(db: Session, message_id: int, user_id: int, emoji: str) -> Reaction:
    """Save a reaction to database (handles duplicates gracefully)"""
    existing = db.query(Reaction).filter(
        Reaction.message_id == message_id,
        Reaction.user_id == user_id,
        Reaction.emoji == emoji
    ).first()
    
    if existing:
        return existing
    
    reaction = Reaction(
        message_id=message_id,
        user_id=user_id,
        emoji=emoji
    )
    db.add(reaction)
    db.commit()
    db.refresh(reaction)
    return reaction

def get_message_reactions(db: Session, message_id: int) -> list:
    """Get all reactions for a message"""
    return db.query(Reaction).filter(Reaction.message_id == message_id).all()

def remove_reaction(db: Session, message_id: int, user_id: int, emoji: str) -> bool:
    """Remove a reaction from a message"""
    reaction = db.query(Reaction).filter(
        Reaction.message_id == message_id,
        Reaction.user_id == user_id,
        Reaction.emoji == emoji
    ).first()
    
    if reaction:
        db.delete(reaction)
        db.commit()
        return True
    return False

# ==================== GUILD/CHANNEL OPERATIONS ====================
def get_guild_messages(db: Session, guild_id: int, limit: int = 500) -> list:
    """Get all messages from a specific guild"""
    return db.query(Message).filter(Message.guild_id == guild_id).order_by(Message.created_at.desc()).limit(limit).all()

def get_user_guild_messages(db: Session, user_id: int, guild_id: int) -> list:
    """Get all messages from a specific user in a specific guild"""
    return db.query(Message).filter(
        Message.user_id == user_id,
        Message.guild_id == guild_id
    ).order_by(Message.created_at.asc()).all()
