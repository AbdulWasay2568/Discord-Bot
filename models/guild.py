from sqlalchemy import Column, BigInteger, String, Boolean, DateTime
from datetime import datetime
from .base import Base

class Guild(Base):
    __tablename__ = "guilds"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(200), nullable=True)
    buffering_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
