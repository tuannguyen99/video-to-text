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
    from translate_with_ollama import translate_text
    from reverse_sanitize import reverse_sanitize_text, create_reverse_mapping
except ImportError:
    print("Error: Required modules (summarize_with_ollama.py, translate_with_ollama.py or reverse_sanitize.py) not found")
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
    keep_sanitized=False,
    translate_to=None,
    translate_source=None
):
    """
    Execute the complete video processing pipeline.
    
    Args:
        video_path: Path to input video file
        model: Ollama model for summarization/translation
        custom_prompt: Custom prompt for Ollama
        max_summary_length: Maximum summary length in words
        skip_summary: Skip summarization step
        keep_sanitized: Keep summary/translation sanitized
        translate_to: Target language for translation (None = no translation)
        translate_source: Source language for translation
        
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
                    step_num = 4 if translate_to else 3
                    print_section(f"STEP {step_num}: RESTORE CONFIDENTIAL INFORMATION (Summary)")
                    
                    restored_summary = reverse_sanitize_text(summary)
                    
                    summary_restored_path = video_path.parent / f"{base_name}_summary_restored.txt"
                    
                    with open(summary_restored_path, 'w', encoding='utf-8') as f:
                        f.write(restored_summary)
                    
                    results['summary_restored'] = str(summary_restored_path)
                    print(f"✓ Restored summary: {summary_restored_path.name}")
                    print(f"  Confidential information restored")
                
        except Exception as e:
            print(f"Error during summarization: {e}")
            skip_summary = True
    
    # STEP 4 (or 3): Translate sanitized text
    if translate_to:
        step_num = 4 if not skip_summary else 3
        print_section(f"STEP {step_num}: OLLAMA TRANSLATION")
        
        # Check Ollama (if not already checked)
        if skip_summary and not check_ollama_service():
            print("Warning: Ollama not available, skipping translation")
            translate_to = None
        elif skip_summary and not check_model_available(model):
            print(f"Warning: Model {model} not available, skipping translation")
            translate_to = None
    
    if translate_to:
        try:
            # Read sanitized text
            with open(sanitized_txt, 'r', encoding='utf-8') as f:
                sanitized_content = f.read()
            
            print(f"Input: {Path(sanitized_txt).name}")
            print(f"Target language: {translate_to}")
            if translate_source:
                print(f"Source language: {translate_source}")
            print(f"Model: {model}")
            
            # Generate translation
            translation = translate_text(
                sanitized_content,
                target_language=translate_to,
                model=model,
                source_language=translate_source
            )
            
            if translation is None:
                print("Warning: Translation failed")
            else:
                # Save sanitized translation
                base_name = video_path.stem
                safe_lang = translate_to.lower().replace(' ', '_')
                translation_sanitized_path = video_path.parent / f"{base_name}_translation_{safe_lang}_sanitized.txt"
                
                with open(translation_sanitized_path, 'w', encoding='utf-8') as f:
                    f.write(translation)
                
                results['translation_sanitized'] = str(translation_sanitized_path)
                print(f"\n✓ Sanitized translation: {translation_sanitized_path.name}")
                print(f"  Length: {len(translation)} characters")
                
                # Restore confidential information
                if not keep_sanitized:
                    if not skip_summary:
                        print_section(f"STEP 5: RESTORE CONFIDENTIAL INFORMATION (Translation)")
                    restored_translation = reverse_sanitize_text(translation)
                    
                    translation_restored_path = video_path.parent / f"{base_name}_translation_{safe_lang}_restored.txt"
                    
                    with open(translation_restored_path, 'w', encoding='utf-8') as f:
                        f.write(restored_translation)
                    
                    results['translation_restored'] = str(translation_restored_path)
                    print(f"✓ Restored translation: {translation_restored_path.name}")
                    print(f"  Confidential information restored")
                
        except Exception as e:
            print(f"Error during translation: {e}")
            import traceback
            traceback.print_exc()
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Complete video processing pipeline with privacy protection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Complete Workflow:
  1. Transcribe video → Creates original.txt and sanitized.txt
  2. Summarize sanitized text using Ollama → Creates summary_sanitized.txt
  3. Translate sanitized text using Ollama → Creates translation_sanitized.txt
  4. Restore confidential info → Creates summary_restored.txt and translation_restored.txt

Examples:
  # Full pipeline with defaults
  python process_video_complete.py presentation.mp4
  
  # Use different Ollama model
  python process_video_complete.py meeting.mkv --model llama2
  
  # Skip summarization (only transcribe)
  python process_video_complete.py video.mp4 --skip-summary
  
  # Translate to English (restored version will have Vietnamese terms in English text)
  python process_video_complete.py video.mp4 --translate English
  
  # Keep translation sanitized (codes like AC, KT remain - safe to share)
  python process_video_complete.py video.mp4 --translate English --keep-sanitized
  
  # Translate with source language specified
  python process_video_complete.py video.mp4 --translate English --source-lang Vietnamese
  
  # Summarize AND translate
  python process_video_complete.py video.mp4 --translate Japanese --max-length 200
  
  # Keep summary/translation sanitized (don't restore)
  python process_video_complete.py video.mp4 --translate English --keep-sanitized
  
  # Custom summary length
  python process_video_complete.py video.mp4 --max-length 150

Output Files:
  - {video}.txt                              Original transcription
  - {video}_sanitized.txt                    Sanitized transcription
  - {video}_summary_sanitized.txt            Sanitized summary
  - {video}_summary_restored.txt             Restored summary (with confidential info)
  - {video}_translation_{lang}_sanitized.txt Sanitized translation (codes: AC, KT)
  - {video}_translation_{lang}_restored.txt  Restored translation (original terms: Anh chị, Kiến thức)

Note on Translation Restoration:
  By default, confidential terms are restored to their ORIGINAL language (Vietnamese) 
  in the translated text. This means:
  
  Example: "Hello AC, learning new KT" → "Hello Anh chị, learning new Kiến thức"
  
  If you want to keep codes (AC, KT) in translation for sharing, use --keep-sanitized flag.
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
        help='Keep summary/translation sanitized (do not restore confidential info)'
    )
    
    parser.add_argument(
        '--translate', '-t',
        dest='translate_to',
        help='Translate to target language (e.g., English, Japanese, Chinese, Spanish)'
    )
    
    parser.add_argument(
        '--source-lang',
        help='Source language for translation (optional, auto-detect if not specified)'
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
        keep_sanitized=args.keep_sanitized,
        translate_to=args.translate_to,
        translate_source=args.source_lang
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
        if 'translation_sanitized' in results:
            print(f"  {len([k for k in results if 'summary' in k]) + 3}. Sanitized text → Translated by Ollama")
        if 'translation_restored' in results:
            print(f"  {len([k for k in results if 'summary' in k or 'translation_sanitized' in k]) + 3}. Translation → Restored (confidential info recovered)")
        
        print("\n✓ Confidential information protected throughout the process")
        return 0
    else:
        print("\n" + "="*70)
        print("PIPELINE FAILED")
        print("="*70 + "\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
