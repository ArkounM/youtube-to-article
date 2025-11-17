# YouTube to Article Pipeline (Claude Code Edition)

An automated workflow that converts YouTube videos into well-structured, engaging articles using **Claude Code** (no API key required). The pipeline downloads videos, transcribes them with Whisper, and prepares everything for you to generate articles interactively with Claude Code.

## Features

- 🎥 **Video Download**: Download YouTube videos using yt-dlp with smart caching
- 🎤 **Transcription**: High-quality transcription with OpenAI Whisper (multiple model sizes)
- ✍️ **Article Generation**: Use Claude Code directly - no API key needed!
- 🖼️ **Frame Extraction**: Intelligent screenshot extraction at key moments
- 📤 **Publishing**: Save as markdown or publish to Medium, Dev.to
- 💾 **Caching**: Smart caching system to avoid reprocessing
- 🔧 **Modular Design**: Each component works independently

## How It Works

### Two-Step Process

**Step 1: Automated Preparation** (pipeline.py)
- Downloads YouTube video
- Transcribes with Whisper
- Saves transcript
- Creates generation prompt file

**Step 2: Article Generation** (You + Claude Code)
- Review the prompt file
- Ask Claude Code to generate the article
- Claude writes the article directly
- Extract frames and publish

## Project Structure

```
youtube-to-article/
├── config/
│   ├── config.yaml              # Main configuration
│   └── prompts/
│       └── article_generation.txt  # Template (not used with Claude Code)
├── modules/
│   ├── __init__.py
│   ├── video_download.py        # YouTube video downloader
│   ├── transcribe.py            # Whisper transcription
│   ├── frame_extractor.py       # Video frame extraction
│   ├── article_generator.py     # Prompt file generation
│   └── publisher.py             # Publishing to various platforms
├── cache/
│   ├── videos/                  # Downloaded videos
│   ├── audio/                   # Extracted audio files
│   ├── transcripts/             # Transcription JSON files
│   └── frames/                  # Extracted frames
├── output/
│   ├── prompts/                 # Generation prompt files
│   ├── transcripts/             # Human-readable transcripts
│   └── articles/                # Generated articles (JSON + markdown)
├── pipeline.py                  # Main orchestrator (Step 1)
├── generate_article.py          # Helper script (Step 2)
├── requirements.txt
└── README.md
```

## Prerequisites

### System Requirements

1. **Python 3.8+**
2. **ffmpeg** - Required for audio/video processing
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
3. **Claude Code** - The Anthropic CLI tool

### No API Keys Required!

Unlike the API version, this edition works entirely with Claude Code. No need for:
- ❌ Anthropic API key
- ❌ API credits
- ❌ Internet connection during article generation

## Installation

1. **Clone or download this project**

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify ffmpeg installation**
   ```bash
   ffmpeg -version
   ```

## Usage

### Complete Workflow

#### Step 1: Run the Pipeline

Download and transcribe a YouTube video:

```bash
python pipeline.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

This will:
- Download the video
- Transcribe it with Whisper
- Save the transcript
- Create a generation prompt file
- Print instructions for next steps

**Output:**
```
✅ Pipeline preparation complete!
📄 Video: [Video Title]
🎤 Transcript: output/transcripts/transcript_VIDEO_ID.txt
📝 Prompt file: output/prompts/article_prompt_VIDEO_ID_20250105_120000.txt

🤖 NEXT STEP: Generate the article using Claude Code
Run this command:
  python generate_article.py "output/prompts/article_prompt_VIDEO_ID_20250105_120000.txt"
```

#### Step 2: Generate Article with Claude Code

Option A - Using the helper script:
```bash
python generate_article.py "output/prompts/article_prompt_VIDEO_ID_20250105_120000.txt"
```

This prints instructions to copy-paste into Claude Code.

Option B - Directly in Claude Code:
```
Read output/prompts/article_prompt_VIDEO_ID_20250105_120000.txt and follow the instructions to generate the article
```

Claude Code will:
- Read the transcript
- Generate a well-structured article
- Identify key moments for screenshots
- Save the article as JSON to `output/articles/VIDEO_ID_article.json`

#### Step 3: Extract Frames and Publish (Optional)

After Claude generates the article JSON, you can:

1. **Extract video frames** at the key moments Claude identified
2. **Publish** the article as markdown

Ask Claude Code:
```
Read the article JSON at output/articles/VIDEO_ID_article.json, extract frames using the key_moments, and publish as markdown
```

Or create a simple script to do this automatically.

### Pipeline Options

```bash
# Skip cache and regenerate everything
python pipeline.py "https://www.youtube.com/watch?v=VIDEO_ID" --skip-cache

# Custom config file
python pipeline.py "https://www.youtube.com/watch?v=VIDEO_ID" --config my_config.yaml

# Save results to specific JSON file
python pipeline.py "https://www.youtube.com/watch?v=VIDEO_ID" --output-json results.json
```

### Testing Individual Modules

Each module can be tested independently:

```bash
# Test video download
python modules/video_download.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Test transcription (requires video file)
python modules/transcribe.py "cache/videos/VIDEO_ID.mp4" medium

# Test frame extraction
python modules/frame_extractor.py "cache/videos/VIDEO_ID.mp4" 300 5

# Test prompt generation (requires transcript JSON)
python modules/article_generator.py "cache/transcripts/VIDEO_ID.json"
```

## Configuration

Edit `config/config.yaml` to customize:

```yaml
transcription:
  method: "whisper"
  whisper_model: "medium"  # Options: tiny, base, small, medium, large
  language: "en"

article:
  style: "informative"  # Change article style
  target_word_count: 1500

frames:
  format: "jpg"
  quality: 85
  max_frames: 10

publishing:
  auto_publish: false
  platform: "medium"
  draft_mode: true
```

## Article Generation Prompt

The prompt file created by the pipeline contains:
- Video metadata (title, description, duration)
- Full timestamped transcript
- Article requirements (style, word count, format)
- Instructions for Claude Code
- Output format specification (JSON)

Claude Code reads this and generates:
```json
{
  "title": "Article title",
  "subtitle": "Article subtitle",
  "article_body": "Full markdown article...",
  "key_moments": [
    {
      "timestamp": "02:45",
      "description": "Key visual moment",
      "caption": "Screenshot caption"
    }
  ],
  "metadata": {
    "word_count": 1500,
    "reading_time_minutes": 7,
    "key_topics": ["topic1", "topic2"]
  }
}
```

## Output Files

### Generated by Pipeline

- **Video**: `cache/videos/VIDEO_ID.mp4`
- **Audio**: `cache/audio/VIDEO_ID.wav`
- **Transcript (JSON)**: `cache/transcripts/VIDEO_ID.json`
- **Transcript (Text)**: `output/transcripts/transcript_VIDEO_ID.txt`
- **Prompt File**: `output/prompts/article_prompt_VIDEO_ID_TIMESTAMP.txt`
- **Pipeline Results**: `output/pipeline_results_VIDEO_ID_TIMESTAMP.json`

### Generated by Claude Code

- **Article JSON**: `output/articles/VIDEO_ID_article.json`
- **Markdown Article**: `output/articles/article-title.md` (after publishing)
- **Frames**: `cache/frames/VIDEO_ID_frame_*.jpg` (after frame extraction)

## Advantages of Claude Code Edition

### vs. API Version

| Feature | API Version | Claude Code Edition |
|---------|-------------|-------------------|
| API Key Required | ✅ Yes | ❌ No |
| API Costs | 💰 Pay per use | 🆓 Free |
| Article Quality | High | High (same model) |
| Customization | Limited | Full control |
| Iteration | API calls | Interactive chat |
| Offline Work | No | Partially (after transcription) |

### Benefits

1. **No API Costs**: Use Claude Code unlimited without API charges
2. **Interactive Generation**: Review and refine articles in real-time
3. **Full Control**: See exactly what Claude is doing
4. **Easy Iteration**: Ask Claude to refine specific sections
5. **Learning Tool**: Understand the article generation process

## Troubleshooting

### Common Issues

**"ffmpeg not found"**
- Install ffmpeg and ensure it's in your system PATH
- Test with: `ffmpeg -version`

**Transcription is slow**
- Use a smaller Whisper model (tiny, base, small)
- Adjust in `config/config.yaml`: `whisper_model: "base"`

**Out of memory during transcription**
- Use a smaller Whisper model
- Process shorter videos
- Increase system RAM if possible

**Claude Code not generating article**
- Make sure the prompt file exists
- Read the prompt file in Claude Code
- Check the output format in the prompt

## Performance Tips

1. **Use caching**: Don't use `--skip-cache` unless necessary
2. **Choose appropriate Whisper model**:
   - `tiny`: Fastest, lower accuracy (~1GB RAM)
   - `base`: Good balance for testing (~1GB RAM)
   - `medium`: Recommended for production (~5GB RAM)
   - `large`: Best accuracy, slowest (~10GB RAM)
3. **Process videos in batches**: The pipeline handles one video at a time

## Workflow Examples

### Example 1: Basic Article Generation

```bash
# Step 1: Prepare
python pipeline.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Step 2: Generate (in Claude Code)
# "Read output/prompts/article_prompt_dQw4w9WgXcQ_20250105_120000.txt and generate the article"

# Step 3: Publish (in Claude Code)
# "Read output/articles/dQw4w9WgXcQ_article.json and save as markdown with frames"
```

### Example 2: Multiple Videos Batch Processing

```bash
# Prepare multiple videos
python pipeline.py "https://www.youtube.com/watch?v=VIDEO1"
python pipeline.py "https://www.youtube.com/watch?v=VIDEO2"
python pipeline.py "https://www.youtube.com/watch?v=VIDEO3"

# Then process each prompt with Claude Code
```

### Example 3: Custom Article Style

Edit `config/config.yaml`:
```yaml
article:
  style: "conversational"  # or "technical", "educational"
  target_word_count: 2500
```

Run pipeline again to generate new prompts with custom style.

## Extending the Pipeline

### Add Custom Frame Extraction

Create a script to automatically extract frames after article generation:

```python
# extract_and_publish.py
import json
from pathlib import Path
from modules.frame_extractor import extract_frames
from modules.publisher import publish_article

# Load article JSON
article_path = Path("output/articles/VIDEO_ID_article.json")
with open(article_path) as f:
    article_data = json.load(f)

# Extract frames
frames = extract_frames(
    "cache/videos/VIDEO_ID.mp4",
    article_data['key_moments']
)

# Publish with frames
publish_article(article_data, frames_data=frames)
```

### Add Custom Publishing Platforms

Extend `modules/publisher.py` to add new platforms.

## Contributing

This is a modular project. To add features:

1. Create new module in `modules/`
2. Add configuration to `config/config.yaml`
3. Update `pipeline.py` if needed
4. Add tests in module's `__main__` section

## License

MIT License - Feel free to use and modify for your projects.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for video downloading
- [OpenAI Whisper](https://github.com/openai/whisper) for transcription
- [Claude Code](https://github.com/anthropics/claude-code) for article generation
- [ffmpeg](https://ffmpeg.org/) for media processing

---

**Made with ❤️ using Claude Code and Python**
