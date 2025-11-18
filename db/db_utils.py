import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.base import Base
from models.user import User
from models.message import Message
from models.attachment import Attachment
from models.reaction import Reaction

from db.connection import engine, SessionLocal


def create_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)


# Re-export commonly used DB helpers from the queries package so callers
# can import them from `db.db_utils` (keeps older import paths working).
from db.queries.user import get_or_create_user
from db.queries.messages import save_message
from db.queries.attachments import save_attachment
from db.queries.reactions import save_reaction, remove_reaction
from db.queries.attachments import get_message_attachments

__all__ = [
    "engine",
    "SessionLocal",
    "create_db",
    "get_or_create_user",
    "save_message",
    "save_attachment",
    "save_reaction",
    "remove_reaction",
    "get_message_attachments",
]

