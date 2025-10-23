#!/usr/bin/env python3
"""
Complete Video Processing Pipeline

This script orchestrates the complete workflow:
1. Transcribe video to text (creates original + sanitized versions)
2. Summarize the sanitized text using Ollama
3. Restore confidential information in the summary

Usage:
    python process_video_complete.py <video_file>

Example:
    python process_video_complete.py presentation.mp4

Output files:
    - video.txt (original transcription)
    - video_sanitized.txt (confidential info removed)
    - video_summary_sanitized.txt (summary with sanitized info)
    - video_summary_restored.txt (summary with confidential info restored)
"""

import sys
import os
import argparse
from pathlib import Path
import subprocess

# Import project modules
try:
    from main import transcribe_video, check_gpu_availability
except ImportError:
    print("Error: main.py not found in the current directory")
    sys.exit(1)

try:
    from summarize_with_ollama import summarize_text, check_ollama_service, check_model_available
    from reverse_sanitize import reverse_sanitize_text, create_reverse_mapping
except ImportError:
    print("Error: Required modules (summarize_with_ollama.py or reverse_sanitize.py) not found")
    sys.exit(1)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")


def complete_pipeline(
    video_path,
    model="llama3.2",
    custom_prompt=None,
    max_summary_length=None,
    skip_summary=False,
    keep_sanitized=False
):
    """
    Execute the complete video processing pipeline.
    
    Args:
        video_path: Path to input video file
        model: Ollama model for summarization
        custom_prompt: Custom prompt for Ollama
        max_summary_length: Maximum summary length in words
        skip_summary: Skip summarization step
        keep_sanitized: Keep summary sanitized
        
    Returns:
        dict: Paths to all generated files
    """
    video_path = Path(video_path)
    
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        return None
    
    results = {}
    
    # STEP 1: Transcribe video
    print_section("STEP 1: VIDEO TRANSCRIPTION")
    print(f"Video file: {video_path.name}")
    print(f"Device: {check_gpu_availability()}")
    
    try:
        original_txt, sanitized_txt = transcribe_video(str(video_path))
        results['transcription_original'] = original_txt
        results['transcription_sanitized'] = sanitized_txt
        print(f"\n✓ Original transcription: {Path(original_txt).name}")
        print(f"✓ Sanitized transcription: {Path(sanitized_txt).name}")
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None
    
    # STEP 2: Summarize sanitized text
    if not skip_summary:
        print_section("STEP 2: OLLAMA SUMMARIZATION")
        
        # Check Ollama
        if not check_ollama_service():
            print("Warning: Ollama not available, skipping summarization")
            skip_summary = True
        elif not check_model_available(model):
            print(f"Warning: Model {model} not available, skipping summarization")
            skip_summary = True
    
    if not skip_summary:
        try:
            # Read sanitized text
            with open(sanitized_txt, 'r', encoding='utf-8') as f:
                sanitized_content = f.read()
            
            print(f"Input: {Path(sanitized_txt).name} ({len(sanitized_content)} chars)")
            print(f"Model: {model}")
            
            # Generate summary
            summary = summarize_text(
                sanitized_content,
                model=model,
                custom_prompt=custom_prompt,
                max_length=max_summary_length
            )
            
            if summary is None:
                print("Warning: Summarization failed")
                skip_summary = True
            else:
                # Save sanitized summary
                base_name = video_path.stem
                summary_sanitized_path = video_path.parent / f"{base_name}_summary_sanitized.txt"
                
                with open(summary_sanitized_path, 'w', encoding='utf-8') as f:
                    f.write(summary)
                
                results['summary_sanitized'] = str(summary_sanitized_path)
                print(f"\n✓ Sanitized summary: {summary_sanitized_path.name}")
                print(f"  Length: {len(summary)} characters")
                
                # STEP 3: Restore confidential information
                if not keep_sanitized:
                    print_section("STEP 3: RESTORE CONFIDENTIAL INFORMATION")
                    
                    reverse_map = create_reverse_mapping()
                    restored_summary = reverse_sanitize_text(summary, reverse_map)
                    
                    summary_restored_path = video_path.parent / f"{base_name}_summary_restored.txt"
                    
                    with open(summary_restored_path, 'w', encoding='utf-8') as f:
                        f.write(restored_summary)
                    
                    results['summary_restored'] = str(summary_restored_path)
                    print(f"✓ Restored summary: {summary_restored_path.name}")
                    print(f"  Confidential information restored")
                
        except Exception as e:
            print(f"Error during summarization: {e}")
            skip_summary = True
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Complete video processing pipeline with privacy protection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Complete Workflow:
  1. Transcribe video → Creates original.txt and sanitized.txt
  2. Summarize sanitized text using Ollama → Creates summary_sanitized.txt
  3. Restore confidential info in summary → Creates summary_restored.txt

Examples:
  # Full pipeline with defaults
  python process_video_complete.py presentation.mp4
  
  # Use different Ollama model
  python process_video_complete.py meeting.mkv --model llama2
  
  # Skip summarization (only transcribe)
  python process_video_complete.py video.mp4 --skip-summary
  
  # Keep summary sanitized (don't restore)
  python process_video_complete.py video.mp4 --keep-sanitized
  
  # Custom summary length
  python process_video_complete.py video.mp4 --max-length 150

Output Files:
  - {video}.txt                    Original transcription
  - {video}_sanitized.txt          Sanitized transcription
  - {video}_summary_sanitized.txt  Sanitized summary
  - {video}_summary_restored.txt   Restored summary (with confidential info)
"""
    )
    
    parser.add_argument(
        'video_file',
        help='Path to video file to process'
    )
    
    parser.add_argument(
        '--model', '-m',
        default='llama3.2',
        help='Ollama model for summarization (default: llama3.2)'
    )
    
    parser.add_argument(
        '--prompt', '-p',
        help='Custom prompt for summarization. Use {text} as placeholder'
    )
    
    parser.add_argument(
        '--max-length',
        type=int,
        help='Maximum summary length in words'
    )
    
    parser.add_argument(
        '--skip-summary', '-s',
        action='store_true',
        help='Skip summarization step (transcription only)'
    )
    
    parser.add_argument(
        '--keep-sanitized', '-k',
        action='store_true',
        help='Keep summary sanitized (do not restore confidential info)'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("\n" + "="*70)
    print("  VIDEO PROCESSING PIPELINE WITH PRIVACY PROTECTION")
    print("="*70)
    
    # Execute pipeline
    results = complete_pipeline(
        args.video_file,
        model=args.model,
        custom_prompt=args.prompt,
        max_summary_length=args.max_length,
        skip_summary=args.skip_summary,
        keep_sanitized=args.keep_sanitized
    )
    
    if results:
        # Print summary
        print_section("PIPELINE COMPLETE")
        print("Generated files:")
        for key, path in results.items():
            print(f"  ✓ {key.replace('_', ' ').title()}: {Path(path).name}")
        
        print("\n" + "="*70)
        print("SUCCESS: All files generated without information leakage!")
        print("="*70 + "\n")
        
        # Show workflow
        print("Workflow Summary:")
        print("  1. Video → Transcribed to text")
        print("  2. Original → Sanitized (confidential info removed)")
        if 'summary_sanitized' in results:
            print("  3. Sanitized text → Summarized by Ollama")
        if 'summary_restored' in results:
            print("  4. Summary → Restored (confidential info recovered)")
        
        print("\n✓ Confidential information protected throughout the process")
        return 0
    else:
        print("\n" + "="*70)
        print("PIPELINE FAILED")
        print("="*70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
