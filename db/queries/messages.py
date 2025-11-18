from models.message import Message
from sqlalchemy.orm import Session

def save_message(db: Session, discord_message_id: int, user_id: int, channel_id: int, guild_id: int, 
                content: str = None, is_bot_message: bool = False) -> Message:
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
    return db.query(Message).filter(Message.user_id == user_id).order_by(Message.created_at.desc()).limit(limit).all()

def get_channel_messages(db: Session, channel_id: int, limit: int = 100) -> list:
    return db.query(Message).filter(Message.channel_id == channel_id).order_by(Message.created_at.desc()).limit(limit).all()

def get_guild_messages(db: Session, guild_id: int, limit: int = 500) -> list:
    return db.query(Message).filter(Message.guild_id == guild_id).order_by(Message.created_at.desc()).limit(limit).all()

def get_user_guild_messages(db: Session, user_id: int, guild_id: int) -> list:
    return db.query(Message).filter(
        Message.user_id == user_id,
        Message.guild_id == guild_id
    ).order_by(Message.created_at.asc()).all()
