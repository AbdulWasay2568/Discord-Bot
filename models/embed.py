from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Embed(Base):
    __tablename__ = "embeds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    index = Column(Integer, default=0)

    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String(1000), nullable=True)
    type = Column(String(50), default="rich")
    color = Column(Integer, nullable=True)  
    raw_data = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    message = relationship("Message", backref="embeds")
