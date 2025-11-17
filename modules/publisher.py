"""
Publishing Module
Saves articles as markdown and publishes to various platforms
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_markdown_frontmatter(
    article_data: Dict,
    seo_data: Optional[Dict] = None,
    video_metadata: Optional[Dict] = None
) -> str:
    """
    Create YAML frontmatter for markdown file.

    Args:
        article_data: Article data
        seo_data: SEO metadata
        video_metadata: Video metadata

    Returns:
        YAML frontmatter string
    """
    frontmatter = ["---"]

    # Basic metadata
    frontmatter.append(f"title: \"{article_data['title']}\"")
    frontmatter.append(f"subtitle: \"{article_data.get('subtitle', '')}\"")

    # Date
    frontmatter.append(f"date: {datetime.now().strftime('%Y-%m-%d')}")

    # SEO data if available
    if seo_data:
        frontmatter.append(f"description: \"{seo_data.get('meta_description', '')}\"")
        frontmatter.append(f"slug: {seo_data.get('slug', '')}")
        if seo_data.get('tags'):
            tags_str = ", ".join(seo_data['tags'])
            frontmatter.append(f"tags: [{tags_str}]")

    # Article metadata
    metadata = article_data.get('metadata', {})
    if metadata.get('word_count'):
        frontmatter.append(f"word_count: {metadata['word_count']}")
    if metadata.get('reading_time_minutes'):
        frontmatter.append(f"reading_time: {metadata['reading_time_minutes']}")

    # Video metadata if available
    if video_metadata:
        frontmatter.append(f"video_id: {video_metadata.get('video_id', '')}")
        frontmatter.append(f"video_url: {video_metadata.get('url', '')}")

    frontmatter.append("---\n")

    return "\n".join(frontmatter)


def embed_frames_in_markdown(
    article_body: str,
    frames_data: List[Dict],
    relative_path: bool = True
) -> str:
    """
    Embed frame references in article markdown.

    Args:
        article_body: Article markdown text
        frames_data: List of frame data dicts
        relative_path: Use relative paths for images

    Returns:
        Article with embedded image references
    """
    if not frames_data:
        return article_body

    # Add frames at the end of article
    article_body += "\n\n---\n\n## Screenshots\n\n"

    for frame in frames_data:
        timestamp = frame.get('timestamp', '')
        caption = frame.get('caption', '')
        frame_path = frame.get('frame_path', '')

        if relative_path:
            # Convert to relative path
            frame_path = Path(frame_path).name
            frame_path = f"../cache/frames/{frame_path}"

        article_body += f"\n### {timestamp}\n\n"
        article_body += f"![{caption}]({frame_path})\n\n"
        article_body += f"*{caption}*\n\n"

    return article_body


def save_markdown(
    article_data: Dict,
    output_dir: Path = Path("output/articles"),
    filename: Optional[str] = None,
    frames_data: Optional[List[Dict]] = None,
    seo_data: Optional[Dict] = None,
    video_metadata: Optional[Dict] = None
) -> Path:
    """
    Save article as markdown file with frontmatter.

    Args:
        article_data: Article data
        output_dir: Output directory
        filename: Custom filename (defaults to slugified title)
        frames_data: Frame data for embedding
        seo_data: SEO metadata
        video_metadata: Video metadata

    Returns:
        Path to saved markdown file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    if filename is None:
        if seo_data and seo_data.get('slug'):
            filename = f"{seo_data['slug']}.md"
        else:
            # Slugify title
            title = article_data['title']
            slug = title.lower()
            slug = "".join(c if c.isalnum() or c.isspace() else "" for c in slug)
            slug = "-".join(slug.split())[:50]
            filename = f"{slug}.md"

    output_path = output_dir / filename

    # Build markdown content
    content = []

    # Add frontmatter
    content.append(create_markdown_frontmatter(article_data, seo_data, video_metadata))

    # Add article body
    article_body = article_data['article_body']

    # Embed frames if provided
    if frames_data:
        article_body = embed_frames_in_markdown(article_body, frames_data)

    content.append(article_body)

    # Write file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))

    print(f"✓ Markdown saved: {output_path}")

    return output_path


def publish_to_medium(
    article_data: Dict,
    api_key: Optional[str] = None,
    draft: bool = True
) -> Dict:
    """
    Publish article to Medium.

    Args:
        article_data: Article data
        api_key: Medium API key
        draft: Publish as draft

    Returns:
        Response data from Medium API

    Raises:
        Exception: If publishing fails
    """
    if api_key is None:
        api_key = os.getenv('MEDIUM_API_KEY')

    if not api_key:
        raise ValueError("MEDIUM_API_KEY not found")

    print("📤 Publishing to Medium...")

    try:
        # Get user ID
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        user_response = requests.get(
            'https://api.medium.com/v1/me',
            headers=headers
        )
        user_response.raise_for_status()
        user_id = user_response.json()['data']['id']

        # Publish post
        post_data = {
            'title': article_data['title'],
            'contentFormat': 'markdown',
            'content': article_data['article_body'],
            'publishStatus': 'draft' if draft else 'public'
        }

        post_response = requests.post(
            f'https://api.medium.com/v1/users/{user_id}/posts',
            headers=headers,
            json=post_data
        )
        post_response.raise_for_status()

        result = post_response.json()['data']

        print(f"✓ Published to Medium: {result['url']}")

        return result

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to publish to Medium: {str(e)}")


def publish_to_devto(
    article_data: Dict,
    api_key: Optional[str] = None,
    draft: bool = True,
    tags: Optional[List[str]] = None
) -> Dict:
    """
    Publish article to Dev.to.

    Args:
        article_data: Article data
        api_key: Dev.to API key
        draft: Publish as draft
        tags: List of tags

    Returns:
        Response data from Dev.to API

    Raises:
        Exception: If publishing fails
    """
    if api_key is None:
        api_key = os.getenv('DEVTO_API_KEY')

    if not api_key:
        raise ValueError("DEVTO_API_KEY not found")

    print("📤 Publishing to Dev.to...")

    try:
        headers = {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }

        # Prepare tags
        if tags is None:
            tags = article_data.get('metadata', {}).get('key_topics', [])[:4]

        post_data = {
            'article': {
                'title': article_data['title'],
                'body_markdown': article_data['article_body'],
                'published': not draft,
                'tags': tags
            }
        }

        response = requests.post(
            'https://dev.to/api/articles',
            headers=headers,
            json=post_data
        )
        response.raise_for_status()

        result = response.json()

        print(f"✓ Published to Dev.to: {result['url']}")

        return result

    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to publish to Dev.to: {str(e)}")


def publish_article(
    article_data: Dict,
    platform: str = "local",
    output_dir: Path = Path("output/articles"),
    frames_data: Optional[List[Dict]] = None,
    seo_data: Optional[Dict] = None,
    video_metadata: Optional[Dict] = None,
    draft: bool = True
) -> Dict[str, any]:
    """
    Publish article to specified platform.

    Args:
        article_data: Article data
        platform: Platform name (local, medium, devto)
        output_dir: Output directory for local files
        frames_data: Frame data
        seo_data: SEO metadata
        video_metadata: Video metadata
        draft: Publish as draft

    Returns:
        Dictionary with publishing results

    Raises:
        ValueError: If platform is unsupported
        Exception: If publishing fails
    """
    results = {}

    # Always save local markdown
    markdown_path = save_markdown(
        article_data,
        output_dir,
        frames_data=frames_data,
        seo_data=seo_data,
        video_metadata=video_metadata
    )
    results['markdown_path'] = str(markdown_path)

    # Publish to platform if requested
    if platform.lower() == "medium":
        medium_result = publish_to_medium(article_data, draft=draft)
        results['medium_url'] = medium_result.get('url')

    elif platform.lower() == "devto":
        tags = seo_data.get('tags') if seo_data else None
        devto_result = publish_to_devto(article_data, draft=draft, tags=tags)
        results['devto_url'] = devto_result.get('url')

    elif platform.lower() != "local":
        raise ValueError(f"Unsupported platform: {platform}")

    return results


if __name__ == "__main__":
    # Test the module
    import sys

    if len(sys.argv) < 2:
        print("Usage: python publisher.py <article_json_path>")
        sys.exit(1)

    article_path = Path(sys.argv[1])

    try:
        # Load article data
        with open(article_path, 'r', encoding='utf-8') as f:
            article_data = json.load(f)

        # Save as markdown
        result = publish_article(article_data, platform="local")

        print(f"\n{'='*60}")
        print("Publishing Results:")
        print(f"{'='*60}")
        print(f"Markdown: {result['markdown_path']}")
        print(f"{'='*60}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
