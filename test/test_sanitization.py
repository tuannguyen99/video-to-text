#!/usr/bin/env python3
"""
Test script to demonstrate the text sanitization feature.
"""

import re
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from confidential_terms import CONFIDENTIAL_TERMS, ADVANCED_PATTERNS


def sanitize_text(text):
    """
    Replace confidential information in the transcribed text.
    
    Args:
        text (str): Original text to sanitize
    
    Returns:
        str: Sanitized text with confidential information replaced
    """
    sanitized_text = text
    
    # Apply replacements from CONFIDENTIAL_TERMS (case-insensitive)
    for pattern, replacement in CONFIDENTIAL_TERMS.items():
        sanitized_text = re.sub(pattern, replacement, sanitized_text, flags=re.IGNORECASE)
    
    # Apply advanced patterns
    for pattern, replacement in ADVANCED_PATTERNS:
        sanitized_text = re.sub(pattern, replacement, sanitized_text)
    
    return sanitized_text


if __name__ == "__main__":
    # Example text with confidential information
    test_text = """
    Xin chào Anh chị,
    
    Hôm nay chúng ta sẽ học về Kiến thức mới.
    Anh chị vui lòng chú ý.
    Đây là một kiến thức quan trọng.
    
    Cảm ơn anh chị đã theo dõi!
    """
    
    print("=" * 60)
    print("ORIGINAL TEXT:")
    print("=" * 60)
    print(test_text)
    
    print("\n" + "=" * 60)
    print("SANITIZED TEXT:")
    print("=" * 60)
    sanitized = sanitize_text(test_text)
    print(sanitized)
    
    print("\n" + "=" * 60)
    print("REPLACEMENTS APPLIED:")
    print("=" * 60)
    for pattern, replacement in CONFIDENTIAL_TERMS.items():
        print(f"  '{pattern}' → '{replacement}'")
