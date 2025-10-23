# 🔄 Reverse Sanitization Guide

## Overview

The reverse sanitization feature allows authorized users to restore sanitized transcriptions back to their original form, recovering the confidential information that was previously replaced.

## How It Works

```
Original Text          →  Sanitization   →  Sanitized Text
"Anh chị học KT"          (Forward)         "AC học KT"
                                                    ↓
                                           Reverse Sanitization
                                                    ↓
Restored Text          ←  Restoration    ←  Sanitized Text
"Anh chị học KT"          (Backward)        "AC học KT"
```

## Process Flow

### 1. Forward Process (Sanitization)
```bash
python main.py video.mp4
```
**Creates:**
- `video.txt` (original)
- `video_sanitized.txt` (confidential info replaced)

### 2. Reverse Process (Restoration)
```bash
python reverse_sanitize.py video_sanitized.txt
```
**Creates:**
- `video_restored.txt` (confidential info restored)

## Usage Examples

### Basic Usage
```bash
# Restore a sanitized file
python reverse_sanitize.py meeting_sanitized.txt

# Output: meeting_restored.txt
```

### Custom Output Path
```bash
# Specify where to save restored file
python reverse_sanitize.py meeting_sanitized.txt -o confidential_original.txt
```

### Help Information
```bash
# Show all options
python reverse_sanitize.py --help
```

## Complete Example

### Step 1: Create Original Transcription
```bash
python main.py presentation.mp4
```
**Output:**
- `presentation.txt` - Original with confidential info
- `presentation_sanitized.txt` - Safe to share

### Step 2: Share Sanitized Version
Share `presentation_sanitized.txt` with team members who don't need access to confidential information.

### Step 3: Restore When Needed
```bash
python reverse_sanitize.py presentation_sanitized.txt
```
**Output:**
- `presentation_restored.txt` - Confidential info restored

### Step 4: Verify Restoration
```bash
python test_reverse_sanitization.py
```
Shows the complete cycle: Original → Sanitized → Restored

## Mapping Table

The restoration uses the same configuration from `confidential_terms.py`:

| Code | ← Restores To → | Original Term |
|------|-----------------|---------------|
| AC   | ←              | Anh chị       |
| KT   | ←              | Kiến thức     |

## Testing

### Test with Sample Data
```bash
python test_reverse_sanitization.py
```

**Shows:**
1. Original text
2. Sanitized version
3. Restored version
4. Verification (matches or differences)
5. Complete mapping table

### Expected Output
```
STEP 1: ORIGINAL TEXT
    Xin chào Anh chị,
    Hôm nay chúng ta sẽ học về Kiến thức mới.

STEP 2: SANITIZED TEXT
    Xin chào AC,
    Hôm nay chúng ta sẽ học về KT mới.

STEP 3: RESTORED TEXT
    Xin chào Anh chị,
    Hôm nay chúng ta sẽ học về Kiến thức mới.

✓ SUCCESS: Restored text matches original!
```

## Important Notes

### ⚠️ Security Considerations

1. **Access Control**
   - Only authorized personnel should use reverse sanitization
   - Keep restored files secure
   - Don't share restored files publicly

2. **File Management**
   - Restored files contain confidential information
   - Store in secure locations
   - Delete after use if no longer needed

3. **Audit Trail**
   - Track who restores sanitized files
   - Document reasons for restoration
   - Follow your organization's security policies

### 📝 Case Sensitivity Note

The restoration process may differ in case from the original:
- **Original**: "anh chị" (lowercase)
- **Sanitized**: "AC"
- **Restored**: "Anh chị" (title case - using first pattern from config)

This is expected behavior and doesn't affect meaning.

## Configuration

### Current Mappings

Edit `confidential_terms.py` to modify mappings:

```python
CONFIDENTIAL_TERMS = {
    r'Anh chị': 'AC',     # Forward: Anh chị → AC
    r'anh chị': 'AC',     # Reverse: AC → Anh chị (first match)
    r'Kiến thức': 'KT',   # Forward: Kiến thức → KT
    r'kiến thức': 'KT',   # Reverse: KT → Kiến thức (first match)
}
```

### Adding New Terms

When adding terms, ensure they can be reversed:

```python
CONFIDENTIAL_TERMS = {
    # Good - unique code
    r'Secret Name': 'SN',
    
    # Bad - ambiguous code (avoid)
    r'Secret Name': 'S',
    r'Super New': 'S',  # Same code causes conflicts!
}
```

## File Naming Convention

| Original File | Sanitized File | Restored File |
|--------------|----------------|---------------|
| `video.txt` | `video_sanitized.txt` | `video_restored.txt` |
| `meeting.txt` | `meeting_sanitized.txt` | `meeting_restored.txt` |

## Best Practices

### ✅ DO

- Test restoration with `test_reverse_sanitization.py` before production use
- Keep `confidential_terms.py` consistent during sanitization and restoration
- Use unique codes for each confidential term
- Document when and why you restore files
- Secure restored files immediately after creation

### ❌ DON'T

- Share restored files with unauthorized personnel
- Use the same code for multiple different terms
- Restore files on shared/public computers
- Leave restored files in unsecured locations
- Forget to verify restoration accuracy

## Troubleshooting

### Issue: Restoration Doesn't Match Original

**Cause**: Case sensitivity differences

**Solution**: This is expected. The restored text uses the first matching pattern from the configuration.

### Issue: Some Terms Not Restored

**Cause**: 
1. Term not in `confidential_terms.py`
2. Different configuration used during sanitization

**Solution**: 
1. Verify `confidential_terms.py` contains all terms
2. Use the same configuration file that was used during sanitization

### Issue: Code Conflicts

**Cause**: Multiple terms map to the same code

**Example:**
```python
CONFIDENTIAL_TERMS = {
    r'Term A': 'TA',
    r'Term Alpha': 'TA',  # Conflict!
}
```

**Solution**: Use unique codes for each term:
```python
CONFIDENTIAL_TERMS = {
    r'Term A': 'TA',
    r'Term Alpha': 'TAL',  # Unique code
}
```

## Integration Workflow

### For Teams

1. **Content Creator** (has access to confidential info):
   ```bash
   python main.py presentation.mp4
   # Share: presentation_sanitized.txt
   ```

2. **Team Members** (work with sanitized version):
   - Receive: `presentation_sanitized.txt`
   - Review, edit, analyze safely

3. **Authorized Reviewer** (needs to verify original):
   ```bash
   python reverse_sanitize.py presentation_sanitized.txt
   # Review: presentation_restored.txt
   # Delete after verification
   ```

## Command Reference

### Reverse Sanitization
```bash
# Basic restoration
python reverse_sanitize.py <sanitized_file>

# Custom output
python reverse_sanitize.py <sanitized_file> -o <output_file>

# Help
python reverse_sanitize.py --help
```

### Testing
```bash
# Test forward and reverse process
python test_reverse_sanitization.py

# Test only forward (sanitization)
python test_sanitization.py
```

## FAQ

**Q: Can I restore a file multiple times?**
A: Yes, restoration is repeatable and produces the same result.

**Q: Will restoration work if I change confidential_terms.py?**
A: Only if the same mappings exist. Use the original configuration for accurate restoration.

**Q: Is the restoration process reversible?**
A: Yes, you can sanitize a restored file again to get back to the sanitized version.

**Q: What happens to terms not in the configuration?**
A: They remain unchanged. Only configured codes are restored.

**Q: Can I automate restoration?**
A: Yes, the script returns exit code 0 on success, 1 on failure for automation.

---

**Remember: Restored files contain confidential information. Handle with appropriate security measures!** 🔒
