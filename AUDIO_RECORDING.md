# Audio Recording - Quick Start Guide

## ✅ IMPLEMENTED: Audio Recording Module

Record both microphone and system audio (desktop audio) for transcription.

## 📋 Quick Commands

### Record Both Microphone + System Audio
```bash
python src/record_audio.py --duration 60
# Output: videos/recording_mixed_2025-10-28_14-30-00.wav
```

### Record Microphone Only
```bash
python src/record_audio.py --duration 30 --microphone-only
# Output: videos/recording_mic_2025-10-28_14-30-00.wav
```

### Record System Audio Only (Desktop Audio)
```bash
python src/record_audio.py --duration 60 --system-only
# Output: videos/recording_system_2025-10-28_14-30-00.wav
```

### Manual Recording (Stop with Ctrl+C)
```bash
python src/record_audio.py --microphone-only
# Press Ctrl+C when you want to stop
```

### List Available Devices
```bash
python src/record_audio.py --list-devices
```

## 🎯 Complete Workflow Examples

### Example 1: Record Meeting → Transcribe → Translate
```bash
# 1. Record meeting (both mic + desktop audio)
python src/record_audio.py --duration 3600 --output videos/meeting.wav

# 2. Transcribe and translate
python src/process_video_complete.py videos/meeting.wav --translate English

# Output files:
# - meeting.txt (original transcription)
# - meeting_sanitized.txt (privacy protected)
# - meeting_translation_english_restored.txt (translation)
```

### Example 2: Record Presentation → Transcribe → Summarize → Teams
```bash
# 1. Record presentation
python src/record_audio.py --duration 1800 --output videos/presentation.wav

# 2. Process with summary and send to Teams
python src/process_video_complete.py videos/presentation.wav \
  --max-length 200 \
  --send-to-teams \
  --teams-webhook "YOUR_WEBHOOK_URL"
```

### Example 3: Record Online Class → Full Pipeline
```bash
# 1. Record class (30 minutes)
python src/record_audio.py --duration 1800 --output videos/class.wav

# 2. Transcribe → Translate → Summarize
python src/process_video_complete.py videos/class.wav \
  --translate English \
  --max-length 150
```

## 🔧 Advanced Options

### Select Specific Microphone
```bash
# 1. List devices to find device index
python src/record_audio.py --list-devices

# Output:
# 📱 Input Devices (Microphones):
#   [0] Built-in Microphone [DEFAULT]
#   [1] USB Headset Microphone
#   [2] External Microphone

# 2. Record with specific device
python src/record_audio.py --duration 60 --mic-device 1
```

### Custom Output Location
```bash
python src/record_audio.py --duration 60 --output "D:/Recordings/meeting_2025.wav"
```

### Different Durations for Different Needs
```bash
# Quick voice note (30 seconds)
python src/record_audio.py --duration 30 --microphone-only

# Short meeting (15 minutes)
python src/record_audio.py --duration 900

# Long presentation (1 hour)
python src/record_audio.py --duration 3600

# All day recording (8 hours)
python src/record_audio.py --duration 28800
```

## 📊 What Gets Recorded?

### Microphone Only
- Your voice
- Any sounds picked up by microphone
- Ideal for: Voice notes, narration, in-person meetings

### System Audio Only
- Desktop sounds
- Application audio
- Media playback
- Ideal for: Recording webinars, online videos, tutorials

### Both (Mixed)
- 50% microphone + 50% system audio
- Perfectly synchronized
- Ideal for: Online meetings, video conferences, remote presentations

## 🎵 Audio Format

- **Format:** WAV (uncompressed)
- **Sample Rate:** 44,100 Hz (CD quality)
- **Channels:** Stereo (2 channels)
- **Bit Depth:** 16-bit
- **Compatible:** Works with WhisperX transcription

## 💡 Tips & Best Practices

### For Best Quality:
1. **Use a good microphone** - Built-in mics often pick up fan noise
2. **Reduce background noise** - Close windows, turn off fans
3. **Test first** - Record 10 seconds to check levels
4. **Check device selection** - Use `--list-devices` to find best mic
5. **Position matters** - Keep mic 6-12 inches from mouth

### For Online Meetings:
```bash
# Record both your voice and meeting audio:
python src/record_audio.py --duration 3600 --output videos/meeting.wav

# Tip: Start recording BEFORE joining the meeting
# Tip: Add 5 minutes to duration for buffer time
```

### For Lectures/Presentations:
```bash
# System audio only (if recording screen/slides):
python src/record_audio.py --duration 5400 --system-only --output videos/lecture.wav

# Microphone only (if presenting in person):
python src/record_audio.py --duration 5400 --microphone-only --output videos/lecture.wav
```

## ⚠️ Troubleshooting

### "PyAudio not available"
```bash
# Install PyAudio
pip install pyaudio

# On Windows, if pip install fails:
# Download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Then: pip install PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl
```

### "soundcard not available"
```bash
pip install soundcard
```

### "No audio devices found"
- Check that microphone is connected
- Check Windows sound settings
- Restart terminal and try again
- Try `python src/record_audio.py --list-devices`

### "Permission denied"
- Grant microphone permission to Python
- Windows: Settings → Privacy → Microphone
- Check antivirus isn't blocking

### Recording is silent
- Check volume levels in Windows
- Test microphone in other apps first
- Try different device with `--mic-device`
- Check mute button on headset

### System audio not recording
- Enable Stereo Mix in Windows:
  1. Right-click speaker icon → Sounds
  2. Recording tab → Right-click → Show Disabled Devices
  3. Enable "Stereo Mix" or "What U Hear"
  4. Set as default

## 📏 File Sizes

Approximate file sizes for WAV recordings:

| Duration | File Size (Stereo, 44.1kHz, 16-bit) |
|----------|-------------------------------------|
| 1 minute | ~10 MB |
| 5 minutes | ~50 MB |
| 15 minutes | ~150 MB |
| 30 minutes | ~300 MB |
| 1 hour | ~600 MB |
| 2 hours | ~1.2 GB |

💡 **Tip:** After transcription, you can compress or delete the WAV file to save space.

## 🔄 Integration with Pipeline

Audio recordings work seamlessly with all other features:

```bash
# Record
python src/record_audio.py --duration 60 --output videos/audio.wav

# Transcribe
python src/process_video_complete.py videos/audio.wav

# Transcribe + Translate
python src/process_video_complete.py videos/audio.wav --translate English

# Transcribe + Translate + Google Translate
python src/process_video_complete.py videos/audio.wav --translate English
python src/auto_translate_google.py videos/audio_sanitized.txt --target-lang Japanese

# Full Pipeline: Record → Transcribe → Translate → Summarize → Teams
python src/record_audio.py --duration 3600 --output videos/meeting.wav
python src/process_video_complete.py videos/meeting.wav \
  --translate English \
  --max-length 200 \
  --send-to-teams \
  --teams-webhook "YOUR_WEBHOOK_URL"
```

## 🎬 Real-World Use Cases

### Use Case 1: Online Meeting
```bash
# Record entire Zoom/Teams meeting
python src/record_audio.py --duration 3600 --output videos/project_meeting.wav

# Get transcription and send to team
python src/process_video_complete.py videos/project_meeting.wav \
  --translate English \
  --send-to-teams --teams-webhook "URL"
```

### Use Case 2: Lecture Notes
```bash
# Record 90-minute lecture
python src/record_audio.py --duration 5400 --output videos/lecture_01.wav

# Get summary
python src/process_video_complete.py videos/lecture_01.wav --max-length 300
```

### Use Case 3: Interview
```bash
# Record interview
python src/record_audio.py --duration 1800 --microphone-only --output videos/interview.wav

# Get transcription (keep private - no Teams)
python src/process_video_complete.py videos/interview.wav
```

### Use Case 4: Podcast Recording
```bash
# Record podcast with guest (system audio = guest's voice)
python src/record_audio.py --duration 7200 --output videos/podcast_ep01.wav

# Get transcription for show notes
python src/process_video_complete.py videos/podcast_ep01.wav
```

## 🆘 Getting Help

```bash
# Show all options
python src/record_audio.py --help

# List devices
python src/record_audio.py --list-devices

# Test with short recording
python src/record_audio.py --duration 10 --output videos/test.wav
```

---

**✅ Audio recording is ready to use!**

Start recording your meetings, presentations, and lectures for automatic transcription and translation!
