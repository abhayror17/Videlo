"""
Media storage utilities for downloading and storing generated media locally.
"""

import os
import aiohttp
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# Media storage directory
MEDIA_DIR = Path(__file__).parent.parent.parent / "media"

def ensure_media_dir():
    """Ensure media directory exists."""
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    # Create subdirectories by date
    today = datetime.utcnow().strftime("%Y-%m-%d")
    (MEDIA_DIR / today).mkdir(parents=True, exist_ok=True)
    return MEDIA_DIR / today

def get_media_path(filename: str) -> Path:
    """Get full path for a media file."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return MEDIA_DIR / today / filename

def get_media_url(filename: str) -> str:
    """Get URL path for serving media file."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return f"/media/{today}/{filename}"

async def download_media(url: str, generation_id: int, generation_type: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Download media from URL and store locally.
    
    Args:
        url: Remote URL to download from
        generation_id: ID of the generation
        generation_type: Type of generation (text2img, txt2video, etc.)
    
    Returns:
        Tuple of (local_path, local_url) or (None, None) on failure
    """
    if not url:
        return None, None
    
    try:
        # Determine file extension
        if '.mp4' in url.lower():
            ext = '.mp4'
        elif '.webm' in url.lower():
            ext = '.webm'
        elif '.png' in url.lower():
            ext = '.png'
        elif '.jpg' in url.lower() or '.jpeg' in url.lower():
            ext = '.jpg'
        elif '.webp' in url.lower():
            ext = '.webp'
        elif '.mp3' in url.lower():
            ext = '.mp3'
        elif '.wav' in url.lower():
            ext = '.wav'
        else:
            # Default based on type
            ext = '.mp4' if 'video' in generation_type else '.png'
        
        # Create filename
        today = datetime.utcnow().strftime("%Y-%m-%d")
        filename = f"{generation_type}_{generation_id}_{datetime.utcnow().strftime('%H%M%S')}{ext}"
        
        # Ensure directory exists
        media_dir = MEDIA_DIR / today
        media_dir.mkdir(parents=True, exist_ok=True)
        
        local_path = media_dir / filename
        
        # Download the file with timeout and retry
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            with open(local_path, 'wb') as f:
                                f.write(await response.read())
                            
                            local_url = f"/media/{today}/{filename}"
                            print(f"[Media] Downloaded: {filename}")
                            return str(local_path), local_url
                        elif response.status == 400:
                            error_body = await response.text()
                            print(f"[Media] HTTP 400 error downloading from {url}: {error_body[:200]}")
                            # 400 usually means the URL is invalid or expired - don't retry
                            return None, None
                        elif response.status == 404:
                            print(f"[Media] HTTP 404 - URL not found: {url[:100]}")
                            return None, None
                        else:
                            last_error = f"HTTP {response.status}"
                            print(f"[Media] Download attempt {attempt + 1} failed: HTTP {response.status}")
            except aiohttp.ClientError as e:
                last_error = str(e)
                print(f"[Media] Download attempt {attempt + 1} failed: {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
        
        print(f"[Media] Failed to download after {max_retries} attempts: {last_error}")
        return None, None
                    
    except Exception as e:
        print(f"[Media] Download error: {e}")
        return None, None

def delete_media(local_path: str) -> bool:
    """
    Delete a local media file.
    
    Args:
        local_path: Path to the local file
    
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        if local_path and os.path.exists(local_path):
            os.remove(local_path)
            print(f"[Media] Deleted: {local_path}")
            return True
    except Exception as e:
        print(f"[Media] Delete error: {e}")
    return False

def cleanup_old_media(days: int = 1) -> int:
    """
    Delete media files older than specified days.
    
    Args:
        days: Number of days to keep
    
    Returns:
        Number of files deleted
    """
    from datetime import timedelta
    
    deleted_count = 0
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    try:
        if not MEDIA_DIR.exists():
            return 0
        
        for date_dir in MEDIA_DIR.iterdir():
            if date_dir.is_dir():
                try:
                    dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                    if dir_date < cutoff:
                        # Delete all files in this directory
                        for file in date_dir.iterdir():
                            if file.is_file():
                                file.unlink()
                                deleted_count += 1
                        # Remove the directory
                        date_dir.rmdir()
                        print(f"[Media] Cleaned up directory: {date_dir.name}")
                except ValueError:
                    # Directory name is not a date, skip
                    pass
    except Exception as e:
        print(f"[Media] Cleanup error: {e}")
    
    return deleted_count
