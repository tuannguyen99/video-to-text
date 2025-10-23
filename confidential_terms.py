"""
Configuration file for confidential terms and their replacements.

Add or modify terms here to customize what information gets sanitized.
The matching is case-insensitive by default.
"""

# Dictionary of confidential terms and their replacements
# Key: Original term (regex pattern)
# Value: Replacement text
CONFIDENTIAL_TERMS = {
    # Vietnamese terms
    r'Anh chị': 'AC',
    r'anh chị': 'AC',
    r'Kiến thức': 'KT',
    r'kiến thức': 'KT',
    
    # Add more terms here as needed
    # Example:
    # r'Company Name': 'COMPANY',
    # r'Secret Project': 'PROJECT',
    # r'\d{3}-\d{3}-\d{4}': 'XXX-XXX-XXXX',  # Phone numbers
    # r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': '[EMAIL]',  # Email addresses
}

# Additional regex patterns for more complex matching
# These will be applied in order
ADVANCED_PATTERNS = [
    # Example: Replace all numbers with [NUMBER]
    # (r'\b\d+\b', '[NUMBER]'),
    
    # Example: Replace email addresses
    # (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
    
    # Example: Replace phone numbers (Vietnamese format)
    # (r'\b0\d{9}\b', '[PHONE]'),
]
