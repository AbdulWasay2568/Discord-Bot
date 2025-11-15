from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_message_id = Column(BigInteger, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel_id = Column(BigInteger, nullable=False)
    guild_id = Column(BigInteger, nullable=False)
    content = Column(Text, nullable=True)
    is_bot_message = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="messages")
    attachments = relationship("Attachment", back_populates="message", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="message", cascade="all, delete-orphan")
