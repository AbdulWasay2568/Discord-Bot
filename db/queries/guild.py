from models.guild import Guild
from sqlalchemy.orm import Session
from typing import List, Optional


def get_guild(db: Session, guild_id: int) -> Optional[Guild]:
	return db.query(Guild).filter(Guild.id == guild_id).first()


def create_or_update_guild(db: Session, guild_id: int, name: str = None, buffering_enabled: bool = True) -> Guild:
	g = get_guild(db, guild_id)
	if g:
		if name is not None:
			g.name = name
		g.buffering_enabled = buffering_enabled
		db.commit()
		db.refresh(g)
		return g

	g = Guild(id=guild_id, name=name, buffering_enabled=buffering_enabled)
	db.add(g)
	db.commit()
	db.refresh(g)
	return g


def list_guilds(db: Session) -> List[Guild]:
	return db.query(Guild).all()


def delete_guild(db: Session, guild_id: int) -> bool:
	g = get_guild(db, guild_id)
	if g:
		db.delete(g)
		db.commit()
		return True
	return False

