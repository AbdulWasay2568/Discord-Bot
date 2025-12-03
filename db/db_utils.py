from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.config.settings import DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment")
sync_db_url = DATABASE_URL
if "+asyncpg" in sync_db_url:
    sync_db_url = sync_db_url.replace("+asyncpg", "")
if sync_db_url.startswith("postgresql+psycopg2://"):
    sync_db_url = sync_db_url.replace("postgresql+psycopg2://", "postgresql://", 1)

engine = create_engine(sync_db_url, echo=False)
SessionLocal = sessionmaker(bind=engine)


def get_message_attachments(db_session, message_id):
    try:
        from db.schema import Message
    except Exception:
        return []

    message = db_session.query(Message).filter(Message.id == message_id).first()
    if not message:
        return []
    return message.attachments or []
