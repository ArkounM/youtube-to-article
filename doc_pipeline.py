"""
Documentation Pipeline - Generate Docusaurus documentation from YouTube videos
Automated workflow to convert YouTube videos into structured documentation pages
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import yaml

from modules.video_download import download_video
from modules.transcribe import transcribe_video
from modules.documentation_generator import (
    create_doc_generation_prompt,
    generate_documentation_index,
    save_documentation_structure
)

# Safe print function for Windows console
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        # Remove emojis and try again
        print(text.encode('ascii', 'ignore').decode('ascii'))


def load_config(config_path: Path = Path("config/config.yaml")) -> Dict:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def save_pipeline_results(results: Dict, output_dir: Path = Path("output")) -> Path:
    """
    Save documentation pipeline results as JSON.

    Args:
        results: Pipeline results dictionary
        output_dir: Output directory

    Returns:
        Path to saved results file
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    video_id = results.get('video_metadata', {}).get('video_id', 'unknown')
    results_path = output_dir / f"doc_pipeline_results_{video_id}_{timestamp}.json"

    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return results_path


def run_doc_pipeline(
    input_source: str,
    config: Optional[Dict] = None,
    skip_cache: bool = False
) -> Dict:
    """
    Run the Documentation Pipeline (download/load + transcribe + create prompt).

    Args:
        input_source: YouTube video URL or local file path
        config: Configuration dict (loads from file if None)
        skip_cache: Skip cached results

    Returns:
        Dictionary with pipeline results

    Raises:
        Exception: If any step fails
    """
    # Load config if not provided
    if config is None:
        config = load_config()

    results = {
        'input_source': input_source,
        'pipeline_type': 'documentation',
        'timestamp': datetime.now().isoformat(),
        'status': 'started'
    }

    print("="*70)
    safe_print("📚 Documentation Pipeline (Claude Code Edition)")
    print("="*70)
    print(f"Input: {input_source}")
    print(f"Skip cache: {skip_cache}")
    print("="*70 + "\n")

    try:
        # Step 1: Download/load video
        if input_source.startswith(('http://', 'https://', 'www.')):
            safe_print("📥 STEP 1: Downloading video...")
        else:
            safe_print("📥 STEP 1: Loading local video...")
        print("-" * 70)
        video_metadata = download_video(input_source, skip_cache=skip_cache)
        results['video_metadata'] = video_metadata
        print()

        # Step 2: Transcribe
        safe_print("🎤 STEP 2: Transcribing video...")
        print("-" * 70)
        doc_config = config.get('documentation', {})
        transcript_data = transcribe_video(
            video_metadata['video_path'],
            model_size=config['transcription']['whisper_model'],
            language=config['transcription']['language'],
            skip_cache=skip_cache
        )
        results['transcript'] = transcript_data
        print()

        # Step 3: Create documentation generation prompt
        safe_print("📝 STEP 3: Creating documentation generation prompt...")
        print("-" * 70)
        prompt_file = create_doc_generation_prompt(
            transcript_data,
            video_metadata,
            doc_config
        )
        results['prompt_file'] = str(prompt_file)
        print()

        # Save results
        safe_print("💾 Saving pipeline results...")
        print("-" * 70)
        results_path = save_pipeline_results(results)
        results['results_path'] = str(results_path)
        safe_print(f"✓ Results saved: {results_path}\n")

        # Final summary and instructions
        results['status'] = 'ready_for_generation'
        print("="*70)
        safe_print("✅ Documentation pipeline preparation complete!")
        print("="*70)
        safe_print(f"📺 Video: {results['video_metadata']['title']}")
        safe_print(f"🎤 Transcript: {transcript_data}")
        safe_print(f"📝 Prompt file: {prompt_file}")
        print("="*70)
        safe_print("\n🤖 NEXT STEP: Generate documentation using Claude Code")
        print("-" * 70)
        print(f"Run this command:\n")
        print(f"  python generate_documentation.py \"{prompt_file}\"\n")
        print("Or manually tell Claude Code:")
        print(f"  \"Read {prompt_file} and follow the instructions to generate the documentation\"\n")
        print("="*70)

        return results

    except Exception as e:
        results['status'] = 'failed'
        results['error'] = str(e)
        print(f"\n❌ Pipeline failed: {str(e)}")
        raise


def main():
    """
    Main entry point for CLI.
    """
    parser = argparse.ArgumentParser(
        description="Documentation Pipeline - Generate Docusaurus docs from videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # YouTube video
  python doc_pipeline.py https://www.youtube.com/watch?v=VIDEO_ID

  # Local MP4 file
  python doc_pipeline.py path/to/video.mp4

  # Skip cache and regenerate everything
  python doc_pipeline.py https://www.youtube.com/watch?v=VIDEO_ID --skip-cache

  # Custom config file
  python doc_pipeline.py path/to/video.mp4 --config my_config.yaml

After running this pipeline:
  1. Review the generated prompt file in output/doc_prompts/
  2. Run: python generate_documentation.py <prompt_file>
  3. Or tell Claude Code to read the prompt file and generate the documentation
        """
    )

    parser.add_argument(
        'input',
        help='YouTube video URL or path to local video file'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to config file (default: config/config.yaml)'
    )

    parser.add_argument(
        '--skip-cache',
        action='store_true',
        help='Skip cached results and regenerate everything'
    )

    parser.add_argument(
        '--output-json',
        type=str,
        help='Save results to specific JSON file'
    )

    args = parser.parse_args()

    try:
        # Load config
        config = load_config(Path(args.config))

        # Run documentation pipeline
        results = run_doc_pipeline(
            input_source=args.input,
            config=config,
            skip_cache=args.skip_cache
        )

        # Save to custom path if specified
        if args.output_json:
            output_path = Path(args.output_json)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            safe_print(f"\n💾 Results also saved to: {output_path}")

        sys.exit(0)

    except KeyboardInterrupt:
        safe_print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        safe_print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
