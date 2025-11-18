from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
import enum

class ChannelType(enum.Enum):
    text = "text"
    thread = "thread"

class Channel(Base):
    __tablename__ = "channels"

    id = Column(BigInteger, primary_key=True)  
    guild_id = Column(BigInteger, ForeignKey("guilds.id"), nullable=False)
    name = Column(String(200))
    type = Column(Enum(ChannelType), default=ChannelType.text)
    buffering_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    guild = relationship("Guild", backref="channels")
