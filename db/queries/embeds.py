from models.embed import Embed
from sqlalchemy.orm import Session
from typing import List, Optional


def save_embed(db: Session, message_id: int, index: int = 0, title: str = None,
			   description: str = None, url: str = None, type: str = "rich",
			   color: int = None, raw_data: dict = None) -> Embed:
	embed = Embed(
		message_id=message_id,
		index=index,
		title=title,
		description=description,
		url=url,
		type=type,
		color=color,
		raw_data=raw_data,
	)
	db.add(embed)
	db.commit()
	db.refresh(embed)
	return embed


def get_embed(db: Session, embed_id: int) -> Optional[Embed]:
	return db.query(Embed).filter(Embed.id == embed_id).first()


def get_embeds_for_message(db: Session, message_id: int) -> List[Embed]:
	return db.query(Embed).filter(Embed.message_id == message_id).order_by(Embed.index).all()


def update_embed(db: Session, embed_id: int, **fields) -> Optional[Embed]:
	embed = get_embed(db, embed_id)
	if not embed:
		return None
	for k, v in fields.items():
		if hasattr(embed, k):
			setattr(embed, k, v)
	db.commit()
	db.refresh(embed)
	return embed


def delete_embed(db: Session, embed_id: int) -> bool:
	embed = get_embed(db, embed_id)
	if embed:
		db.delete(embed)
		db.commit()
		return True
	return False

