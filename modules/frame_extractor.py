"""
Frame Extraction Module
Extracts video frames at specific timestamps using ffmpeg
"""

import subprocess
from pathlib import Path
from typing import List, Dict, Optional


def timestamp_to_seconds(timestamp: str) -> float:
    """
    Convert MM:SS or HH:MM:SS timestamp to seconds.

    Args:
        timestamp: Time string in MM:SS or HH:MM:SS format

    Returns:
        Time in seconds

    Raises:
        ValueError: If timestamp format is invalid
    """
    parts = timestamp.split(':')

    try:
        if len(parts) == 2:  # MM:SS
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        else:
            raise ValueError(f"Invalid timestamp format: {timestamp}")
    except ValueError:
        raise ValueError(f"Invalid timestamp format: {timestamp}")


def extract_frame_at_timestamp(
    video_path: str,
    timestamp: str,
    output_path: Path,
    quality: int = 85
) -> Path:
    """
    Extract a single frame at a specific timestamp.

    Args:
        video_path: Path to video file
        timestamp: Timestamp in MM:SS or HH:MM:SS format
        output_path: Path for output image
        quality: JPEG quality (1-100)

    Returns:
        Path to extracted frame

    Raises:
        Exception: If frame extraction fails
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert timestamp to seconds
    seconds = timestamp_to_seconds(timestamp)

    try:
        cmd = [
            'ffmpeg',
            '-ss', str(seconds),  # Seek to timestamp
            '-i', str(video_path),
            '-vframes', '1',  # Extract one frame
            '-q:v', str(int((100 - quality) / 10)),  # Quality (lower is better for ffmpeg)
            '-y',  # Overwrite
            str(output_path)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        return output_path

    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to extract frame at {timestamp}: {e.stderr}")
    except FileNotFoundError:
        raise Exception("ffmpeg not found. Please install ffmpeg and add it to PATH.")


def extract_frames(
    video_path: str,
    key_moments: List[Dict[str, str]],
    frames_dir: Path = Path("cache/frames"),
    quality: int = 85,
    name_prefix: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Extract frames at specified key moments.

    Args:
        video_path: Path to video file
        key_moments: List of dicts with 'timestamp' and 'description' keys
        frames_dir: Directory to save frames
        quality: JPEG quality (1-100)
        name_prefix: Prefix for frame filenames (defaults to video name)

    Returns:
        List of dicts with frame info:
            - timestamp: Original timestamp
            - description: Frame description
            - caption: Frame caption
            - frame_path: Path to extracted frame file

    Raises:
        Exception: If frame extraction fails
    """
    frames_dir = Path(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    video_path = Path(video_path)
    if name_prefix is None:
        name_prefix = video_path.stem

    print(f"🖼️  Extracting {len(key_moments)} frames...")

    extracted_frames = []

    for i, moment in enumerate(key_moments, 1):
        timestamp = moment.get('timestamp', '')
        description = moment.get('description', '')
        caption = moment.get('caption', description)

        # Generate frame filename
        timestamp_safe = timestamp.replace(':', '-')
        frame_filename = f"{name_prefix}_frame_{i:02d}_{timestamp_safe}.jpg"
        frame_path = frames_dir / frame_filename

        try:
            # Extract frame
            extract_frame_at_timestamp(
                str(video_path),
                timestamp,
                frame_path,
                quality
            )

            extracted_frames.append({
                'timestamp': timestamp,
                'description': description,
                'caption': caption,
                'frame_path': str(frame_path),
                'frame_number': i
            })

            print(f"  ✓ Frame {i}/{len(key_moments)}: {timestamp} - {description[:50]}...")

        except Exception as e:
            print(f"  ✗ Failed to extract frame at {timestamp}: {e}")
            continue

    print(f"✓ Extracted {len(extracted_frames)}/{len(key_moments)} frames")

    return extracted_frames


def extract_frames_smart(
    video_path: str,
    duration: float,
    num_frames: int = 10,
    frames_dir: Path = Path("cache/frames"),
    quality: int = 85,
    name_prefix: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Extract frames at evenly spaced intervals (smart extraction).

    Args:
        video_path: Path to video file
        duration: Video duration in seconds
        num_frames: Number of frames to extract
        frames_dir: Directory to save frames
        quality: JPEG quality (1-100)
        name_prefix: Prefix for frame filenames

    Returns:
        List of dicts with frame info

    Raises:
        Exception: If frame extraction fails
    """
    frames_dir = Path(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    video_path = Path(video_path)
    if name_prefix is None:
        name_prefix = video_path.stem

    print(f"🖼️  Extracting {num_frames} evenly-spaced frames...")

    # Calculate evenly spaced timestamps
    interval = duration / (num_frames + 1)
    timestamps = [interval * (i + 1) for i in range(num_frames)]

    extracted_frames = []

    for i, seconds in enumerate(timestamps, 1):
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        timestamp = f"{minutes:02d}:{secs:02d}"

        frame_filename = f"{name_prefix}_frame_{i:02d}_{timestamp.replace(':', '-')}.jpg"
        frame_path = frames_dir / frame_filename

        try:
            # Extract frame
            extract_frame_at_timestamp(
                str(video_path),
                timestamp,
                frame_path,
                quality
            )

            extracted_frames.append({
                'timestamp': timestamp,
                'description': f'Frame at {timestamp}',
                'caption': f'Screenshot at {timestamp}',
                'frame_path': str(frame_path),
                'frame_number': i
            })

            print(f"  ✓ Frame {i}/{num_frames}: {timestamp}")

        except Exception as e:
            print(f"  ✗ Failed to extract frame at {timestamp}: {e}")
            continue

    print(f"✓ Extracted {len(extracted_frames)}/{num_frames} frames")

    return extracted_frames


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) < 2:
        print("Usage: python frame_extractor.py <video_path> [duration] [num_frames]")
        sys.exit(1)

    test_video = sys.argv[1]
    test_duration = float(sys.argv[2]) if len(sys.argv) > 2 else 300.0
    test_num_frames = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    try:
        # Test smart extraction
        frames = extract_frames_smart(
            test_video,
            duration=test_duration,
            num_frames=test_num_frames
        )

        print(f"\n{'='*60}")
        print("Frame Extraction Results:")
        print(f"{'='*60}")
        for frame in frames:
            print(f"  {frame['frame_number']}. [{frame['timestamp']}] {frame['frame_path']}")
        print(f"{'='*60}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
