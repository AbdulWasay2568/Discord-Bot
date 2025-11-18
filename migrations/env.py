import os
from dotenv import load_dotenv
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from models import Base  # your SQLAlchemy Base
from bot.config.settings import DATABASE_URL

# Alembic config object
config = context.config
fileConfig(config.config_file_name)

# Set target metadata for autogenerate
target_metadata = Base.metadata

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL not found in .env")
config.set_main_option("sqlalchemy.url", DATABASE_URL)
