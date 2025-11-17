"""
Article Generation Helper for Claude Code
This script provides a convenient way to trigger Claude Code article generation
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    """
    Main entry point for the article generation helper.
    """
    parser = argparse.ArgumentParser(
        description="Generate article from prompt file using Claude Code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This is a helper script that prints instructions for Claude Code.

Usage:
  1. Run the pipeline: python pipeline.py <youtube_url>
  2. Run this script: python generate_article.py <prompt_file>
  3. Follow the printed instructions to have Claude Code generate the article

Example:
  python generate_article.py output/prompts/article_prompt_abc123_20250105_120000.txt
        """
    )

    parser.add_argument(
        'prompt_file',
        help='Path to the generation prompt file'
    )

    args = parser.parse_args()

    prompt_file = Path(args.prompt_file)

    if not prompt_file.exists():
        print(f"❌ Error: Prompt file not found: {prompt_file}")
        sys.exit(1)

    print("="*70)
    print("🤖 Article Generation with Claude Code")
    print("="*70)
    print(f"Prompt file: {prompt_file}")
    print("="*70)
    print("\nCopy and paste this message to Claude Code:\n")
    print("-" * 70)
    print(f'Read the file "{prompt_file}" and follow ALL the instructions inside.')
    print("Generate the article according to the requirements and save the JSON output")
    print("to the specified location.")
    print("-" * 70)
    print("\nOr simply run this in Claude Code chat:")
    print(f'  "Read {prompt_file} and execute the instructions"')
    print("="*70)


if __name__ == "__main__":
    main()
