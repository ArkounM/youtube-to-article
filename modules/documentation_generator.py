"""
Documentation Generation Module
Creates Docusaurus-formatted documentation pages from video transcripts
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def create_doc_generation_prompt(
    transcript_data: Dict,
    video_metadata: Dict,
    config: Dict,
    output_dir: Path = Path("output/doc_prompts")
) -> Path:
    """
    Create a prompt file for Claude Code to generate documentation pages.

    Args:
        transcript_data: Transcript data with segments
        video_metadata: Video metadata (title, description, etc.)
        config: Configuration dict with documentation settings
        output_dir: Directory to save prompt files

    Returns:
        Path to created prompt file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    video_id = video_metadata.get('video_id', 'unknown')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prompt_filename = f"doc_prompt_{video_id}_{timestamp}.txt"
    prompt_path = output_dir / prompt_filename

    # Format transcript
    formatted_transcript = format_transcript_for_prompt(transcript_data)

    # Build prompt content
    prompt_content = f"""# Documentation Generation Task

You are tasked with converting a YouTube video transcript into a comprehensive Docusaurus documentation structure.

## Video Information

**Title:** {video_metadata.get('title', 'Unknown')}
**Duration:** {int(video_metadata.get('duration', 0) / 60)} minutes
**Video ID:** {video_metadata.get('video_id', 'Unknown')}
**URL:** {video_metadata.get('url', 'Unknown')}

**Description:**
{video_metadata.get('description', 'No description')[:500]}

## Documentation Requirements

- **Style:** {config.get('style', 'technical')}
- **Target Format:** Docusaurus Markdown (.md)
- **Page Structure:** Create multiple .md files for subtopics within the main topic
- **Image Path Pattern:** `/img/{config.get('image_subfolder', 'default')}/`
- **Front Matter Required:** Yes (YAML frontmatter for Docusaurus)

## Your Task

1. **Analyze the transcript below** and identify the main topic and subtopics
2. **Create a hierarchical documentation structure** where:
   - Each major topic becomes its own .md file
   - Subtopics become H2 (##) or H3 (###) sections
   - Content is organized logically for reference

3. **For each page, include:**
   - Clear, descriptive title
   - Docusaurus YAML front matter (sidebar_position, label)
   - Introduction/Overview section
   - Detailed sections with step-by-step instructions where applicable
   - Key points and tips highlighted with blockquotes or emphasis
   - Cross-references to related pages using [link text](/path/to/page)

4. **Identify 3-5 key moments per page** where screenshots/frames would enhance documentation
   - For each moment, provide: timestamp (MM:SS), description, and caption
   - Images should be referenced as: ![Description](/img/{config.get('image_subfolder', 'default')}/image-name.png)

5. **Example page structure:**

```markdown
---
sidebar_position: 1
label: "Basic Navigation Setup"
---

# Basic Navigation Setup

Perfect for single focus assets ranging in scale from an object to a building.

## Installation

1. Open your Unreal Engine project
2. Navigate to **Window > World Settings**
3. Set your **Game Mode** to `TSI_Gamemode_Basic`

![Set Basic Game Mode](/img/archviz-nav/basic-1.png)

This will automatically configure:

- Appropriate player character
- Player controller
- HUD class

## Setting Spawn Location

To set where the player spawns:

1. Place a **PlayerStart** actor in your level
2. Position it at your desired spawn location
3. The player will automatically spawn at this location when the app starts

![Set Player Start](/img/archviz-nav/basic-2.png)
![Set Start Location](/img/archviz-nav/basic-3.png)

## How It Works

The basic navigation system relies on a camera attached to the pawn...
```

6. **Output Format - Save as JSON:**

```json
{{
  "main_topic": "Main title from video",
  "overview": "Brief overview of the documentation structure",
  "pages": [
    {{
      "page_id": "page-slug",
      "title": "Page Title",
      "sidebar_position": 1,
      "content": "Full markdown content with YAML frontmatter...",
      "key_moments": [
        {{
          "timestamp": "MM:SS",
          "description": "What's happening at this moment",
          "caption": "Caption for the screenshot",
          "image_name": "descriptive-name.png"
        }}
      ],
      "related_pages": ["page-slug-2", "page-slug-3"]
    }},
    {{
      "page_id": "page-slug-2",
      "title": "Page Title 2",
      "sidebar_position": 2,
      "content": "Full markdown content...",
      "key_moments": [],
      "related_pages": ["page-slug"]
    }}
  ],
  "metadata": {{
    "total_pages": 3,
    "main_topic": "Main title",
    "subtopics": ["topic1", "topic2", "topic3"],
    "total_key_moments": 12,
    "image_subfolder": "{config.get('image_subfolder', 'default')}"
  }}
}}
```

7. **Save the output** to: `output/documentation/{video_id}_docs.json`

## Transcript

{formatted_transcript}

---

## Instructions for Execution

After reading this file, execute the following:

1. Generate documentation structure following all requirements above
2. Create multiple documentation pages (each as its own .md file in the JSON structure)
3. Ensure each page has proper Docusaurus frontmatter
4. Identify key moments for screenshots across all pages
5. Save the JSON output to `output/documentation/{video_id}_docs.json`
6. Inform the user that documentation has been generated and where it was saved
"""

    # Write prompt file
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt_content)

    print(f"[OK] Documentation generation prompt created: {prompt_path}")

    return prompt_path


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


def save_documentation_structure(
    docs_json: Dict,
    output_dir: Path = Path("output/documentation"),
    create_md_files: bool = True
) -> Dict[str, Path]:
    """
    Save documentation structure and optionally create markdown files from JSON.

    Args:
        docs_json: Documentation structure JSON from Claude
        output_dir: Directory to save documentation files
        create_md_files: Whether to create individual .md files

    Returns:
        Dictionary mapping page IDs to file paths
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    created_files = {}

    if create_md_files and 'pages' in docs_json:
        # Create a subdirectory for the documentation
        main_topic_slug = docs_json.get('main_topic', 'docs').lower().replace(' ', '-')
        doc_subdir = output_dir / main_topic_slug

        for page in docs_json['pages']:
            page_id = page.get('page_id', 'unknown')
            content = page.get('content', '')

            # Create markdown file
            md_filename = f"{page_id}.md"
            md_path = doc_subdir / md_filename
            doc_subdir.mkdir(parents=True, exist_ok=True)

            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)

            created_files[page_id] = md_path
            print(f"[OK] Documentation page created: {md_path}")

    return created_files


def extract_key_moments_from_docs(docs_json: Dict) -> List[Dict]:
    """
    Extract all key moments from documentation structure for frame extraction.

    Args:
        docs_json: Documentation structure JSON

    Returns:
        List of all key moments with page context
    """
    all_moments = []

    for page in docs_json.get('pages', []):
        page_title = page.get('title', 'Unknown')
        for moment in page.get('key_moments', []):
            moment_with_context = {
                **moment,
                'page': page_title,
                'page_id': page.get('page_id', 'unknown')
            }
            all_moments.append(moment_with_context)

    return all_moments


def generate_documentation_index(
    docs_json: Dict,
    output_dir: Path = Path("output/documentation")
) -> Path:
    """
    Generate a _category_.json file for Docusaurus to structure the sidebar.

    Args:
        docs_json: Documentation structure JSON
        output_dir: Directory for the documentation

    Returns:
        Path to generated _category_.json file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    main_topic_slug = docs_json.get('main_topic', 'docs').lower().replace(' ', '-')
    category_path = output_dir / main_topic_slug / "_category_.json"
    category_path.parent.mkdir(parents=True, exist_ok=True)

    category_data = {
        "label": docs_json.get('main_topic', 'Documentation'),
        "position": 1,
        "collapsed": False,
        "items": [
            {
                "type": "doc",
                "id": page.get('page_id', 'unknown'),
                "label": page.get('title', 'Untitled')
            }
            for page in docs_json.get('pages', [])
        ]
    }

    with open(category_path, 'w', encoding='utf-8') as f:
        json.dump(category_data, f, indent=2, ensure_ascii=False)

    print(f"[OK] Docusaurus category index created: {category_path}")

    return category_path


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) < 2:
        print("Usage: python documentation_generator.py <docs_json_path>")
        sys.exit(1)

    docs_path = Path(sys.argv[1])

    try:
        # Load documentation JSON
        with open(docs_path, 'r', encoding='utf-8') as f:
            docs_json = json.load(f)

        # Save documentation files
        created = save_documentation_structure(docs_json)

        # Generate index
        index_path = generate_documentation_index(docs_json)

        print(f"\n{'='*60}")
        print("Documentation Created:")
        print(f"{'='*60}")
        print(f"Pages created: {len(created)}")
        print(f"Index: {index_path}")
        print(f"{'='*60}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
