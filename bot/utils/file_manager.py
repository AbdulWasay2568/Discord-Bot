import aiohttp
import os
from pathlib import Path
from datetime import datetime

ATTACHMENTS_DIR = Path(__file__).parent.parent / "attachments"
ATTACHMENTS_DIR.mkdir(exist_ok=True)

async def download_attachment(url: str, filename: str, message_id: int) -> tuple[str, bool]:
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
    msg_dir = ATTACHMENTS_DIR / f"msg_{message_id}"
    safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    return msg_dir / safe_filename

def get_attachment_size(local_path: str) -> int:
    """Get the size of a locally stored file"""
    try:
        return os.path.getsize(local_path)
    except:
        return 0
