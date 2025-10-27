# Microsoft Teams Integration Guide

## Overview

Send transcription, translation, and summary files directly to Microsoft Teams channels using webhook integration.

## Quick Start

### 1. Get Teams Webhook URL

1. Open Microsoft Teams
2. Go to your channel
3. Click "..." → "Connectors" → "Incoming Webhook"
4. Click "Add" → "Configure"
5. Give it a name (e.g., "Video Transcription Bot")
6. Copy the webhook URL

**Webhook URL format:**
```
https://your-org.webhook.office.com/webhookb2/xxxx-xxxx-xxxx/IncomingWebhook/yyyy-yyyy-yyyy
```

### 2. Send Files to Teams

## Usage Examples

### From `auto_translate_google.py`:

```bash
# Translate and send to Teams
python src/auto_translate_google.py videos/input.txt \
  --target-lang English \
  --send-to-teams \
  --teams-webhook "https://your-webhook-url"

# With custom output
python src/auto_translate_google.py videos/input.txt \
  --target-lang Japanese \
  --output videos/translation_jp.txt \
  --send-to-teams \
  --teams-webhook "https://your-webhook-url"

# Headless mode + Teams
python src/auto_translate_google.py videos/input.txt \
  --target-lang English \
  --headless \
  --send-to-teams \
  --teams-webhook "https://your-webhook-url"
```

### From `process_video_complete.py`:

```bash
# Full pipeline: transcribe → translate → send to Teams
python src/process_video_complete.py videos/video.mp4 \
  --translate English \
  --send-to-teams \
  --teams-webhook "https://your-webhook-url"

# Transcribe + summarize + send
python src/process_video_complete.py videos/video.mp4 \
  --max-length 200 \
  --send-to-teams \
  --teams-webhook "https://your-webhook-url"

# Multiple operations
python src/process_video_complete.py videos/video.mp4 \
  --translate English \
  --max-length 150 \
  --send-to-teams \
  --teams-webhook "https://your-webhook-url"
```

### Standalone `send_to_teams.py`:

```bash
# Send single file
python src/send_to_teams.py videos/output.txt \
  --webhook "https://your-webhook-url"

# With custom message
python src/send_to_teams.py videos/output.txt \
  --webhook "https://your-webhook-url" \
  --title "📄 Important Document" \
  --message "Please review this translation"

# Include file content in message
python src/send_to_teams.py videos/summary.txt \
  --webhook "https://your-webhook-url" \
  --include-content

# Send with saved webhook
python src/send_to_teams.py videos/output.txt

# List saved webhooks
python src/send_to_teams.py --list-webhooks
```

## Save Webhook URL (Recommended)

Instead of typing the webhook URL every time, save it:

```bash
# Save webhook with name
python src/send_to_teams.py --save-webhook \
  --webhook "https://your-webhook-url" \
  --name "my-team-channel"

# Use saved webhook
python src/send_to_teams.py videos/output.txt --name "my-team-channel"

# Or set as default
python src/send_to_teams.py --save-webhook \
  --webhook "https://your-webhook-url" \
  --name "default"

# Then just use without specifying:
python src/send_to_teams.py videos/output.txt
```

## Environment Variable

Set webhook as environment variable:

### Windows (PowerShell):
```powershell
$env:TEAMS_WEBHOOK_URL = "https://your-webhook-url"
```

### Windows (CMD):
```cmd
set TEAMS_WEBHOOK_URL=https://your-webhook-url
```

### Linux/Mac:
```bash
export TEAMS_WEBHOOK_URL="https://your-webhook-url"
```

Then use without `--teams-webhook`:
```bash
python src/auto_translate_google.py videos/input.txt \
  --target-lang English \
  --send-to-teams
```

## What Gets Sent?

### From `auto_translate_google.py`:
- ✅ Translated file (`_autotranslated.txt`)
- ✅ Preview of first 1000 characters

### From `process_video_complete.py`:
- ✅ Original transcription (`.txt`)
- ✅ Sanitized transcription (`_sanitized.txt`)
- ✅ Summary files (if generated)
- ✅ Translation files (if generated)
- ✅ Preview of restored files only

## Message Format

Messages in Teams will appear as:

```
📄 Translation English Restored - video.mp4

File: video_translation_english_restored.txt
Size: 2.5 KB

Preview:
Hello Anh chị, today we will learn about Kiến thức...
```

## Troubleshooting

### Error: "Module not available"
```bash
# Make sure send_to_teams.py is in src/ directory
ls src/send_to_teams.py
```

### Error: "Webhook URL not provided"
```bash
# Provide webhook URL:
--teams-webhook "https://your-url"

# Or save it:
python src/send_to_teams.py --save-webhook --webhook "https://your-url"

# Or use environment variable:
export TEAMS_WEBHOOK_URL="https://your-url"
```

### Error: "Failed to send to Teams"
- Check webhook URL is correct
- Verify webhook is still active in Teams
- Check internet connection
- Ensure file exists and is readable

### Test Webhook
```bash
# Test if webhook works
python src/send_to_teams.py --test-webhook \
  --webhook "https://your-webhook-url"
```

## Privacy & Security

### What's Sent:
- ✅ File name
- ✅ File size
- ✅ File content (optionally)

### What's NOT Sent:
- ❌ Original video file
- ❌ Full sanitized content (only restored)
- ❌ Webhook URL is stored locally only

### Best Practices:
1. **Use sanitized files** when sharing with teams
2. **Don't send restored files** to public channels
3. **Review content** before sending sensitive data
4. **Rotate webhooks** periodically for security
5. **Use separate webhooks** for different channels/projects

## Complete Workflow Example

```bash
# 1. Process video with full pipeline
python src/process_video_complete.py videos/meeting.mp4 \
  --translate English \
  --max-length 200 \
  --send-to-teams \
  --teams-webhook "https://your-webhook-url"

# This will:
# - Transcribe video
# - Create sanitized version
# - Generate summary
# - Translate to English
# - Restore confidential info
# - Send ALL result files to Teams

# 2. Manual translation with Teams
python src/auto_translate_google.py videos/input_sanitized.txt \
  --target-lang Japanese \
  --send-to-teams \
  --teams-webhook "https://your-webhook-url"

# 3. Send existing file
python src/send_to_teams.py videos/important_summary.txt \
  --webhook "https://your-webhook-url" \
  --title "📊 Weekly Summary"
```

## Advanced Configuration

### Custom Teams Message Card

Edit `send_to_teams.py` to customize the message card:

```python
# Modify create_teams_card function
card = {
    "@type": "MessageCard",
    "themeColor": "0078D7",  # Change color
    "title": f"🎯 {title}",  # Change emoji
    # ... customize more ...
}
```

### Filter Files to Send

In `process_video_complete.py`, control which files are sent:

```python
# Only send restored files
for key, file_path in results.items():
    if 'restored' in key:  # Only restored files
        send_file_to_teams(...)
```

## FAQ

**Q: Can I send to multiple channels?**  
A: Yes, save multiple webhooks with different names and specify `--name` parameter.

**Q: Is the file uploaded to Teams?**  
A: No, only the file content is included in the message card (up to size limit).

**Q: What's the file size limit?**  
A: Teams messages have a limit of ~28KB. Large files show preview only.

**Q: Can I send images/videos?**  
A: Not directly. Only text files are supported with content preview.

**Q: Is this secure?**  
A: Webhooks are as secure as you keep the URL. Use HTTPS and don't share URLs publicly.

## Support

For issues or questions:
1. Check logs in terminal output
2. Test webhook with `--test-webhook`
3. Verify file exists and is readable
4. Check Teams connector is still active
