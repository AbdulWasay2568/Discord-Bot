from models.reaction import Reaction
from sqlalchemy.orm import Session

def save_reaction(db: Session, message_id: int, user_id: int, emoji: str) -> Reaction:
    existing = db.query(Reaction).filter(
        Reaction.message_id == message_id,
        Reaction.user_id == user_id,
        Reaction.emoji == emoji
    ).first()
    
    if existing:
        return existing
    
    reaction = Reaction(
        message_id=message_id,
        user_id=user_id,
        emoji=emoji
    )
    db.add(reaction)
    db.commit()
    db.refresh(reaction)
    return reaction

def get_message_reactions(db: Session, message_id: int) -> list:
    return db.query(Reaction).filter(Reaction.message_id == message_id).all()

def remove_reaction(db: Session, message_id: int, user_id: int, emoji: str) -> bool:
    reaction = db.query(Reaction).filter(
        Reaction.message_id == message_id,
        Reaction.user_id == user_id,
        Reaction.emoji == emoji
    ).first()
    
    if reaction:
        db.delete(reaction)
        db.commit()
        return True
    return False
