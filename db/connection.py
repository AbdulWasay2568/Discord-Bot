from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
from bot.config.settings import DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment")

# Convert common postgres sync URL to an asyncpg URL if needed
db_url = DATABASE_URL
if db_url.startswith("postgresql://") and "+" not in db_url.split("://", 1)[1]:
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql+psycopg2://"):
    db_url = db_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)

try:
    engine = create_async_engine(db_url, echo=False)
except ModuleNotFoundError as e:
    if 'asyncpg' in str(e):
        raise RuntimeError("The async DB driver 'asyncpg' is required for SQLAlchemy asyncio. Install it in your venv: pip install asyncpg") from e
    raise
except InvalidRequestError as e:
    raise RuntimeError("Invalid DB driver loaded. Ensure DATABASE_URL uses an async driver like 'postgresql+asyncpg://...' and that 'asyncpg' is installed.") from e

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
