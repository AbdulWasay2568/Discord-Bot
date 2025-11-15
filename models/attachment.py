from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_attachment_id = Column(BigInteger, unique=True, nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    content_type = Column(String(50))
    size = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)

    message = relationship("Message", back_populates="attachments")
