# Teams Integration - Quick Reference

## ✅ IMPLEMENTED: Teams Integration

Teams integration has been added to **both** `auto_translate_google.py` and `process_video_complete.py`.

## 📋 How to Use

### Option 1: From `auto_translate_google.py`

```bash
# Basic: Translate and send to Teams
python src/auto_translate_google.py videos/input.txt \
  --target-lang English \
  --send-to-teams \
  --teams-webhook "YOUR_WEBHOOK_URL"
```

**What it sends:**
- Translated file (`_autotranslated.txt`)
- File preview (first 1000 characters)

### Option 2: From `process_video_complete.py`

```bash
# Full pipeline: transcribe → translate → summarize → send to Teams
python src/process_video_complete.py videos/video.mp4 \
  --translate English \
  --max-length 200 \
  --send-to-teams \
  --teams-webhook "YOUR_WEBHOOK_URL"
```

**What it sends:**
- Original transcription (`.txt`)
- Sanitized transcription (`_sanitized.txt`)
- Summary files (if `--max-length` used)
- Translation files (if `--translate` used)
- Restored files (with previews)

## 🔗 Get Your Webhook URL

1. Open **Microsoft Teams**
2. Go to your **channel**
3. Click **"..."** → **"Connectors"** → **"Incoming Webhook"**
4. Click **"Add"** → **"Configure"**
5. Give it a name (e.g., "Video Bot")
6. **Copy** the webhook URL

Webhook looks like:
```
https://your-org.webhook.office.com/webhookb2/xxxxx/IncomingWebhook/yyyyy
```

## 💡 Save Webhook (Recommended)

Instead of typing the URL every time:

```bash
# Save webhook
python src/send_to_teams.py --save-webhook \
  --webhook "YOUR_WEBHOOK_URL" \
  --name "my-channel"

# Then use saved webhook
python src/auto_translate_google.py videos/input.txt \
  --target-lang English \
  --send-to-teams \
  --teams-webhook "my-channel"
```

## 🌍 Or Use Environment Variable

**Windows (PowerShell):**
```powershell
$env:TEAMS_WEBHOOK_URL = "YOUR_WEBHOOK_URL"
```

**Then use without `--teams-webhook`:**
```bash
python src/auto_translate_google.py videos/input.txt \
  --target-lang English \
  --send-to-teams
```

## 📝 Complete Examples

### Example 1: Google Translate → Teams
```bash
python src/auto_translate_google.py "videos/2025-10-08 20-01-44_sanitized.txt" \
  --target-lang English \
  --send-to-teams \
  --teams-webhook "https://your-webhook-url"
```

### Example 2: Full Pipeline → Teams
```bash
python src/process_video_complete.py videos/meeting.mp4 \
  --translate Japanese \
  --max-length 150 \
  --send-to-teams \
  --teams-webhook "https://your-webhook-url"
```

### Example 3: Just Send Existing File
```bash
python src/send_to_teams.py videos/output.txt \
  --webhook "https://your-webhook-url" \
  --title "📄 Important Document"
```

## 🔍 Command Line Options

### `auto_translate_google.py`:
- `--send-to-teams` - Enable Teams integration
- `--teams-webhook URL` - Webhook URL or saved name

### `process_video_complete.py`:
- `--send-to-teams` - Enable Teams integration  
- `--teams-webhook URL` - Webhook URL or saved name

### `send_to_teams.py` (standalone):
- `--webhook URL` - Required (or use saved/env)
- `--title TEXT` - Custom title
- `--message TEXT` - Custom message
- `--include-content` - Include file content
- `--save-webhook` - Save webhook for later
- `--name NAME` - Webhook name
- `--list-webhooks` - List saved webhooks

## 📊 What Appears in Teams?

```
📄 Translation English Restored - video.mp4

File: video_translation_english_restored.txt
Size: 2.5 KB
Created: 2025-10-27 10:30:15

Preview:
Hello Anh chị, today we will learn about Kiến thức...
(Preview limited to 1000 characters)

[View Full Message]
```

## 🛠️ Troubleshooting

### "Module not available"
```bash
# Check file exists
ls src/send_to_teams.py
```

### "Webhook URL not provided"
```bash
# Provide URL directly
--teams-webhook "https://your-url"

# Or save it first
python src/send_to_teams.py --save-webhook --webhook "https://your-url"

# Or use environment variable
$env:TEAMS_WEBHOOK_URL = "https://your-url"
```

### Test Your Webhook
```bash
python src/send_to_teams.py --test-webhook \
  --webhook "https://your-webhook-url"
```

## 🔐 Security Tips

1. **Don't commit** webhook URLs to git
2. **Use environment variables** for sensitive webhooks
3. **Review content** before sending to public channels
4. **Send sanitized files** for sharing, not restored
5. **Rotate webhooks** periodically

## 📚 Full Documentation

See `TEAMS_INTEGRATION.md` for complete guide including:
- Advanced configuration
- Custom message cards
- Multiple channels
- Security best practices
- FAQ

## ✨ Quick Test

```bash
# 1. Save webhook
python src/send_to_teams.py --save-webhook \
  --webhook "YOUR_WEBHOOK_URL" \
  --name "default"

# 2. Test with existing file
python src/send_to_teams.py "videos/2025-10-08 20-01-44_sanitized.txt"

# 3. If successful, integrate with translation
python src/auto_translate_google.py "videos/2025-10-08 20-01-44_sanitized.txt" \
  --target-lang English \
  --send-to-teams
```

---

**✅ Teams integration is ready to use!**

For questions or issues, check the full documentation in `TEAMS_INTEGRATION.md`.
