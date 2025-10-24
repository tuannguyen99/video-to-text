#!/usr/bin/env python3
"""
Reverse Sanitization Script

This script converts sanitized transcriptions back to their original form.
Use this tool when you need to restore confidential information from sanitized files.

Usage:
    python reverse_sanitize.py <sanitized_file.txt>

Example:
    python reverse_sanitize.py video_sanitized.txt
"""

import sys
import os
import argparse
import re
from pathlib import Path

# Import confidential terms configuration
try:
    from confidential_terms import CONFIDENTIAL_TERMS, ADVANCED_PATTERNS
except ImportError:
    # Fallback to default terms if config file not found
    CONFIDENTIAL_TERMS = {
        r'Anh chị': 'AC',
        r'anh chị': 'AC',
        r'Kiến thức': 'KT',
        r'kiến thức': 'KT',
    }
    ADVANCED_PATTERNS = []


def create_reverse_mapping():
    """
    Create a reverse mapping from sanitized codes back to original terms.
    
    Returns:
        dict: Mapping of sanitized codes to original terms
    """
    reverse_map = {}
    
    # Create reverse mapping from CONFIDENTIAL_TERMS
    for original_pattern, replacement_code in CONFIDENTIAL_TERMS.items():
        # Remove regex characters to get the actual term
        original_term = original_pattern.replace(r'\b', '').strip()
        
        # Store the replacement code as key and original as value
        # Use the first occurrence if there are duplicates
        if replacement_code not in reverse_map:
            reverse_map[replacement_code] = original_term
    
    return reverse_map


def reverse_sanitize_text(sanitized_text):
    """
    Convert sanitized text back to original form.
    
    Args:
        sanitized_text (str): Sanitized text with replaced terms
    
    Returns:
        str: Text with original confidential information restored
    """
    restored_text = sanitized_text
    
    # Get reverse mapping
    reverse_map = create_reverse_mapping()
    
    # Apply reverse replacements
    for code, original_term in reverse_map.items():
        # Use word boundaries to avoid partial replacements
        pattern = r'\b' + re.escape(code) + r'\b'
        restored_text = re.sub(pattern, original_term, restored_text)
    
    return restored_text


def process_sanitized_file(sanitized_file_path, output_path=None):
    """
    Read a sanitized file and restore it to original form.
    
    Args:
        sanitized_file_path (str): Path to the sanitized text file
        output_path (str, optional): Path for restored text file. If None, uses original naming
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if input file exists
        if not os.path.exists(sanitized_file_path):
            print(f"Error: File '{sanitized_file_path}' not found.")
            return False
        
        # Read sanitized text
        with open(sanitized_file_path, 'r', encoding='utf-8') as f:
            sanitized_text = f.read()
        
        # Restore to original
        restored_text = reverse_sanitize_text(sanitized_text)
        
        # Determine output path
        if output_path is None:
            # Remove _sanitized suffix and add _restored
            base_name = Path(sanitized_file_path).stem
            extension = Path(sanitized_file_path).suffix
            
            if base_name.endswith('_sanitized'):
                base_name = base_name.replace('_sanitized', '')
            
            output_path = f"{base_name}_restored{extension}"
        
        # Save restored text
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(restored_text)
        
        print(f"✓ Input file: {sanitized_file_path}")
        print(f"✓ Output file: {output_path}")
        print(f"✓ Restoration completed successfully!")
        
        # Show what was restored
        reverse_map = create_reverse_mapping()
        if reverse_map:
            print(f"\n📝 Restored terms:")
            for code, original in reverse_map.items():
                print(f"   {code} → {original}")
        
        return True
        
    except Exception as e:
        print(f"Error during restoration: {str(e)}")
        return False


def main():
    """Main function to handle command line arguments and run restoration."""
    parser = argparse.ArgumentParser(
        description="Restore sanitized transcriptions to original form",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python reverse_sanitize.py video_sanitized.txt
    python reverse_sanitize.py video_sanitized.txt -o original.txt
    
Note: This tool uses the same confidential_terms.py configuration.
Make sure it contains the same terms used during sanitization.
        """
    )
    
    parser.add_argument(
        "sanitized_file",
        help="Path to the sanitized text file"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: filename_restored.txt)",
        default=None
    )
    
    # Parse arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # Process the file
    success = process_sanitized_file(args.sanitized_file, args.output)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
