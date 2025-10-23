#!/usr/bin/env python3
"""
Ollama Summarization Script

This script takes sanitized transcriptions and uses Ollama to generate summaries.
The summary is then reverse-sanitized to restore confidential information.

Usage:
    python summarize_with_ollama.py <sanitized_file.txt>

Example:
    python summarize_with_ollama.py video_sanitized.txt

Requirements:
    - Ollama must be installed and running locally
    - Default model: llama3.2 (can be changed with --model)
"""

import sys
import os
import argparse
import json
from pathlib import Path

try:
    import ollama
except ImportError:
    print("Error: ollama package not found.")
    print("Install it with: pip install ollama")
    sys.exit(1)

# Import reverse sanitization function
try:
    from reverse_sanitize import reverse_sanitize_text, create_reverse_mapping
except ImportError:
    print("Error: reverse_sanitize.py not found in the current directory")
    sys.exit(1)


def check_ollama_service():
    """
    Check if Ollama service is running and accessible.
    
    Returns:
        bool: True if Ollama is running, False otherwise
    """
    try:
        # Try to list available models
        ollama.list()
        return True
    except Exception as e:
        print(f"Error: Cannot connect to Ollama service: {e}")
        print("\nPlease ensure Ollama is installed and running:")
        print("1. Install: https://ollama.ai/download")
        print("2. Start service: ollama serve")
        print("3. Pull a model: ollama pull llama3.2")
        return False


def check_model_available(model_name):
    """
    Check if a specific model is available in Ollama.
    
    Args:
        model_name: Name of the model to check
        
    Returns:
        bool: True if model is available, False otherwise
    """
    try:
        response = ollama.list()
        # ollama.list() returns ListResponse object with models attribute
        available_models = [model.model for model in response.models]
        
        # Check for exact match or partial match (e.g., llama3.2:latest)
        for available in available_models:
            if model_name in available or available.startswith(model_name):
                return True
        
        print(f"\nModel '{model_name}' not found.")
        print("Available models:")
        for model in available_models:
            print(f"  - {model}")
        print(f"\nTo download the model, run: ollama pull {model_name}")
        return False
    except Exception as e:
        print(f"Error checking model availability: {e}")
        return False


def summarize_text(text, model="llama3.2", custom_prompt=None, max_length=None):
    """
    Summarize text using Ollama.
    
    Args:
        text: Text to summarize (sanitized)
        model: Ollama model to use
        custom_prompt: Optional custom prompt for summarization
        max_length: Optional maximum length for summary
        
    Returns:
        str: Summary of the text
    """
    # Build the prompt
    if custom_prompt:
        prompt = custom_prompt.replace("{text}", text)
    else:
        prompt = f"""Please provide a concise summary of the following text.
Focus on the main points and key information.
{'Keep the summary under ' + str(max_length) + ' words.' if max_length else ''}

Text to summarize:
{text}

Summary:"""

    print(f"Generating summary using {model}...")
    print("This may take a moment...")
    
    try:
        # Call Ollama API
        response = ollama.generate(
            model=model,
            prompt=prompt,
            stream=False
        )
        
        summary = response['response'].strip()
        return summary
        
    except Exception as e:
        print(f"Error during summarization: {e}")
        return None


def process_file(
    input_file, 
    model="llama3.2", 
    custom_prompt=None, 
    max_length=None,
    keep_sanitized=False
):
    """
    Process a sanitized file: summarize and optionally restore confidential info.
    
    Args:
        input_file: Path to sanitized transcript file
        model: Ollama model to use
        custom_prompt: Optional custom prompt
        max_length: Optional maximum summary length
        keep_sanitized: If True, don't reverse sanitization
        
    Returns:
        tuple: (sanitized_summary_path, restored_summary_path or None)
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: File not found: {input_file}")
        return None, None
    
    # Read sanitized text
    print(f"Reading: {input_path.name}")
    with open(input_path, 'r', encoding='utf-8') as f:
        sanitized_text = f.read()
    
    print(f"Text length: {len(sanitized_text)} characters")
    
    # Summarize the sanitized text
    summary = summarize_text(sanitized_text, model, custom_prompt, max_length)
    
    if summary is None:
        print("Failed to generate summary")
        return None, None
    
    print(f"Summary generated: {len(summary)} characters")
    
    # Save sanitized summary
    base_name = input_path.stem
    # Remove _sanitized suffix if present
    if base_name.endswith('_sanitized'):
        base_name = base_name[:-10]
    
    sanitized_summary_path = input_path.parent / f"{base_name}_summary_sanitized.txt"
    
    with open(sanitized_summary_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    print(f"✓ Sanitized summary saved: {sanitized_summary_path.name}")
    
    # Restore confidential information if requested
    restored_summary_path = None
    if not keep_sanitized:
        print("\nRestoring confidential information...")
        restored_summary = reverse_sanitize_text(summary)
        
        restored_summary_path = input_path.parent / f"{base_name}_summary_restored.txt"
        
        with open(restored_summary_path, 'w', encoding='utf-8') as f:
            f.write(restored_summary)
        print(f"✓ Restored summary saved: {restored_summary_path.name}")
    
    return str(sanitized_summary_path), str(restored_summary_path) if restored_summary_path else None


def main():
    parser = argparse.ArgumentParser(
        description="Summarize sanitized transcripts using Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with default model (llama3.2)
  python summarize_with_ollama.py video_sanitized.txt
  
  # Use a different model
  python summarize_with_ollama.py video_sanitized.txt --model llama2
  
  # Keep summary sanitized (don't restore)
  python summarize_with_ollama.py video_sanitized.txt --keep-sanitized
  
  # Set maximum summary length
  python summarize_with_ollama.py video_sanitized.txt --max-length 200
  
  # Use custom prompt
  python summarize_with_ollama.py video_sanitized.txt --prompt "Summarize in 3 bullet points: {text}"
"""
    )
    
    parser.add_argument(
        'input_file',
        help='Path to sanitized transcript file'
    )
    
    parser.add_argument(
        '--model', '-m',
        default='llama3.2',
        help='Ollama model to use (default: llama3.2)'
    )
    
    parser.add_argument(
        '--prompt', '-p',
        help='Custom prompt for summarization. Use {text} as placeholder for the input text'
    )
    
    parser.add_argument(
        '--max-length',
        type=int,
        help='Maximum length of summary in words'
    )
    
    parser.add_argument(
        '--keep-sanitized', '-k',
        action='store_true',
        help='Keep summary sanitized (do not restore confidential info)'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check Ollama service and available models, then exit'
    )
    
    args = parser.parse_args()
    
    # Check Ollama service
    if not check_ollama_service():
        sys.exit(1)
    
    # If --check flag, just show info and exit
    if args.check:
        print("\n✓ Ollama service is running")
        check_model_available(args.model)
        sys.exit(0)
    
    # Check if model is available
    if not check_model_available(args.model):
        sys.exit(1)
    
    # Process the file
    print("\n" + "="*60)
    print("OLLAMA SUMMARIZATION PIPELINE")
    print("="*60 + "\n")
    
    sanitized_path, restored_path = process_file(
        args.input_file,
        model=args.model,
        custom_prompt=args.prompt,
        max_length=args.max_length,
        keep_sanitized=args.keep_sanitized
    )
    
    if sanitized_path:
        print("\n" + "="*60)
        print("SUMMARY COMPLETE")
        print("="*60)
        print(f"\n✓ Sanitized summary: {Path(sanitized_path).name}")
        if restored_path:
            print(f"✓ Restored summary: {Path(restored_path).name}")
        print("\nSummary pipeline completed successfully!")
        return 0
    else:
        print("\nSummarization failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
