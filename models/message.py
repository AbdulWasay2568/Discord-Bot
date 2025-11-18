from sqlalchemy import Column, Integer, BigInteger, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_message_id = Column(BigInteger, unique=True, nullable=False)
    channel_id = Column(BigInteger, ForeignKey("channels.id"), nullable=False)
    guild_id = Column(BigInteger, ForeignKey("guilds.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    content = Column(Text, nullable=True)
    is_bot_message = Column(Boolean, default=False)
    is_pinned = Column(Boolean, default=False)
    has_embeds = Column(Boolean, default=False)
    has_attachments = Column(Boolean, default=False)
    reaction_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.now)
    edited_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="messages")
    attachments = relationship("Attachment", back_populates="message", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="message", cascade="all, delete-orphan")
