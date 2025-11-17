"""
Extract frames from video based on article JSON key moments
"""
import sys
import io
import json
from pathlib import Path

# Force UTF-8 encoding for stdout/stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from modules.frame_extractor import extract_frames

def main():
    # Load article JSON
    article_path = 'output/articles/15d0iHhJEfM_article.json'
    print(f"Loading article from: {article_path}")

    with open(article_path, 'r', encoding='utf-8') as f:
        article_data = json.load(f)

    # Extract frames
    video_path = 'cache/videos/15d0iHhJEfM.mp4'
    print(f"Video path: {video_path}")
    print(f"Extracting {len(article_data['key_moments'])} frames...\n")

    frames = extract_frames(
        video_path,
        article_data['key_moments'],
        frames_dir=Path('cache/frames'),
        quality=85,
        name_prefix='15d0iHhJEfM'
    )

    print('\n' + '='*70)
    print('Frame Extraction Complete!')
    print('='*70)
    for frame in frames:
        print(f"  {frame['frame_number']}. [{frame['timestamp']}] {frame['frame_path']}")
    print('='*70)

    return frames

if __name__ == "__main__":
    main()
