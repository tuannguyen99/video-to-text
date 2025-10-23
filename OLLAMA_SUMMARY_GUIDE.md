# 🤖 Ollama Summarization Guide

## Overview

This guide explains how to use Ollama to summarize transcribed videos while maintaining privacy protection. The complete workflow ensures that **confidential information never leaves your system** in its original form.

## Complete Workflow

```
Video File
    ↓
[1] Transcribe → Creates original.txt + sanitized.txt
    ↓
[2] Sanitize → Replace "Anh chị" → "AC", "Kiến thức" → "KT"
    ↓
[3] Summarize (Ollama) → LLM processes sanitized text only
    ↓
[4] Restore → Convert "AC" → "Anh chị", "KT" → "Kiến thức"
    ↓
Final Summary (with confidential info restored for authorized users)
```

## Prerequisites

### 1. Install Ollama

Download and install Ollama from: https://ollama.com/download

**Windows:**
```powershell
winget install Ollama.Ollama
```

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

### 2. Start Ollama Service

```bash
ollama serve
```

Leave this running in a terminal.

### 3. Download a Model

```bash
# Recommended: Llama 3.2 (small, fast)
ollama pull llama3.2

# Alternative: Llama 2
ollama pull llama2

# Alternative: Mistral
ollama pull mistral
```

### 4. Verify Installation

```bash
ollama list
```

Should show your downloaded models.

## Usage

### Option 1: Complete Pipeline (Recommended)

Process video → transcribe → sanitize → summarize → restore in one command:

```bash
python process_video_complete.py presentation.mp4
```

**Output files:**
- `presentation.txt` - Original transcription
- `presentation_sanitized.txt` - Safe version (no confidential info)
- `presentation_summary_sanitized.txt` - Summary (sanitized)
- `presentation_summary_restored.txt` - Summary (confidential info restored)

### Option 2: Step-by-Step Workflow

#### Step 1: Transcribe Video

```bash
python main.py presentation.mp4
```

**Creates:**
- `presentation.txt` (original)
- `presentation_sanitized.txt` (confidential info removed)

#### Step 2: Summarize Sanitized Text

```bash
python summarize_with_ollama.py presentation_sanitized.txt
```

**Creates:**
- `presentation_summary_sanitized.txt` (summary with codes)
- `presentation_summary_restored.txt` (summary with confidential info)

## Command Options

### process_video_complete.py

```bash
# Full pipeline with default model (llama3.2)
python process_video_complete.py video.mp4

# Use different model
python process_video_complete.py video.mp4 --model llama2

# Skip summarization (transcription only)
python process_video_complete.py video.mp4 --skip-summary

# Keep summary sanitized (don't restore confidential info)
python process_video_complete.py video.mp4 --keep-sanitized

# Limit summary length
python process_video_complete.py video.mp4 --max-length 200

# Custom prompt
python process_video_complete.py video.mp4 --prompt "Summarize in 3 bullet points: {text}"
```

### summarize_with_ollama.py

```bash
# Basic usage
python summarize_with_ollama.py video_sanitized.txt

# Use different model
python summarize_with_ollama.py video_sanitized.txt --model mistral

# Keep sanitized (don't restore)
python summarize_with_ollama.py video_sanitized.txt --keep-sanitized

# Custom prompt
python summarize_with_ollama.py video_sanitized.txt --prompt "Create a 5-point summary: {text}"

# Check Ollama status
python summarize_with_ollama.py --check
```

## Examples

### Example 1: Meeting Summary

```bash
# Transcribe meeting video
python main.py meeting_2024.mp4

# Get summary with confidential info restored
python summarize_with_ollama.py meeting_2024_sanitized.txt

# Result: meeting_2024_summary_restored.txt
```

### Example 2: Short Summary

```bash
# Complete pipeline with 100-word limit
python process_video_complete.py presentation.mkv --max-length 100
```

### Example 3: Share Sanitized Summary

```bash
# Create summary but keep it sanitized for sharing
python summarize_with_ollama.py video_sanitized.txt --keep-sanitized

# Now share: video_summary_sanitized.txt (safe to share)
```

## Privacy Protection

### How It Works

1. **Original Content**: "Xin chào Anh chị, hôm nay ta học Kiến thức mới"
2. **Sanitized** (sent to Ollama): "Xin chào AC, hôm nay ta học KT mới"
3. **Ollama Summary** (sanitized): "Buổi học giới thiệu AC với KT mới"
4. **Restored**: "Buổi học giới thiệu Anh chị với Kiến thức mới"

### Key Points

✅ **Ollama only sees sanitized text** - No confidential information leaked  
✅ **Summary inherits protection** - AC and KT used instead of originals  
✅ **Restoration is optional** - Can keep summary sanitized for sharing  
✅ **Local processing** - Everything runs on your machine  

## Testing

### Test Complete Pipeline

```bash
python test_complete_pipeline.py
```

**This tests:**
- ✓ Sanitization (confidential → codes)
- ✓ Summarization (mock or real Ollama)
- ✓ Restoration (codes → confidential)
- ✓ File operations

**Expected output:**
```
✅ ALL TESTS PASSED

The complete pipeline is working correctly:
  • Transcription → Sanitization ✓
  • Sanitized text → Summarization ✓
  • Summary → Restoration ✓
  • File operations ✓

🔒 Confidential information is protected throughout the process!
```

## Troubleshooting

### Issue: "Cannot connect to Ollama service"

**Cause:** Ollama is not running

**Solution:**
```bash
# Start Ollama service
ollama serve
```

### Issue: "Model 'llama3.2' not found"

**Cause:** Model not downloaded

**Solution:**
```bash
# Download the model
ollama pull llama3.2

# Check available models
ollama list
```

### Issue: Summarization is slow

**Cause:** Large text or slow hardware

**Solutions:**
1. Use a smaller model: `--model llama3.2` (instead of larger models)
2. Limit input text length
3. Use GPU acceleration (Ollama will use GPU if available)

### Issue: Summary quality is poor

**Solutions:**
1. Use a better model: `--model llama2` or `--model mistral`
2. Provide custom prompt: `--prompt "Summarize key points in bullet form: {text}"`
3. Adjust max length: `--max-length 300`

### Issue: Restoration doesn't work correctly

**Cause:** Configuration mismatch

**Solution:**
- Ensure `confidential_terms.py` hasn't changed between sanitization and restoration
- Use the same configuration file throughout the process

## Custom Prompts

### Template

```bash
python summarize_with_ollama.py video_sanitized.txt \
  --prompt "Your custom prompt here. Use {text} as placeholder."
```

### Examples

**Bullet points:**
```bash
--prompt "Summarize the following in 5 bullet points:\n{text}\n\nSummary:"
```

**Executive summary:**
```bash
--prompt "Provide an executive summary for business stakeholders:\n{text}\n\nExecutive Summary:"
```

**Action items:**
```bash
--prompt "Extract action items and key decisions from:\n{text}\n\nAction Items:"
```

**Timeline:**
```bash
--prompt "Create a chronological timeline of events discussed in:\n{text}\n\nTimeline:"
```

## Performance Tips

### 1. Model Selection

| Model | Size | Speed | Quality | Use Case |
|-------|------|-------|---------|----------|
| llama3.2 | ~2GB | Fast | Good | Daily use, quick summaries |
| llama2 | ~4GB | Medium | Better | Important meetings |
| mistral | ~4GB | Medium | Better | Technical content |

### 2. Hardware

- **GPU**: Ollama automatically uses GPU if available (much faster)
- **CPU**: Works fine, just slower for large texts
- **RAM**: Recommended 8GB+ for smooth operation

### 3. Optimization

```bash
# Fast summary (shorter is faster)
python summarize_with_ollama.py video_sanitized.txt --max-length 50

# Balance (default)
python summarize_with_ollama.py video_sanitized.txt --max-length 200

# Detailed (slower)
python summarize_with_ollama.py video_sanitized.txt --max-length 500
```

## File Management

### Generated Files

After running the complete pipeline:

```
presentation.mp4                      (Original video - input)
├── presentation.txt                  (Original transcription - DO NOT SHARE)
├── presentation_sanitized.txt        (Safe to share)
├── presentation_summary_sanitized.txt (Safe to share)
└── presentation_summary_restored.txt  (DO NOT SHARE - for authorized users only)
```

### .gitignore Configuration

Already configured to exclude sensitive files:

```gitignore
# Never commit these to Git
*.txt                          # All text outputs
*.mp4                          # Video files
*.mkv                          # Video files
*_restored.txt                 # Restored content
```

## Integration Examples

### Example Workflow: Team Meeting

```bash
# 1. Record meeting → meeting.mp4
# 2. Process with full pipeline
python process_video_complete.py meeting.mp4

# 3. Share with team (safe files)
#    - meeting_sanitized.txt
#    - meeting_summary_sanitized.txt

# 4. Manager reviews restored version (confidential)
#    - meeting_summary_restored.txt
```

### Example Workflow: Training Video

```bash
# 1. Process training video
python process_video_complete.py training.mp4 --max-length 300

# 2. Public summary (sanitized)
cp training_summary_sanitized.txt public/training_overview.txt

# 3. Internal summary (restored)
cp training_summary_restored.txt internal/training_full.txt
```

## Security Best Practices

### ✅ DO

- Run Ollama locally (never send data to external APIs)
- Keep restored files secure
- Use sanitized versions for sharing
- Test with `--check` flag before processing important files
- Document who can access restored files

### ❌ DON'T

- Share restored files publicly
- Use external LLM APIs (defeats privacy protection)
- Commit restored files to Git
- Process confidential videos on shared computers

## Advanced Configuration

### Custom Confidential Terms

Edit `confidential_terms.py`:

```python
CONFIDENTIAL_TERMS = {
    # Default terms
    r'Anh chị': 'AC',
    r'Kiến thức': 'KT',
    
    # Add your own
    r'Project Phoenix': 'PROJ_A',
    r'Client ABC': 'CLIENT_1',
    r'\$\d+(?:,\d{3})*(?:\.\d{2})?': '[AMOUNT]',  # Money amounts
}
```

### Environment Variables

```bash
# Set default Ollama model
export OLLAMA_MODEL=llama3.2

# Set Ollama host (if running on different machine)
export OLLAMA_HOST=http://localhost:11434
```

## FAQ

**Q: Does Ollama send data to the internet?**  
A: No, Ollama runs completely locally. No data leaves your machine.

**Q: Can I use this without Ollama?**  
A: Yes! Use `--skip-summary` to skip summarization and only transcribe.

**Q: What languages does this support?**  
A: WhisperX supports 90+ languages. Ollama models work with most major languages.

**Q: How accurate is the summarization?**  
A: Depends on the model. llama3.2 and llama2 are quite good for general content.

**Q: Can I summarize without restoring?**  
A: Yes! Use `--keep-sanitized` flag to keep the summary sanitized.

**Q: Is this safe for highly confidential content?**  
A: Yes, as long as:
  - Ollama runs locally (not cloud-based)
  - You configure all confidential terms properly
  - You control access to restored files

---

## Quick Reference

```bash
# Complete pipeline (one command)
python process_video_complete.py video.mp4

# Just summarize existing sanitized file
python summarize_with_ollama.py video_sanitized.txt

# Check Ollama status
python summarize_with_ollama.py --check

# Test everything
python test_complete_pipeline.py
```

**Need help?** Check the main [README.md](README.md) or [PRIVACY_GUIDE.md](PRIVACY_GUIDE.md) for more information.

---

**🔒 Remember: This system protects confidential information by never exposing it to the LLM in its original form!**
