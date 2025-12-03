from db.schema import Message
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

async def batch_create_messages(db: AsyncSession, messages: list[Message]) -> list[Message]:
    db.add_all(messages)
    await db.commit()
    return messages

async def batch_update_messages(db: AsyncSession, message_updates: list[tuple[Message, Dict[str, Any]]]) -> list[Message]:
    updated_messages = []
    for message, updates in message_updates:
        for key, value in updates.items():
            if hasattr(message, key):
                setattr(message, key, value)
        
        if "content" in updates:
            message.edited_timestamp = datetime.now()
        
        updated_messages.append(message)
    
    await db.commit()
    return updated_messages

async def get_messages_batch(db: AsyncSession, message_ids: list[int]) -> Dict[int, Message]:
    result = await db.execute(
        select(Message).filter(Message.id.in_(message_ids))
    )
    messages = result.scalars().all()
    return {msg.id: msg for msg in messages}

