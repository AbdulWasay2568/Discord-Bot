"""Compatibility utilities for synchronous DB access used by legacy commands.

Provides a synchronous `SessionLocal` and helper functions like
`get_message_attachments` so older parts of the code (e.g. backup commands)
can continue to use the sync SQLAlchemy API while other modules use the
async engine.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.config.settings import DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment")

# If the project-wide DATABASE_URL is set to an async driver (e.g.
# "postgresql+asyncpg://..."), convert it to a sync URL so the legacy
# synchronous Session can connect via psycopg2 (postgresql://...).
sync_db_url = DATABASE_URL
if "+asyncpg" in sync_db_url:
    sync_db_url = sync_db_url.replace("+asyncpg", "")
if sync_db_url.startswith("postgresql+psycopg2://"):
    sync_db_url = sync_db_url.replace("postgresql+psycopg2://", "postgresql://", 1)

engine = create_engine(sync_db_url, echo=False)
SessionLocal = sessionmaker(bind=engine)


def get_message_attachments(db_session, message_id):
    """Return attachments for a message as stored in the Message.attachments JSON column.

    Parameters
    - db_session: a SQLAlchemy sync Session (from `SessionLocal()`)
    - message_id: integer message id

    Returns: list of attachment dicts (may be empty)
    """
    try:
        from models.models import Message
    except Exception:
        return []

    message = db_session.query(Message).filter(Message.id == message_id).first()
    if not message:
        return []
    return message.attachments or []
