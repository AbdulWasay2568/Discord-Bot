from models.models import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from typing import Dict, Any

# D. Messages

# Core endpoints for message buffering.

# GET /messages/{message_id} – Fetch a single message.
async def get_message(db:AsyncSession, message_id:int)->Message|None:
    result = await db.execute(select(Message).filter(Message.id == message_id))
    return result.scalar_one_or_none()

# POST /messages – Insert a new message
async def create_message(db:AsyncSession, message:Message)->Message:
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message

# update message

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

#  delete a message
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

# GET /channels/{channel_id}/messages – List messages in a channel with filters:
# date range, author, reactions, text search, attachments, pagination, sorting.

# POST /messages/bulk-delete – Mark multiple messages as deleted (for bulk deletion events).
# POST /messages/bulk – Insert multiple messages (for backfill/reconciliation).



# F. Embeds

# Endpoints for message embeds.

# POST /messages/{message_id}/embeds – Insert or update embeds.

# GET /messages/{message_id}/embeds – Fetch message embeds.



# I. /list Command / Search

# Endpoints to power the search command (can be paginated + filtered).

# POST /search/messages – Search messages with filters:

# channels, members, reactions, date range, text, attachments, filename.

# sorting: created_desc, created_asc, reactions_desc.

# pagination: limit, offset.

# GET /search/filters – Fetch available filters for UI buttons.

