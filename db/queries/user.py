from models.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# upsert a user
async def upsert_user(db: AsyncSession, user: User) -> User:
    result = await db.execute(select(User).filter(User.id == user.id))
    existing = result.scalar_one_or_none()

    if existing:
        existing.username = user.username
        existing.avatar = user.avatar
        existing.global_name = user.global_name
        existing.bot = user.bot
        existing.system = user.system
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

# Get user by ID
async def get_user(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()

# Delete user by ID
async def delete_user(db: AsyncSession, user_id: int) -> None:
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        await db.delete(user)
        await db.commit()


# GET /guilds/{guild_id}/members – List all members in a guild.
