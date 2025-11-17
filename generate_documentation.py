"""
Documentation Generation Script
Processes the documentation JSON output from Claude Code and creates the final file structure
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from modules.documentation_generator import (
    save_documentation_structure,
    generate_documentation_index,
    extract_key_moments_from_docs
)


def safe_print(text):
    """Print safely handling Unicode on Windows."""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'ignore').decode('ascii'))


def process_documentation_json(
    json_path: str,
    output_dir: Path = Path("output/documentation"),
    generate_frames: bool = True
) -> dict:
    """
    Process documentation JSON and create the documentation structure.

    Args:
        json_path: Path to the documentation JSON file from Claude
        output_dir: Directory to save the documentation files
        generate_frames: Whether to generate frame extraction instructions

    Returns:
        Dictionary with processing results
    """
    json_path = Path(json_path)

    if not json_path.exists():
        raise FileNotFoundError(f"Documentation JSON not found: {json_path}")

    # Load the documentation JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        docs_json = json.load(f)

    print("="*70)
    safe_print("📚 Processing Documentation Output")
    print("="*70)
    print(f"Input: {json_path}")
    print("="*70 + "\n")

    results = {
        'input_json': str(json_path),
        'output_directory': str(output_dir),
        'main_topic': docs_json.get('main_topic', 'Unknown'),
        'total_pages': 0,
        'created_files': {},
        'key_moments': [],
        'status': 'processing'
    }

    try:
        # Step 1: Save documentation files
        safe_print("📝 STEP 1: Creating documentation files...")
        print("-" * 70)
        created_files = save_documentation_structure(
            docs_json,
            output_dir=output_dir,
            create_md_files=True
        )
        results['created_files'] = {k: str(v) for k, v in created_files.items()}
        results['total_pages'] = len(created_files)
        print()

        # Step 2: Generate Docusaurus sidebar index
        safe_print("📋 STEP 2: Generating Docusaurus sidebar index...")
        print("-" * 70)
        index_path = generate_documentation_index(docs_json, output_dir=output_dir)
        results['sidebar_index'] = str(index_path)
        print()

        # Step 3: Extract key moments for frame generation
        if generate_frames:
            safe_print("🖼️  STEP 3: Extracting key moments for frame generation...")
            print("-" * 70)
            key_moments = extract_key_moments_from_docs(docs_json)
            results['key_moments'] = key_moments
            results['total_moments'] = len(key_moments)

            # Create a frame extraction instruction file
            frames_instruction_path = output_dir / f"frames_instruction_{docs_json.get('main_topic', 'docs').lower().replace(' ', '_')}.txt"
            output_dir.mkdir(parents=True, exist_ok=True)

            with open(frames_instruction_path, 'w', encoding='utf-8') as f:
                f.write("# Frame Extraction Instructions\n\n")
                f.write(f"Documentation: {docs_json.get('main_topic', 'Unknown')}\n")
                f.write(f"Total frames to extract: {len(key_moments)}\n\n")

                for i, moment in enumerate(key_moments, 1):
                    f.write(f"{i}. **{moment.get('description', 'Unknown')}**\n")
                    f.write(f"   - Page: {moment.get('page', 'Unknown')}\n")
                    f.write(f"   - Timestamp: {moment.get('timestamp', 'Unknown')}\n")
                    f.write(f"   - Image: {moment.get('image_name', 'frame.png')}\n")
                    f.write(f"   - Caption: {moment.get('caption', '')}\n\n")

            results['frames_instruction_file'] = str(frames_instruction_path)
            print(f"✓ Frame extraction instructions: {frames_instruction_path}")
            print()

        # Step 4: Create summary
        safe_print("✅ STEP 4: Creating documentation summary...")
        print("-" * 70)

        # Create structure summary
        structure_summary = {
            'main_topic': docs_json.get('main_topic', 'Unknown'),
            'pages': [
                {
                    'id': page.get('page_id', 'unknown'),
                    'title': page.get('title', 'Untitled'),
                    'position': page.get('sidebar_position', 0),
                    'moments': len(page.get('key_moments', []))
                }
                for page in docs_json.get('pages', [])
            ],
            'metadata': docs_json.get('metadata', {})
        }

        summary_path = output_dir / f"structure_{docs_json.get('main_topic', 'docs').lower().replace(' ', '_')}.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(structure_summary, f, indent=2, ensure_ascii=False)

        results['structure_summary'] = str(summary_path)
        print()

        # Final summary
        results['status'] = 'completed'
        print("="*70)
        safe_print("✅ Documentation processing complete!")
        print("="*70)
        safe_print(f"📚 Topic: {results['main_topic']}")
        safe_print(f"📄 Pages created: {results['total_pages']}")
        safe_print(f"🖼️  Key moments identified: {results['total_moments']}")
        safe_print(f"📁 Output directory: {output_dir}")
        print("="*70)
        print("\nNext Steps:")
        print("1. Review the generated .md files in the output directory")
        print("2. Add your images to the /img/ subdirectory according to the structure")
        print("3. Adjust sidebar positions and cross-links as needed")
        if generate_frames:
            print(f"4. Use the frame extraction instructions in: {results['frames_instruction_file']}")
            print("5. Extract frames from the video at specified timestamps")
        print()

        return results

    except Exception as e:
        results['status'] = 'failed'
        results['error'] = str(e)
        print(f"\n❌ Processing failed: {str(e)}")
        raise


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Generate Docusaurus documentation from Claude-generated JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process documentation JSON
  python generate_documentation.py output/documentation/video_id_docs.json

  # Custom output directory
  python generate_documentation.py output/documentation/video_id_docs.json --output docs/

  # Don't generate frame instructions
  python generate_documentation.py output/documentation/video_id_docs.json --no-frames
        """
    )

    parser.add_argument(
        'json_file',
        help='Path to the documentation JSON file from Claude'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='output/documentation',
        help='Output directory for documentation files (default: output/documentation)'
    )

    parser.add_argument(
        '--no-frames',
        action='store_true',
        help='Skip frame extraction instructions'
    )

    args = parser.parse_args()

    try:
        results = process_documentation_json(
            json_path=args.json_file,
            output_dir=Path(args.output),
            generate_frames=not args.no_frames
        )

        # Save processing results
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        results_path = output_dir / "processing_results.json"

        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        safe_print(f"\n💾 Processing results saved: {results_path}")
        sys.exit(0)

    except KeyboardInterrupt:
        safe_print("\n\n⚠️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        safe_print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
