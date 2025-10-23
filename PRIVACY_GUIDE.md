# Privacy Protection - Quick Reference

## How It Works

When you transcribe a video, the script automatically creates TWO files:

1. **`video_name.txt`** - Original transcription (with confidential info)
2. **`video_name_sanitized.txt`** - Safe version (confidential info replaced)

## Default Protected Terms

| Original Vietnamese | Replacement Code |
|---------------------|------------------|
| Anh chị             | AC               |
| Kiến thức           | KT               |

## Adding Your Own Terms

Edit `confidential_terms.py`:

```python
CONFIDENTIAL_TERMS = {
    r'Your Secret': 'SECRET',
    r'Private Info': 'PRIVATE',
}
```

## Advanced Protection Examples

### Protect Phone Numbers
```python
ADVANCED_PATTERNS = [
    (r'\b0\d{9}\b', '[PHONE]'),  # Vietnamese format
]
```

### Protect Email Addresses
```python
ADVANCED_PATTERNS = [
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
]
```

### Protect ID Numbers
```python
ADVANCED_PATTERNS = [
    (r'\b\d{9}\b', '[ID]'),  # 9-digit IDs
    (r'\b\d{12}\b', '[CCCD]'),  # 12-digit citizen IDs
]
```

## Testing Your Patterns

Run the test script:
```bash
python test_sanitization.py
```

## Usage

### Forward Process (Sanitize)
```bash
# Normal use (creates both files)
python main.py video.mp4

# Only create original (no sanitization)
python main.py video.mp4 --no-sanitize
```

### Reverse Process (Restore)
```bash
# Restore sanitized file to original
python reverse_sanitize.py video_sanitized.txt

# Specify custom output
python reverse_sanitize.py video_sanitized.txt -o original.txt
```

**Output:** Creates `video_restored.txt` with confidential information restored.

## Best Practices

✅ **DO:**
- Share the `*_sanitized.txt` file with others
- Keep the original `.txt` file private
- Test your patterns with `test_sanitization.py`
- Add terms specific to your domain

❌ **DON'T:**
- Share the original `.txt` file publicly
- Forget to update `confidential_terms.py` for new projects
- Use overly broad patterns that might replace normal words

## Example Workflow

### Standard Workflow (with sanitization)
1. Transcribe video: `python main.py meeting.mp4`
2. Check both outputs:
   - `meeting.txt` (original - keep private)
   - `meeting_sanitized.txt` (safe - can share)
3. Share only the sanitized version
4. Add new terms to `confidential_terms.py` as needed

### Restoration Workflow (when needed)
1. Receive sanitized file: `meeting_sanitized.txt`
2. Restore to original: `python reverse_sanitize.py meeting_sanitized.txt`
3. Get restored output: `meeting_restored.txt`
4. Keep restored file secure (contains confidential info)

⚠️ **Security Note**: Only restore sanitized files when you have authorization to access the original confidential information.

## Tips

- Use regex for flexible matching
- Case-insensitive by default for CONFIDENTIAL_TERMS
- Test with sample text before processing important videos
- Keep a backup of your `confidential_terms.py` configuration
