from sqlalchemy import Column, BigInteger, DateTime, Boolean
from .base import Base
from datetime import datetime

class buffer(Base):
    __tablename__ = "sync_state"

    channel_id = Column(BigInteger, primary_key=True)
    odlest_buffered_timestamp = Column(DateTime, nullable=True)
    last_synced_message_id = Column(BigInteger, nullable=True)
    last_sync_at = Column(DateTime, nullable=True)
    initial_backfill_complete = Column(Boolean, default=False)


