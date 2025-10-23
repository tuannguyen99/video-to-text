#!/usr/bin/env python3
"""
Ollama Translation Script

This script takes sanitized transcriptions and uses Ollama to translate them.
The translation is then reverse-sanitized to restore confidential information.

Usage:
    python translate_with_ollama.py <sanitized_file.txt> --target-lang <language>

Example:
    python translate_with_ollama.py video_sanitized.txt --target-lang English
    python translate_with_ollama.py video_sanitized.txt --target-lang Japanese

Requirements:
    - Ollama must be installed and running locally
    - Default model: llama3.2 (can be changed with --model)
"""

import sys
import os
import argparse
from pathlib import Path

try:
    import ollama
except ImportError:
    print("Error: ollama package not found.")
    print("Install it with: pip install ollama")
    sys.exit(1)

# Import reverse sanitization function
try:
    from reverse_sanitize import reverse_sanitize_text
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
        ollama.list()
        return True
    except Exception as e:
        print(f"Error: Cannot connect to Ollama service: {e}")
        print("\nPlease ensure Ollama is installed and running:")
        print("1. Install: https://ollama.com/download")
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


def translate_text(text, target_language, model="llama3.2", custom_prompt=None, source_language=None):
    """
    Translate text using Ollama.
    
    Args:
        text: Text to translate (sanitized)
        target_language: Target language for translation
        model: Ollama model to use
        custom_prompt: Optional custom prompt for translation
        source_language: Optional source language (auto-detect if None)
        
    Returns:
        str: Translated text
    """
    # Build the prompt
    if custom_prompt:
        prompt = custom_prompt.replace("{text}", text).replace("{target_lang}", target_language)
        if source_language:
            prompt = prompt.replace("{source_lang}", source_language)
    else:
        if source_language:
            prompt = f"""Translate the following text from {source_language} to {target_language}.
Maintain the original meaning and tone. Keep any abbreviations or codes (like AC, KT) unchanged.

Text to translate:
{text}

Translation in {target_language}:"""
        else:
            prompt = f"""Translate the following text to {target_language}.
Maintain the original meaning and tone. Keep any abbreviations or codes (like AC, KT) unchanged.

Text to translate:
{text}

Translation in {target_language}:"""

    print(f"Translating to {target_language} using {model}...")
    print("This may take a moment...")
    
    try:
        response = ollama.generate(
            model=model,
            prompt=prompt,
            stream=False
        )
        
        translation = response['response'].strip()
        return translation
        
    except Exception as e:
        print(f"Error during translation: {e}")
        return None


def process_file(
    input_file,
    target_language,
    model="llama3.2",
    custom_prompt=None,
    source_language=None,
    keep_sanitized=False
):
    """
    Process a sanitized file: translate and optionally restore confidential info.
    
    Args:
        input_file: Path to sanitized transcript file
        target_language: Target language for translation
        model: Ollama model to use
        custom_prompt: Optional custom prompt
        source_language: Optional source language
        keep_sanitized: If True, don't reverse sanitization
        
    Returns:
        tuple: (sanitized_translation_path, restored_translation_path or None)
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
    
    # Translate the sanitized text
    translation = translate_text(
        sanitized_text,
        target_language,
        model,
        custom_prompt,
        source_language
    )
    
    if translation is None:
        print("Failed to generate translation")
        return None, None
    
    print(f"Translation generated: {len(translation)} characters")
    
    # Save sanitized translation
    base_name = input_path.stem
    if base_name.endswith('_sanitized'):
        base_name = base_name[:-10]
    
    # Create safe filename for target language
    safe_lang = target_language.lower().replace(' ', '_')
    sanitized_translation_path = input_path.parent / f"{base_name}_translation_{safe_lang}_sanitized.txt"
    
    with open(sanitized_translation_path, 'w', encoding='utf-8') as f:
        f.write(translation)
    print(f"✓ Sanitized translation saved: {sanitized_translation_path.name}")
    
    # Restore confidential information if requested
    restored_translation_path = None
    if not keep_sanitized:
        print("\nRestoring confidential information...")
        restored_translation = reverse_sanitize_text(translation)
        
        restored_translation_path = input_path.parent / f"{base_name}_translation_{safe_lang}_restored.txt"
        
        with open(restored_translation_path, 'w', encoding='utf-8') as f:
            f.write(restored_translation)
        print(f"✓ Restored translation saved: {restored_translation_path.name}")
    
    return str(sanitized_translation_path), str(restored_translation_path) if restored_translation_path else None


def main():
    parser = argparse.ArgumentParser(
        description="Translate sanitized transcripts using Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Translate Vietnamese to English
  python translate_with_ollama.py video_sanitized.txt --target-lang English
  
  # Translate to Japanese with specific model
  python translate_with_ollama.py video_sanitized.txt --target-lang Japanese --model llama2
  
  # Keep translation sanitized (don't restore)
  python translate_with_ollama.py video_sanitized.txt --target-lang English --keep-sanitized
  
  # Specify source language explicitly
  python translate_with_ollama.py video_sanitized.txt --target-lang English --source-lang Vietnamese
  
  # Use custom prompt
  python translate_with_ollama.py video_sanitized.txt --target-lang English \\
    --prompt "Translate professionally from {source_lang} to {target_lang}: {text}"

Privacy Protection:
  - Ollama receives ONLY sanitized text (confidential terms are replaced with codes)
  - Translation preserves the codes (AC, KT, etc.)
  - Restoration converts codes back to ORIGINAL language terms in the translated text
  - No confidential information is exposed during translation

Important Note:
  Restored translations contain original language terms mixed with target language.
  Example: Vietnamese → English translation
    Original:  "Xin chào Anh chị, học Kiến thức"
    Sanitized: "Xin chào AC, học KT" (sent to Ollama)
    Translated: "Hello AC, learning KT" (from Ollama)
    Restored:  "Hello Anh chị, learning Kiến thức" (Vietnamese terms in English)
  
  Use --keep-sanitized flag if you want codes (AC, KT) to remain in translation.
"""
    )
    
    parser.add_argument(
        'input_file',
        help='Path to sanitized transcript file'
    )
    
    parser.add_argument(
        '--target-lang', '-t',
        required=True,
        help='Target language for translation (e.g., English, Japanese, Chinese, Spanish)'
    )
    
    parser.add_argument(
        '--source-lang', '-s',
        help='Source language (optional, will auto-detect if not specified)'
    )
    
    parser.add_argument(
        '--model', '-m',
        default='llama3.2',
        help='Ollama model to use (default: llama3.2)'
    )
    
    parser.add_argument(
        '--prompt', '-p',
        help='Custom prompt for translation. Use {text}, {target_lang}, {source_lang} as placeholders'
    )
    
    parser.add_argument(
        '--keep-sanitized', '-k',
        action='store_true',
        help='Keep translation sanitized (do not restore confidential info)'
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
    print("OLLAMA TRANSLATION PIPELINE")
    print("="*60 + "\n")
    
    sanitized_path, restored_path = process_file(
        args.input_file,
        target_language=args.target_lang,
        model=args.model,
        custom_prompt=args.prompt,
        source_language=args.source_lang,
        keep_sanitized=args.keep_sanitized
    )
    
    if sanitized_path:
        print("\n" + "="*60)
        print("TRANSLATION COMPLETE")
        print("="*60)
        print(f"\n✓ Sanitized translation: {Path(sanitized_path).name}")
        if restored_path:
            print(f"✓ Restored translation: {Path(restored_path).name}")
        print(f"\nTranslation to {args.target_lang} completed successfully!")
        print("🔒 Confidential information protected during translation")
        return 0
    else:
        print("\nTranslation failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
