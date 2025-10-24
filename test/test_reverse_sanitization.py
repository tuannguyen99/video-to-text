#!/usr/bin/env python3
"""
Test script to demonstrate the reverse sanitization feature.
Shows: Original → Sanitized → Restored
"""

import re
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from confidential_terms import CONFIDENTIAL_TERMS, ADVANCED_PATTERNS


def sanitize_text(text):
    """Sanitize text (forward direction)."""
    sanitized_text = text
    
    for pattern, replacement in CONFIDENTIAL_TERMS.items():
        sanitized_text = re.sub(pattern, replacement, sanitized_text, flags=re.IGNORECASE)
    
    for pattern, replacement in ADVANCED_PATTERNS:
        sanitized_text = re.sub(pattern, replacement, sanitized_text)
    
    return sanitized_text


def create_reverse_mapping():
    """Create reverse mapping."""
    reverse_map = {}
    
    for original_pattern, replacement_code in CONFIDENTIAL_TERMS.items():
        original_term = original_pattern.replace(r'\b', '').strip()
        if replacement_code not in reverse_map:
            reverse_map[replacement_code] = original_term
    
    return reverse_map


def reverse_sanitize_text(sanitized_text):
    """Restore sanitized text (reverse direction)."""
    restored_text = sanitized_text
    reverse_map = create_reverse_mapping()
    
    for code, original_term in reverse_map.items():
        pattern = r'\b' + re.escape(code) + r'\b'
        restored_text = re.sub(pattern, original_term, restored_text)
    
    return restored_text


if __name__ == "__main__":
    # Example text
    original_text = """
    Xin chào Anh chị,
    
    Hôm nay chúng ta sẽ học về Kiến thức mới.
    Anh chị vui lòng chú ý đến kiến thức này.
    Đây là một phần kiến thức quan trọng.
    
    Cảm ơn anh chị đã theo dõi!
    """
    
    # Forward: Original → Sanitized
    sanitized_text = sanitize_text(original_text)
    
    # Reverse: Sanitized → Restored
    restored_text = reverse_sanitize_text(sanitized_text)
    
    # Display results
    print("=" * 70)
    print("STEP 1: ORIGINAL TEXT")
    print("=" * 70)
    print(original_text)
    
    print("\n" + "=" * 70)
    print("STEP 2: SANITIZED TEXT (Confidential info replaced)")
    print("=" * 70)
    print(sanitized_text)
    
    print("\n" + "=" * 70)
    print("STEP 3: RESTORED TEXT (Back to original)")
    print("=" * 70)
    print(restored_text)
    
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    
    # Check if restoration is accurate
    if original_text.strip() == restored_text.strip():
        print("✓ SUCCESS: Restored text matches original!")
    else:
        print("✗ WARNING: Restored text differs from original")
        print("\nDifferences:")
        original_lines = original_text.strip().split('\n')
        restored_lines = restored_text.strip().split('\n')
        for i, (orig, rest) in enumerate(zip(original_lines, restored_lines)):
            if orig != rest:
                print(f"  Line {i+1}:")
                print(f"    Original: {orig}")
                print(f"    Restored: {rest}")
    
    print("\n" + "=" * 70)
    print("MAPPING TABLE")
    print("=" * 70)
    reverse_map = create_reverse_mapping()
    print(f"{'Code':<15} {'→':<5} {'Original Term':<20}")
    print("-" * 70)
    for code, original in reverse_map.items():
        print(f"{code:<15} {'→':<5} {original:<20}")
