"""
Video Download Module
Downloads YouTube videos using yt-dlp with caching support, or uses local video files
"""

import json
import re
import shutil
from pathlib import Path
from typing import Dict, Optional
import yt_dlp


def is_url(input_string: str) -> bool:
    """
    Determine if input is a YouTube URL or a local file path.

    Args:
        input_string: Either a YouTube URL or file path

    Returns:
        True if input is a URL, False if it's a file path
    """
    return input_string.startswith(('http://', 'https://', 'www.'))


def extract_video_id(url: str) -> str:
    """
    Extract YouTube video ID from URL.

    Args:
        url: YouTube video URL

    Returns:
        Video ID string

    Raises:
        ValueError: If URL format is invalid
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
        r'youtube\.com\/v\/([^&\n?#]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract video ID from URL: {url}")


def load_local_video(
    file_path: str,
    cache_dir: Path = Path("cache/videos")
) -> Dict[str, any]:
    """
    Load a local video file and create metadata.

    Args:
        file_path: Path to local MP4 video file
        cache_dir: Directory to cache video copy and metadata

    Returns:
        Dictionary containing:
            - video_path: Path to video file
            - video_id: Generated ID from filename
            - title: Filename without extension
            - duration: Duration in seconds (0 if can't be determined)
            - description: Empty string
            - upload_date: Empty string
            - uploader: "Local File"
            - view_count: 0
            - thumbnail: Empty string
            - url: Local file path

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Video file not found: {file_path}")

    if not file_path.suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']:
        raise ValueError(f"Unsupported video format: {file_path.suffix}")

    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Generate video ID from filename (remove extension and special chars)
    video_id = file_path.stem.lower().replace(' ', '_').replace('-', '_')

    # Copy video to cache
    cached_video = cache_dir / f"{video_id}.mp4"
    cached_metadata = cache_dir / f"{video_id}.json"

    # Copy file to cache if not already there
    if not cached_video.exists():
        print(f"📋 Loading local video: {file_path.name}")
        shutil.copy2(file_path, cached_video)
        print(f"✓ Video copied to cache: {cached_video}")
    else:
        print(f"✓ Using cached local video: {video_id}")

    # Prepare metadata
    metadata = {
        'video_path': str(cached_video),
        'video_id': video_id,
        'title': file_path.stem,
        'duration': 0,  # Local files don't have duration info without additional processing
        'description': '',
        'upload_date': '',
        'uploader': 'Local File',
        'view_count': 0,
        'thumbnail': '',
        'url': str(file_path),
        'is_local': True
    }

    # Save metadata
    with open(cached_metadata, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✓ Loaded: {metadata['title']}")

    return metadata


def download_video(
    url: str,
    cache_dir: Path = Path("cache/videos"),
    skip_cache: bool = False
) -> Dict[str, any]:
    """
    Download YouTube video using yt-dlp with caching, or load local video file.

    Args:
        url: YouTube video URL or local file path
        cache_dir: Directory to cache downloaded videos
        skip_cache: If True, force re-download even if cached

    Returns:
        Dictionary containing:
            - video_path: Path to downloaded video file
            - video_id: YouTube video ID or local file ID
            - title: Video title
            - duration: Duration in seconds
            - description: Video description
            - upload_date: Upload date (YYYYMMDD format)
            - uploader: Channel name
            - is_local: Boolean indicating if this is a local file

    Raises:
        Exception: If download fails or file not found
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Check if input is a URL or local file
    if not is_url(url):
        return load_local_video(url, cache_dir)

    # Extract video ID
    video_id = extract_video_id(url)

    # Check cache
    cached_video = cache_dir / f"{video_id}.mp4"
    cached_metadata = cache_dir / f"{video_id}.json"

    if not skip_cache and cached_video.exists() and cached_metadata.exists():
        print(f"✓ Using cached video: {video_id}")
        with open(cached_metadata, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        return metadata

    print(f"⬇ Downloading video: {video_id}")

    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': str(cache_dir / f'{video_id}.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info and download
            info = ydl.extract_info(url, download=True)

            # Prepare metadata
            metadata = {
                'video_path': str(cached_video),
                'video_id': video_id,
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'description': info.get('description', ''),
                'upload_date': info.get('upload_date', ''),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'thumbnail': info.get('thumbnail', ''),
                'url': url,
                'is_local': False
            }

            # Save metadata
            with open(cached_metadata, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            print(f"✓ Downloaded: {metadata['title']}")
            print(f"  Duration: {metadata['duration']} seconds")

            return metadata

    except Exception as e:
        raise Exception(f"Failed to download video: {str(e)}")


def get_cached_metadata(video_id: str, cache_dir: Path = Path("cache/videos")) -> Optional[Dict]:
    """
    Retrieve cached metadata for a video.

    Args:
        video_id: YouTube video ID
        cache_dir: Cache directory path

    Returns:
        Metadata dictionary if cached, None otherwise
    """
    cache_dir = Path(cache_dir)
    metadata_file = cache_dir / f"{video_id}.json"

    if metadata_file.exists():
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    return None


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) < 2:
        print("Usage: python video_download.py <youtube_url>")
        sys.exit(1)

    test_url = sys.argv[1]

    try:
        result = download_video(test_url)
        print(f"\n{'='*60}")
        print("Download Results:")
        print(f"{'='*60}")
        print(f"Title: {result['title']}")
        print(f"Video ID: {result['video_id']}")
        print(f"Duration: {result['duration']} seconds")
        print(f"Path: {result['video_path']}")
        print(f"{'='*60}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
