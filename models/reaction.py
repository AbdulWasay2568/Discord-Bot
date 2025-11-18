from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Reaction(Base):
    __tablename__ = "reactions"
    __table_args__ = (
        UniqueConstraint('message_id', 'user_id', 'emoji', name='unique_user_emoji_per_message'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    emoji = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    message = relationship("Message", back_populates="reactions")
    user = relationship("User", back_populates="reactions")
