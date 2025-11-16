"""
File manager - Download and store Discord attachments locally
Prevents attachment URLs from expiring
"""
import aiohttp
import os
from pathlib import Path
from datetime import datetime

# Create attachments directory if it doesn't exist
ATTACHMENTS_DIR = Path(__file__).parent.parent / "attachments"
ATTACHMENTS_DIR.mkdir(exist_ok=True)

async def download_attachment(url: str, filename: str, message_id: int) -> tuple[str, bool]:
    """
    Download a Discord attachment and store it locally
    
    Args:
        url: Discord attachment URL
        filename: Original filename
        message_id: Discord message ID (for organizing files)
    
    Returns:
        tuple: (local_path, success_bool)
    """
    try:
        # Create message-specific directory
        msg_dir = ATTACHMENTS_DIR / f"msg_{message_id}"
        msg_dir.mkdir(exist_ok=True)
        
        # Create safe filename
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        if not safe_filename:
            safe_filename = f"attachment_{datetime.now().timestamp()}"
        
        local_path = msg_dir / safe_filename
        
        # Download file
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    with open(local_path, 'wb') as f:
                        f.write(await response.read())
                    
                    print(f"✓ Downloaded: {filename} -> {local_path}")
                    return str(local_path), True
                else:
                    print(f"✗ Failed to download {filename}: HTTP {response.status}")
                    return "", False
    
    except Exception as e:
        print(f"✗ Error downloading {filename}: {str(e)}")
        return "", False

def get_attachment_path(message_id: int, filename: str) -> Path:
    """Get the local path for an attachment"""
    msg_dir = ATTACHMENTS_DIR / f"msg_{message_id}"
    safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    return msg_dir / safe_filename

def get_attachment_size(local_path: str) -> int:
    """Get the size of a locally stored file"""
    try:
        return os.path.getsize(local_path)
    except:
        return 0

def cleanup_old_attachments(days: int = 30) -> int:
    """
    Remove attachments older than specified days
    
    Args:
        days: Number of days to keep attachments
    
    Returns:
        Number of files deleted
    """
    if not ATTACHMENTS_DIR.exists():
        return 0
    
    deleted_count = 0
    cutoff_time = datetime.now().timestamp() - (days * 86400)
    
    for file_path in ATTACHMENTS_DIR.rglob("*"):
        if file_path.is_file():
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except:
                    pass
    
    return deleted_count
