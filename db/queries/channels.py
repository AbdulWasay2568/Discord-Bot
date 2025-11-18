from models.channel import Channel
from sqlalchemy.orm import Session
from typing import List, Optional


def get_channel(db: Session, channel_id: int) -> Optional[Channel]:
	return db.query(Channel).filter(Channel.id == channel_id).first()


def create_or_update_channel(db: Session, channel_id: int, guild_id: int, name: str = None,
							 type: Optional[str] = None, buffering_enabled: bool = True) -> Channel:

	channel = get_channel(db, channel_id)
	if channel:
		if name is not None:
			channel.name = name
		if type is not None:
			channel.type = type
		channel.buffering_enabled = buffering_enabled
		db.commit()
		db.refresh(channel)
		return channel

	channel = Channel(
		id=channel_id,
		guild_id=guild_id,
		name=name,
		type=type,
		buffering_enabled=buffering_enabled,
	)
	db.add(channel)
	db.commit()
	db.refresh(channel)
	return channel


def list_guild_channels(db: Session, guild_id: int) -> List[Channel]:
	return db.query(Channel).filter(Channel.guild_id == guild_id).all()


def delete_channel(db: Session, channel_id: int) -> bool:
	channel = get_channel(db, channel_id)
	if channel:
		db.delete(channel)
		db.commit()
		return True
	return False

