"""
Article Generation Module
Creates prompt files for Claude Code to generate articles from transcripts
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


def format_transcript_for_prompt(transcript_data: Dict) -> str:
    """
    Format transcript data for inclusion in prompt.

    Args:
        transcript_data: Transcript data with segments

    Returns:
        Formatted transcript string with timestamps
    """
    lines = []
    for segment in transcript_data['segments']:
        timestamp = segment['start_time']
        text = segment['text']
        lines.append(f"[{timestamp}] {text}")

    return "\n".join(lines)


def create_generation_prompt(
    transcript_data: Dict,
    video_metadata: Dict,
    config: Dict,
    output_dir: Path = Path("output/prompts")
) -> Path:
    """
    Create a prompt file for Claude Code to generate an article.

    Args:
        transcript_data: Transcript data with segments
        video_metadata: Video metadata (title, description, etc.)
        config: Configuration dict with article settings
        output_dir: Directory to save prompt files

    Returns:
        Path to created prompt file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    video_id = video_metadata.get('video_id', 'unknown')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prompt_filename = f"article_prompt_{video_id}_{timestamp}.txt"
    prompt_path = output_dir / prompt_filename

    # Format transcript
    formatted_transcript = format_transcript_for_prompt(transcript_data)

    # Build prompt content
    prompt_content = f"""# Article Generation Task

You are tasked with converting a YouTube video transcript into a well-structured, engaging article.

## Video Information

**Title:** {video_metadata.get('title', 'Unknown')}
**Duration:** {int(video_metadata.get('duration', 0) / 60)} minutes
**Video ID:** {video_metadata.get('video_id', 'Unknown')}
**URL:** {video_metadata.get('url', 'Unknown')}

**Description:**
{video_metadata.get('description', 'No description')[:500]}

## Article Requirements

- **Style:** {config.get('style', 'informative')}
- **Target Word Count:** {config.get('target_word_count', 1500)} words
- **Format:** Markdown with proper headings and structure

## Your Task

1. **Analyze the transcript below** and understand the key points, insights, and flow
2. **Write a compelling article** that:
   - Has an engaging title and subtitle
   - Maintains the speaker's voice and key insights
   - Is structured with clear sections and headings
   - Makes it readable and engaging for web audiences
   - Adds transitions and narrative flow where needed
   - Avoids simply transcribing - transform it into article format

3. **Identify 5-10 key moments** where screenshots would enhance the article
   - For each moment, provide: timestamp (MM:SS), description, and caption

4. **Save the output** in this JSON format:

```json
{{
  "title": "Main article title",
  "subtitle": "Engaging subtitle or tagline",
  "article_body": "Full article text with markdown formatting...",
  "key_moments": [
    {{
      "timestamp": "MM:SS",
      "description": "What's happening at this moment",
      "caption": "Caption for the screenshot"
    }}
  ],
  "metadata": {{
    "word_count": 1500,
    "reading_time_minutes": 7,
    "key_topics": ["topic1", "topic2", "topic3"]
  }}
}}
```

5. **Save this JSON** to: `output/articles/{video_id}_article.json`

## Transcript

{formatted_transcript}

---

## Instructions for Execution

After reading this file, execute the following:

1. Generate the article following all requirements above
2. Save the JSON output to `output/articles/{video_id}_article.json`
3. Inform the user that the article has been generated and where it was saved
"""

    # Write prompt file
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt_content)

    print(f"✓ Generation prompt created: {prompt_path}")

    return prompt_path


def save_transcript_file(
    transcript_data: Dict,
    video_metadata: Dict,
    output_dir: Path = Path("output/transcripts")
) -> Path:
    """
    Save formatted transcript as a readable text file.

    Args:
        transcript_data: Transcript data with segments
        video_metadata: Video metadata
        output_dir: Directory to save transcript files

    Returns:
        Path to saved transcript file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    video_id = video_metadata.get('video_id', 'unknown')
    transcript_filename = f"transcript_{video_id}.txt"
    transcript_path = output_dir / transcript_filename

    # Format transcript with header
    lines = [
        "=" * 70,
        f"TRANSCRIPT: {video_metadata.get('title', 'Unknown')}",
        "=" * 70,
        f"Video ID: {video_metadata.get('video_id', 'Unknown')}",
        f"Duration: {int(video_metadata.get('duration', 0) / 60)} minutes",
        f"URL: {video_metadata.get('url', 'Unknown')}",
        "=" * 70,
        ""
    ]

    # Add timestamped transcript
    for segment in transcript_data['segments']:
        timestamp = segment['start_time']
        text = segment['text']
        lines.append(f"[{timestamp}] {text}")

    # Write file
    with open(transcript_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    print(f"✓ Transcript saved: {transcript_path}")

    return transcript_path


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) < 2:
        print("Usage: python article_generator.py <transcript_json_path>")
        sys.exit(1)

    transcript_path = Path(sys.argv[1])

    try:
        # Load transcript
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)

        # Mock metadata and config
        video_metadata = {
            'title': 'Test Video',
            'duration': 600,
            'description': 'Test description',
            'video_id': 'test123',
            'url': 'https://youtube.com/watch?v=test123'
        }

        config = {
            'style': 'informative',
            'target_word_count': 1500
        }

        # Create prompt file
        prompt_path = create_generation_prompt(transcript_data, video_metadata, config)
        transcript_file = save_transcript_file(transcript_data, video_metadata)

        print(f"\n{'='*60}")
        print("Files Created:")
        print(f"{'='*60}")
        print(f"Prompt: {prompt_path}")
        print(f"Transcript: {transcript_file}")
        print(f"{'='*60}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
