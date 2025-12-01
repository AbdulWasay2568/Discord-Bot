from models.models import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from typing import Dict, Any

async def get_message(db:AsyncSession, message_id:int)->Message|None:
    result = await db.execute(select(Message).filter(Message.id == message_id))
    return result.scalar_one_or_none()

async def create_message(db:AsyncSession, message:Message)->Message:
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message

async def update_message(db: AsyncSession, message_id: int, author_id: int, updates: Dict[str, Any]) -> Message | None:
    result = await db.execute(
        select(Message).filter(Message.id == message_id, Message.author_id == author_id)
    )
    message = result.scalar_one_or_none()

    if not message:
        return None

    for key, value in updates.items():
        if hasattr(message, key):
            setattr(message, key, value)

    if "content" in updates:
        message.edited_timestamp = datetime.now()

    await db.commit()
    await db.refresh(message)
    return message

async def delete_message(db: AsyncSession, message_id: int, author_id: int) -> bool:
    result = await db.execute(
        select(Message).filter(Message.id == message_id, Message.author_id == author_id)
    )
    message = result.scalar_one_or_none()

    if not message:
        return False

    await db.delete(message)
    await db.commit()
    return True
