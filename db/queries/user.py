from models.user import User
from sqlalchemy.orm import Session

def get_or_create_user(db: Session, discord_id: str, username: str, is_bot: bool = False, avatar_url: str = None, discriminator: str = None) -> User:
    user = db.query(User).filter(User.discord_id == discord_id).first()
    if not user:
        user = User(
            discord_id=discord_id,
            username=username,
            is_bot=is_bot,
            avatar_url=avatar_url,
            discriminator=discriminator
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
