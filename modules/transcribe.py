"""
Transcription Module
Transcribes video audio using OpenAI Whisper with timestamp support
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import whisper


def extract_audio(
    video_path: str,
    audio_dir: Path = Path("cache/audio"),
    audio_format: str = "wav"
) -> Path:
    """
    Extract audio from video file using ffmpeg.

    Args:
        video_path: Path to video file
        audio_dir: Directory to save extracted audio
        audio_format: Audio format (wav, mp3, etc.)

    Returns:
        Path to extracted audio file

    Raises:
        Exception: If audio extraction fails
    """
    audio_dir = Path(audio_dir)
    audio_dir.mkdir(parents=True, exist_ok=True)

    video_path = Path(video_path)
    audio_path = audio_dir / f"{video_path.stem}.{audio_format}"

    if audio_path.exists():
        print(f"[OK] Using cached audio: {audio_path.name}")
        return audio_path

    print(f"Extracting audio from video...")

    try:
        # Use ffmpeg to extract audio
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # Audio codec
            '-ar', '16000',  # Sample rate (Whisper works well with 16kHz)
            '-ac', '1',  # Mono
            '-y',  # Overwrite output file
            str(audio_path)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        print(f"[OK] Audio extracted: {audio_path.name}")
        return audio_path

    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to extract audio: {e.stderr}")
    except FileNotFoundError:
        raise Exception("ffmpeg not found. Please install ffmpeg and add it to PATH.")


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to MM:SS format.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string (MM:SS)
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def transcribe_video(
    video_path: str,
    model_size: str = "medium",
    language: str = "en",
    transcript_dir: Path = Path("cache/transcripts"),
    skip_cache: bool = False
) -> Dict[str, any]:
    """
    Transcribe video audio using OpenAI Whisper.

    Args:
        video_path: Path to video file
        model_size: Whisper model size (tiny, base, small, medium, large)
        language: Language code (en, es, fr, etc.)
        transcript_dir: Directory to cache transcripts
        skip_cache: If True, force re-transcription

    Returns:
        Dictionary containing:
            - text: Full transcript text
            - segments: List of segments with timestamps
            - language: Detected/specified language
            - duration: Total duration in seconds

    Raises:
        Exception: If transcription fails
    """
    transcript_dir = Path(transcript_dir)
    transcript_dir.mkdir(parents=True, exist_ok=True)

    video_path = Path(video_path)
    video_id = video_path.stem
    transcript_file = transcript_dir / f"{video_id}.json"

    # Check cache
    if not skip_cache and transcript_file.exists():
        print(f"[OK] Using cached transcript: {video_id}")
        with open(transcript_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    print(f"Transcribing video with Whisper ({model_size} model)...")

    try:
        # Extract audio
        audio_path = extract_audio(video_path)

        # Load Whisper model
        print(f"Loading Whisper model: {model_size}")
        model = whisper.load_model(model_size)

        # Transcribe
        print(f"Transcribing (this may take a few minutes)...")
        result = model.transcribe(
            str(audio_path),
            language=language,
            verbose=False,
            word_timestamps=False  # Set to True for word-level timestamps
        )

        # Format segments with timestamps
        segments = []
        for segment in result['segments']:
            segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'start_time': format_timestamp(segment['start']),
                'end_time': format_timestamp(segment['end']),
                'text': segment['text'].strip()
            })

        # Prepare transcript data
        transcript_data = {
            'text': result['text'].strip(),
            'segments': segments,
            'language': result['language'],
            'duration': segments[-1]['end'] if segments else 0,
            'segment_count': len(segments)
        }

        # Save to cache
        with open(transcript_file, 'w', encoding='utf-8') as f:
            json.dump(transcript_data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Transcription complete!")
        print(f"  Language: {transcript_data['language']}")
        print(f"  Duration: {transcript_data['duration']:.1f} seconds")
        print(f"  Segments: {transcript_data['segment_count']}")

        return transcript_data

    except Exception as e:
        raise Exception(f"Failed to transcribe video: {str(e)}")


def get_transcript_text_with_timestamps(transcript_data: Dict) -> str:
    """
    Format transcript with timestamps for readability.

    Args:
        transcript_data: Transcript data dictionary

    Returns:
        Formatted transcript string with timestamps
    """
    lines = []
    for segment in transcript_data['segments']:
        timestamp = segment['start_time']
        text = segment['text']
        lines.append(f"[{timestamp}] {text}")

    return "\n".join(lines)


def get_cached_transcript(video_id: str, transcript_dir: Path = Path("cache/transcripts")) -> Optional[Dict]:
    """
    Retrieve cached transcript for a video.

    Args:
        video_id: Video ID
        transcript_dir: Transcript cache directory

    Returns:
        Transcript data if cached, None otherwise
    """
    transcript_dir = Path(transcript_dir)
    transcript_file = transcript_dir / f"{video_id}.json"

    if transcript_file.exists():
        with open(transcript_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    return None


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <video_path> [model_size]")
        sys.exit(1)

    test_video = sys.argv[1]
    test_model = sys.argv[2] if len(sys.argv) > 2 else "base"

    try:
        result = transcribe_video(test_video, model_size=test_model)

        print(f"\n{'='*60}")
        print("Transcription Results:")
        print(f"{'='*60}")
        print(f"Language: {result['language']}")
        print(f"Duration: {result['duration']:.1f} seconds")
        print(f"Segments: {result['segment_count']}")
        print(f"\nFirst 3 segments:")
        for i, segment in enumerate(result['segments'][:3], 1):
            print(f"  {i}. [{segment['start_time']}] {segment['text'][:80]}...")
        print(f"{'='*60}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
