from models.attachment import Attachment
from sqlalchemy.orm import Session

def save_attachment(db: Session, discord_attachment_id: int, message_id: int, filename: str, 
                   url: str, content_type: str = None, size: int = None, local_path: str = None, 
                   is_downloaded: bool = False) -> Attachment:
    existing = db.query(Attachment).filter(Attachment.discord_attachment_id == discord_attachment_id).first()
    if existing:
        return existing
    
    attachment = Attachment(
        discord_attachment_id=discord_attachment_id,
        message_id=message_id,
        filename=filename,
        url=url,
        content_type=content_type,
        size=size,
        local_path=local_path,
        is_downloaded=is_downloaded
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment

def get_message_attachments(db: Session, message_id: int) -> list:
    return db.query(Attachment).filter(Attachment.message_id == message_id).all()
