# 🤖 Ollama Summarization & Translation Guide

## Overview

This guide explains how to use Ollama to **summarize** and **translate** transcribed videos while maintaining privacy protection. The complete workflow ensures that **confidential information never leaves your system** in its original form.

## Complete Workflow

### Summarization Flow

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

### Translation Flow

```
Video File
    ↓
[1] Transcribe → Creates original.txt + sanitized.txt
    ↓
[2] Sanitize → Replace "Anh chị" → "AC", "Kiến thức" → "KT"
    ↓
[3] Translate (Ollama) → Vietnamese "AC, KT" → English "AC, KT"
    ↓
[4] Restore → Convert "AC" → "Anh chị", "KT" → "Kiến thức"
    ↓
Final Translation (with confidential info restored in target language)
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

Process video → transcribe → sanitize → summarize/translate → restore in one command:

#### Summarization Only
```bash
python process_video_complete.py presentation.mp4
```

**Output files:**
- `presentation.txt` - Original transcription
- `presentation_sanitized.txt` - Safe version (no confidential info)
- `presentation_summary_sanitized.txt` - Summary (sanitized)
- `presentation_summary_restored.txt` - Summary (confidential info restored)

#### Translation Only
```bash
python process_video_complete.py presentation.mp4 --translate English --skip-summary
```

**Output files:**
- `presentation.txt` - Original transcription
- `presentation_sanitized.txt` - Safe version
- `presentation_translation_english_sanitized.txt` - Translation (sanitized)
- `presentation_translation_english_restored.txt` - Translation (restored)

#### Both Summarization AND Translation
```bash
python process_video_complete.py presentation.mp4 --translate Japanese --max-length 200
```

**Output files:**
- Original transcription files
- Summary files (both sanitized and restored)
- Translation files (both sanitized and restored)

### Option 2: Step-by-Step Workflow

#### Step 1: Transcribe Video

```bash
python main.py presentation.mp4
```

**Creates:**
- `presentation.txt` (original)
- `presentation_sanitized.txt` (confidential info removed)

#### Step 2A: Summarize Sanitized Text

```bash
python summarize_with_ollama.py presentation_sanitized.txt
```

**Creates:**
- `presentation_summary_sanitized.txt` (summary with codes)
- `presentation_summary_restored.txt` (summary with confidential info)

#### Step 2B: Translate Sanitized Text

```bash
python translate_with_ollama.py presentation_sanitized.txt --target-lang English
```

**Creates:**
- `presentation_translation_english_sanitized.txt` (translation with codes)
- `presentation_translation_english_restored.txt` (translation with confidential info)

## Command Options

### process_video_complete.py

```bash
# Full pipeline with default model (llama3.2)
python process_video_complete.py video.mp4

# Use different model
python process_video_complete.py video.mp4 --model llama2

# Skip summarization (transcription only)
python process_video_complete.py video.mp4 --skip-summary

# Translate to English
python process_video_complete.py video.mp4 --translate English

# Translate with source language specified
python process_video_complete.py video.mp4 --translate English --source-lang Vietnamese

# Summarize AND translate
python process_video_complete.py video.mp4 --translate Japanese --max-length 200

# Keep summary/translation sanitized (don't restore confidential info)
python process_video_complete.py video.mp4 --translate English --keep-sanitized

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

### translate_with_ollama.py

```bash
# Basic translation to English
python translate_with_ollama.py video_sanitized.txt --target-lang English

# Translate to Japanese with specific model
python translate_with_ollama.py video_sanitized.txt --target-lang Japanese --model llama2

# Keep translation sanitized (don't restore)
python translate_with_ollama.py video_sanitized.txt --target-lang English --keep-sanitized

# Specify source language
python translate_with_ollama.py video_sanitized.txt --target-lang English --source-lang Vietnamese

# Custom translation prompt
python translate_with_ollama.py video_sanitized.txt --target-lang English \
  --prompt "Translate professionally: {text}"

# Check Ollama status
python translate_with_ollama.py --check
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

### Example 4: Translate to English

```bash
# Translate Vietnamese video to English
python translate_with_ollama.py meeting_sanitized.txt --target-lang English

# Result: 
#   meeting_translation_english_sanitized.txt (codes: AC, KT - safe to share)
#   meeting_translation_english_restored.txt (Vietnamese terms: Anh chị, Kiến thức)

# Note: Restored version has Vietnamese confidential terms in English text
# Example: "Hello Anh chị, learning new Kiến thức"
```

### Example 5: Translate to Multiple Languages

```bash
# Complete pipeline - transcribe and translate
python process_video_complete.py presentation.mp4 --translate English

# Translate to another language
python translate_with_ollama.py presentation_sanitized.txt --target-lang Japanese

# Translate to a third language
python translate_with_ollama.py presentation_sanitized.txt --target-lang Chinese
```

### Example 6: Summarize AND Translate

```bash
# Get both summary and translation in one command
python process_video_complete.py training.mp4 --translate English --max-length 150

# Output:
#   - training_summary_sanitized.txt & training_summary_restored.txt
#   - training_translation_english_sanitized.txt & training_translation_english_restored.txt
```

## Privacy Protection

### How Summarization Works

1. **Original Content**: "Xin chào Anh chị, hôm nay ta học Kiến thức mới"
2. **Sanitized** (sent to Ollama): "Xin chào AC, hôm nay ta học KT mới"
3. **Ollama Summary** (sanitized): "Buổi học giới thiệu AC với KT mới"
4. **Restored**: "Buổi học giới thiệu Anh chị với Kiến thức mới"

### How Translation Works

1. **Original (Vietnamese)**: "Xin chào Anh chị, hôm nay ta học Kiến thức mới"
2. **Sanitized** (sent to Ollama): "Xin chào AC, hôm nay ta học KT mới"
3. **Ollama Translation** (English, sanitized): "Hello AC, today we learn new KT"
4. **Restored**: "Hello Anh chị, today we learn new Kiến thức"

⚠️ **Important**: Restored translations contain **original language terms** in the target language text. This is intentional to preserve confidential information for authorized users. If you want to keep codes (AC, KT) for sharing, use `--keep-sanitized` flag.

### Key Points

✅ **Ollama only sees sanitized text** - No confidential information leaked  
✅ **Summaries/Translations inherit protection** - AC and KT used instead of originals  
✅ **Restoration is optional** - Can keep outputs sanitized for sharing  
✅ **Local processing** - Everything runs on your machine  
✅ **Multiple languages** - Translate to any language Ollama supports  

## Supported Translation Languages

Ollama models support translation to/from many languages:

**Major Languages:**
- English
- Japanese (日本語)
- Chinese (中文)
- Spanish (Español)
- French (Français)
- German (Deutsch)
- Korean (한국어)
- Portuguese (Português)
- Russian (Русский)
- Italian (Italiano)

**Other Supported Languages:**
- Arabic, Dutch, Hindi, Thai, Turkish, Vietnamese (native), Polish, Swedish, Danish, Norwegian, Finnish, and many more!

**Usage:**
```bash
# Just specify the language name
python translate_with_ollama.py video_sanitized.txt --target-lang "Japanese"
python translate_with_ollama.py video_sanitized.txt --target-lang "中文"  # Chinese characters work too
```  

## Testing

### Test Summarization Pipeline

```bash
python test_complete_pipeline.py
```

**This tests:**
- ✓ Sanitization (confidential → codes)
- ✓ Summarization (mock or real Ollama)
- ✓ Restoration (codes → confidential)
- ✓ File operations

### Test Translation Pipeline

```bash
python test_translation.py
```

**This tests:**
- ✓ Sanitization before translation
- ✓ Translation with privacy protection
- ✓ Code preservation during translation
- ✓ Restoration in translated text

**Expected output:**
```
✅ TRANSLATION TEST PASSED

The translation pipeline is working correctly:
  • Vietnamese → Sanitization ✓
  • Sanitized text → Translation ✓
  • Translation → Restoration ✓
  • Confidential info protected ✓

🔒 Confidential information is protected during translation!
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
A: WhisperX transcription supports 90+ languages. Ollama translation supports all major languages (English, Japanese, Chinese, Spanish, French, German, Korean, etc.).

**Q: How accurate is the summarization/translation?**  
A: Depends on the model. llama3.2 and llama2 are quite good for general content and multiple languages.

**Q: Can I summarize/translate without restoring?**  
A: Yes! Use `--keep-sanitized` flag to keep outputs sanitized (safe to share).

**Q: Can I translate to multiple languages?**  
A: Yes! Run the translate command multiple times with different `--target-lang` values.

**Q: Does translation preserve confidential codes?**  
A: Yes! Ollama is instructed to keep codes like AC and KT unchanged during translation.

**Q: Why does the restored translation have Vietnamese words in English text?**  
A: This is intentional. Restoration converts codes (AC, KT) back to their original Vietnamese terms ("Anh chị", "Kiến thức") to preserve confidential information for authorized users. If you want English-only text with codes, use `--keep-sanitized` flag.

**Q: Which file should I share with others?**  
A: Always share the `*_sanitized.txt` files (with AC, KT codes). Never share `*_restored.txt` files unless the recipient is authorized to see confidential information.

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

# Complete pipeline with translation
python process_video_complete.py video.mp4 --translate English

# Summarize existing sanitized file
python summarize_with_ollama.py video_sanitized.txt

# Translate existing sanitized file
python translate_with_ollama.py video_sanitized.txt --target-lang Japanese

# Check Ollama status
python summarize_with_ollama.py --check
python translate_with_ollama.py --check

# Test everything
python test_complete_pipeline.py
python test_translation.py
```

**Need help?** Check the main [README.md](README.md) or [PRIVACY_GUIDE.md](PRIVACY_GUIDE.md) for more information.

---

**🔒 Remember: This system protects confidential information by never exposing it to the LLM in its original form - whether summarizing or translating!**
