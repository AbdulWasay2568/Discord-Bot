from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_attachment_id = Column(BigInteger, unique=True, nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    url = Column(String(1000), nullable=False)
    content_type = Column(String(255))
    size = Column(BigInteger)
    local_path = Column(String(500), nullable=True)  
    is_downloaded = Column(Boolean, default=False)  
    created_at = Column(DateTime, default=datetime.now)

    message = relationship("Message", back_populates="attachments")
