# WhisperX Offline Video Transcription

A Python script for transcribing video files using WhisperX offline with GPU acceleration support.

## Project Structure

```
whisperx/
├── src/                          # Source code
│   ├── main.py                   # Simple transcription script
│   ├── process_video_complete.py # Complete pipeline with all features
│   ├── confidential_terms.py     # Privacy protection terms
│   ├── reverse_sanitize.py       # Restore confidential information
│   ├── summarize_with_ollama.py  # LLM summarization
│   └── translate_with_ollama.py  # LLM translation
├── test/                         # Test scripts
│   ├── test_sanitization.py
│   ├── test_reverse_sanitization.py
│   ├── test_complete_pipeline.py
│   └── test_translation.py
├── videos/                       # Videos and output files
│   ├── *.mp4                     # Your video files
│   ├── *_sanitized.txt           # Sanitized transcriptions
│   ├── *_summary*.txt            # Summaries
│   └── *_translation*.txt        # Translations
├── venv/                         # Virtual environment
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Features

- 🎥 Video file transcription using WhisperX
- 🚀 GPU acceleration support (CUDA)
- 📝 Text output format (.txt)
- 🔄 Automatic audio extraction from video files
- 🎯 High-quality transcription with word-level alignment
- 📱 Simple command-line interface
- 🔒 Automatic sanitization of confidential information
- 🛡️ Privacy protection with customizable term replacement
- 🤖 LLM summarization with Ollama (NEW!)
- 🔄 Bidirectional sanitization (forward and reverse)
- 📊 Complete privacy-preserving pipeline

## Requirements

- Python 3.8 or higher
- NVIDIA GPU with CUDA support (optional, but recommended)
- FFmpeg installed on your system
- Ollama (optional, for LLM summarization)

### System Dependencies

#### FFmpeg Installation

FFmpeg is required to extract audio from video files.

#### Windows
**Method 1: Using winget (Recommended for Windows 10/11)**
```powershell
winget install --id Gyan.FFmpeg -e --source winget
```
After installation, **restart your terminal** for PATH changes to take effect.

**Method 2: Manual Installation**
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract the archive to a location (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your system PATH
4. Restart your terminal

**Verify Installation**:
```powershell
ffmpeg -version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

**Note**: The `main.py` script is pre-configured to automatically find FFmpeg on Windows systems installed via winget. If you installed FFmpeg manually or in a custom location, you may need to update the FFmpeg path in the script.

## Installation

### Prerequisites

Before installing the project, ensure you have:
- Python 3.8 or higher
- Git (for installing julius from source)
- FFmpeg (installation instructions below)

### Step-by-Step Installation

#### Step 1: Clone or download this project

#### Step 2: Create a virtual environment
```bash
# Windows
python -m venv venv
# or
py -m venv venv

# Linux/macOS
python3 -m venv venv
```

#### Step 3: Activate the virtual environment
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
venv\Scripts\activate.bat

# Linux/macOS
source venv/bin/activate
```

#### Step 4: Install FFmpeg (Windows)
```powershell
# Using winget (recommended for Windows 10/11)
winget install --id Gyan.FFmpeg -e --source winget

# After installation, restart your terminal or PowerShell window
```

**For Linux/macOS**, see the System Dependencies section below.

#### Step 5: Install Python packages
```bash
# Install core packages first
pip install torch torchaudio

# Install julius from GitHub (important!)
pip install git+https://github.com/adefossez/julius.git

# Install whisperx and remaining dependencies
pip install whisperx
```

**Note**: The order matters! Installing julius from GitHub before WhisperX prevents compatibility issues.

#### Step 6: Verify installation
```bash
# Test FFmpeg
ffmpeg -version

# Test Python imports
python -c "import whisperx; import torch; print('Setup successful!')"
```

### Alternative: Install from requirements.txt
If you prefer, you can install all dependencies at once, but you'll need to install julius separately:
```bash
pip install git+https://github.com/adefossez/julius.git
pip install -r requirements.txt
```

**⚠️ Important**: Always install julius from GitHub first to avoid the "No module named 'julius'" error.

## Usage

### Before Running the Script

Ensure the following are ready:
- ✅ Virtual environment is activated (`(venv)` should appear in your terminal)
- ✅ FFmpeg is installed and accessible (`ffmpeg -version` works)
- ✅ You're in the project directory (`whisperx` folder)

### Basic Usage
```bash
# Simple transcription (from project root)
python src/main.py videos/your_video.mp4

# Complete pipeline with all features
python src/process_video_complete.py videos/your_video.mp4
```

### Examples
```bash
# Transcribe a video file
python src/main.py videos/test.mkv

# Transcribe with custom output file
python src/main.py videos/test.mkv -o videos/my_transcription.txt

# Transcribe a video with spaces in the filename
python src/main.py "videos/my video file.mp4"

# Disable sanitization (keep original confidential information)
python src/main.py videos/test.mkv --no-sanitize

# Complete pipeline: transcribe + summarize + translate
python src/process_video_complete.py videos/test.mp4 --summarize --translate English
```

### Output Files

By default, the script creates files in the same directory as the video:

1. **Original transcription**: `video_name.txt` - Contains the raw transcription
2. **Sanitized transcription**: `video_name_sanitized.txt` - Contains transcription with confidential information replaced
3. **Summaries** (if --summarize): `video_name_summary_sanitized.txt` and `video_name_summary_restored.txt`
4. **Translations** (if --translate): `video_name_translation_{lang}_sanitized.txt` and `video_name_translation_{lang}_restored.txt`

### Command Line Options

**main.py (Simple Transcription)**:
- `video_path`: Path to the video file to transcribe (required)
- `-o, --output`: Custom output text file path (optional)
- `--no-sanitize`: Disable sanitization

**process_video_complete.py (Complete Pipeline)**:
- `video_path`: Path to the video file to transcribe (required)
- `-o, --output`: Custom output text file path (optional, default: `video_name.txt`)
- `--no-sanitize`: Disable sanitization and only create the original transcription file

## Privacy and Confidential Information

### Automatic Sanitization

The script automatically sanitizes confidential information in transcriptions by replacing sensitive terms with abbreviated codes. This helps protect privacy when sharing transcriptions.

**Default replacements:**
- "Anh chị" → "AC"
- "Kiến thức" → "KT"

### Reverse Sanitization (NEW!)

You can now restore sanitized text back to its original form using the reverse sanitization tool:

```bash
# Restore a sanitized file
python reverse_sanitize.py video_sanitized.txt

# Specify custom output location
python reverse_sanitize.py video_sanitized.txt -o restored_original.txt
```

**Output:** Creates a `video_restored.txt` file with original confidential information restored.

⚠️ **Important**: Only use this tool when you have authorization to access the original confidential information. The restored file should be kept secure.

### LLM Summarization with Ollama (NEW!)

Generate AI-powered summaries of your transcriptions while maintaining privacy protection:

#### Complete Pipeline (Recommended)

Process video → transcribe → sanitize → summarize → restore in one command:

```bash
# Full pipeline with default settings
python src/process_video_complete.py videos/ presentation.mp4

# Use different Ollama model
python src/process_video_complete.py videos/ meeting.mkv --model llama2

# Limit summary length
python src/process_video_complete.py videos/ video.mp4 --max-length 200
```

**Output files:**
- `video.txt` - Original transcription
- `video_sanitized.txt` - Sanitized transcription (safe to share)
- `video_summary_sanitized.txt` - Sanitized summary (safe to share)
- `video_summary_restored.txt` - Restored summary (confidential)

#### Step-by-Step Approach

```bash
# Step 1: Transcribe video
python main.py presentation.mp4

# Step 2: Summarize sanitized transcription
python src/summarize_with_ollama.py presentation_sanitized.txt
```

#### Privacy Protection in Summarization

```
Original: "Anh chị học Kiến thức mới"
    ↓ (Sanitization)
Sanitized: "AC học KT mới"
    ↓ (Sent to Ollama - No confidential info leaked!)
Summary: "Buổi học giới thiệu AC với KT"
    ↓ (Restoration)
Final: "Buổi học giới thiệu Anh chị với Kiến thức"
```

🔒 **Key Point**: Ollama only processes sanitized text, ensuring confidential information never leaves your system in its original form.

**Prerequisites for Ollama:**
1. Install Ollama: https://ollama.com/download
2. Start service: `ollama serve`
3. Download model: `ollama pull llama3.2`

📖 **For complete Ollama setup and usage, see:** [OLLAMA_SUMMARY_GUIDE.md](OLLAMA_SUMMARY_GUIDE.md)

### LLM Translation with Ollama (NEW!)

Translate your transcriptions to any language while maintaining privacy protection:

#### Complete Pipeline with Translation

Process video → transcribe → sanitize → translate → restore in one command:

```bash
# Translate to English
python src/process_video_complete.py videos/ presentation.mp4 --translate English

# Translate to Japanese with specific model
python src/process_video_complete.py videos/ video.mp4 --translate Japanese --model llama2

# Translate AND summarize
python src/process_video_complete.py videos/ video.mp4 --translate English --max-length 200

# Specify source language explicitly
python src/process_video_complete.py videos/ video.mp4 --translate English --source-lang Vietnamese
```

**Output files:**
- `video.txt` - Original transcription
- `video_sanitized.txt` - Sanitized transcription (safe to share)
- `video_translation_english_sanitized.txt` - Sanitized translation (safe to share)
- `video_translation_english_restored.txt` - Restored translation (confidential)

#### Step-by-Step Translation

```bash
# Step 1: Transcribe video
python main.py presentation.mp4

# Step 2: Translate sanitized transcription
python src/translate_with_ollama.py presentation_sanitized.txt --target-lang English
```

#### Privacy Protection in Translation

```
Original (Vietnamese): "Xin chào Anh chị, học Kiến thức mới"
    ↓ (Sanitization)
Sanitized: "Xin chào AC, học KT mới"
    ↓ (Sent to Ollama for translation - No confidential info leaked!)
Translation (English): "Hello AC, learning new KT"
    ↓ (Restoration)
Final: "Hello Anh chị, learning new Kiến thức"
```

🔒 **Key Point**: Ollama only sees codes (AC, KT) during translation, never the original confidential terms!

⚠️ **Important Note**: By default, restored translations contain **original language terms** (Vietnamese) mixed with the target language. If you need codes to remain (for sharing), use the `--keep-sanitized` flag:

```bash
# Keep codes in translation (safe to share)
python src/process_video_complete.py videos/ video.mp4 --translate English --keep-sanitized
# Result: "Hello AC, learning new KT" (codes remain)
```

**Supported Languages**: English, Japanese, Chinese, Spanish, French, German, Korean, and many more!

📖 **For complete translation guide, see:** [OLLAMA_SUMMARY_GUIDE.md](OLLAMA_SUMMARY_GUIDE.md)

### Google Translate Automation (NEW!)

Automate translation using Google Translate's web interface with browser automation:

#### Basic Usage

```bash
# Auto-translate to English (auto-detect source language)
python src/auto_translate_google.py videos/file.txt --target-lang English

# Specify both source and target languages
python src/auto_translate_google.py videos/file_sanitized.txt --source-lang vi --target-lang en

# Save to custom output file
python src/auto_translate_google.py videos/file.txt --target-lang English --output videos/custom_name.txt

# Run in headless mode (no browser window)
python src/auto_translate_google.py videos/file.txt --target-lang English --headless
```

**How it works:**
1. Opens Microsoft Edge browser
2. Navigates to translate.google.com
3. Enters your text in the source text box
4. Waits for translation to complete
5. Clicks the copy button to get translated text
6. Saves to file with `_autotranslated.txt` suffix

**Output file:** `filename_autotranslated.txt`

**Supported Languages**: English, Vietnamese, Spanish, French, German, Chinese, Japanese, Korean, Thai, Russian, Portuguese, Italian, Arabic, Hindi, and more!

**Prerequisites:**
- Microsoft Edge browser must be installed
- Internet connection required
- First run will download Edge WebDriver automatically

**Comparison with Ollama Translation:**

| Feature | Google Translate | Ollama Translation |
|---------|-----------------|-------------------|
| **Privacy** | ⚠️ Sends data to Google | ✅ 100% Local/Offline |
| **Speed** | 🟡 Fast (depends on internet) | 🟡 Moderate (depends on model) |
| **Quality** | 🟢 High for common languages | 🟡 Good (varies by model) |
| **Languages** | 🟢 100+ languages | 🟡 Limited by model |
| **Cost** | ✅ Free | ✅ Free |
| **Setup** | 🟢 Easy (just browser) | 🟡 Requires Ollama install |
| **Character Limit** | ⚠️ ~5000 chars | ✅ No limit |

💡 **Recommendation**: Use Google Translate for quick translations and many languages. Use Ollama for privacy-sensitive content!

### Send to Microsoft Teams (NEW!)

Automatically send translation results to a Microsoft Teams channel:

#### Setup Teams Webhook

1. **Open Microsoft Teams** and navigate to your channel
2. **Click '...'** (More options) next to the channel name
3. **Select 'Connectors'** or **'Workflows'**
4. **Search for 'Incoming Webhook'**
5. **Click 'Configure'** or **'Add'**
6. **Give it a name** (e.g., "Translation Bot")
7. **Copy the webhook URL**
8. **Click 'Done'**

#### Usage

```bash
# Translate and send to Teams:
python src/auto_translate_google.py videos/file.txt --target-lang English --send-to-teams --teams-webhook "https://outlook.office.com/webhook/..."

# Save webhook for future use:
python src/send_to_teams.py videos/output.txt --webhook "https://..." --save-webhook

# Use saved webhook:
python src/auto_translate_google.py videos/file.txt --target-lang English --send-to-teams

# Send any file to Teams:
python src/send_to_teams.py videos/translation.txt --title "Translation Complete!"

# Send multiple files:
python src/send_to_teams.py videos/file1.txt videos/file2.txt videos/file3.txt

# Don't include content preview:
python src/send_to_teams.py videos/file.txt --no-content
```

#### What Gets Sent to Teams

The Teams message includes:
- 📄 **File name** and location
- 📊 **File size** and character count
- 📅 **Creation timestamp**
- 📝 **Content preview** (first 1000 characters, configurable)
- 🔗 **Quick action button** to open folder

**Message Example:**
```
🌐 Auto Translation Complete
━━━━━━━━━━━━━━━━━━━━━━━━

File: video_sanitized_autotranslated.txt
Size: 2,543 bytes (2.48 KB)
Location: C:\whisperx\videos
Characters: 1,847

📄 Content Preview:
Then let's start AC guys. Today we will learn 
a very easy lesson about its core knowledge...

[📂 Open Folder]
```

**Features:**
- ✅ Automatic notifications when translation completes
- ✅ Rich formatted messages with file details
- ✅ Content preview included
- ✅ Webhook URL saved for reuse
- ✅ Works with any text file

**Integration with Translation:**
```bash
# Complete workflow: Translate → Sanitize → Send to Teams
python src/process_video_complete.py videos/ video.mp4 --translate English --send-to-teams
```

### Customizing Confidential Terms

You can customize which terms to sanitize by editing the `confidential_terms.py` file:

```python
CONFIDENTIAL_TERMS = {
    r'Anh chị': 'AC',
    r'Kiến thức': 'KT',
    # Add your own terms:
    r'Your Secret Term': 'REPLACEMENT',
    r'Company Name': 'COMPANY',
}

# For advanced patterns (emails, phone numbers, etc.)
ADVANCED_PATTERNS = [
    (r'\b0\d{9}\b', '[PHONE]'),  # Vietnamese phone numbers
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
]
```

### Disabling Sanitization

If you don't want to sanitize transcriptions, use the `--no-sanitize` flag:

```bash
python main.py video.mp4 --no-sanitize
```

This will only create the original transcription file without any replacements.

### Supported Video Formats

The script supports any video format that FFmpeg can process, including:
- MP4 (.mp4)
- MKV (.mkv)
- AVI (.avi)
- MOV (.mov)
- WMV (.wmv)
- FLV (.flv)
- And many more...

## GPU Support

The script automatically detects if a CUDA-compatible GPU is available:

- **With GPU**: Uses CUDA acceleration for faster transcription
- **Without GPU**: Falls back to CPU processing (slower but still functional)

To verify GPU support, the script will display the GPU information when it starts.

## Output

The script generates a text file containing the transcribed speech from the video. The output includes:

- Clean text transcription
- Automatic language detection
- Word-level alignment for accuracy

## Troubleshooting

### Common Issues and Solutions

#### 1. **"No module named 'julius'" Error**
**Problem**: The `julius` package fails to install properly through pip.

**Solution**:
```bash
# Install julius directly from GitHub
pip install git+https://github.com/adefossez/julius.git
```

This installs version 0.2.8a1 from source, which resolves compatibility issues with newer Python versions.

#### 2. **FFmpeg Not Found Error: "[WinError 2] The system cannot find the file specified"**
**Problem**: WhisperX cannot find FFmpeg to extract audio from video files.

**Solution for Windows**:

**Step 1**: Install FFmpeg using winget:
```powershell
winget install --id Gyan.FFmpeg -e --source winget
```

**Step 2**: After installation, you need to either:
- **Option A (Recommended)**: Restart your terminal/PowerShell window to load the new PATH
- **Option B**: The script has been modified to automatically add FFmpeg to PATH on Windows

**Step 3**: Verify FFmpeg is accessible:
```powershell
ffmpeg -version
```

**Note**: The `main.py` script now automatically adds the FFmpeg path for Windows users. If you installed FFmpeg in a custom location, update the path in `main.py`:
```python
ffmpeg_path = r"C:\Your\Custom\Path\To\FFmpeg\bin"
```

#### 3. **Virtual Environment Issues**
**Problem**: Python not found or packages not accessible after creating virtual environment.

**Solution**:
```powershell
# Always activate the virtual environment before running the script
.\venv\Scripts\Activate.ps1

# Or use the virtual environment Python directly
.\venv\Scripts\python.exe main.py "your-video.mp4"
```

#### 4. **"GPU not available" message**
**Problem**: Script falls back to CPU (slower but still works).

**Solution** (Optional - for faster processing):
   - Ensure you have a CUDA-compatible NVIDIA GPU
   - Install CUDA toolkit from NVIDIA
   - Reinstall PyTorch with CUDA support:
   ```bash
   pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
   - Verify installation with: `python -c "import torch; print(torch.cuda.is_available())"`

#### 5. **Out of memory errors**
**Solution**:
   - Reduce the batch size in the script (change `batch_size=16` to a lower value like `8` or `4`)
   - Use a smaller model (change `"large-v2"` to `"base"` or `"small"` in line 64 of `main.py`)

#### 6. **Model download issues**
**Solution**:
   - Ensure you have a stable internet connection for the first run
   - The models are cached locally after the first download (~3GB for large-v2)
   - Models are stored in: `%USERPROFILE%\.cache\huggingface\`

#### 7. **Deprecation Warnings**
**Note**: You may see warnings about `pkg_resources` and `torchaudio` being deprecated. These are informational warnings and do not affect functionality. They can be safely ignored.

### Performance Tips

- Use GPU acceleration for faster processing
- For very long videos, consider splitting them into smaller chunks
- The "large-v2" model provides the best accuracy but requires more resources
- For faster processing with slightly lower accuracy, use "base" or "medium" models

## Known Issues and Workarounds

### Issue: Julius Package Installation Failure
**Description**: Installing `julius` via pip may fail or install incorrectly, causing import errors.

**Workaround**: Always install julius from GitHub source:
```bash
pip install git+https://github.com/adefossez/julius.git
```

### Issue: FFmpeg Not Found After Installation (Windows)
**Description**: Even after installing FFmpeg, Python subprocesses cannot find it.

**Workaround**: The script has been modified to automatically add FFmpeg to PATH on Windows. If issues persist:
1. Restart your terminal after installing FFmpeg
2. Verify FFmpeg is in PATH: `ffmpeg -version`
3. If using a custom FFmpeg installation path, update line 10 in `main.py`:
   ```python
   ffmpeg_path = r"C:\Your\Custom\FFmpeg\Path\bin"
   ```

### Issue: Virtual Environment Python Not Found
**Description**: After creating a virtual environment, `python` command not found.

**Workaround**: Use the direct path to Python executable:
```powershell
.\venv\Scripts\python.exe main.py "your-video.mp4"
```

### Issue: Model Compatibility Warnings
**Description**: Warnings about model version mismatches (e.g., "Model was trained with pyannote.audio 0.0.1, yours is 3.4.0").

**Workaround**: These are informational warnings and can be safely ignored. The script will still function correctly, though you may experience slightly different results than with the original model versions.

## Model Information

This script uses WhisperX with the following models:
- **Transcription**: OpenAI Whisper large-v2 model
- **Alignment**: Language-specific alignment models for word-level timestamps

## License

This project uses WhisperX and OpenAI Whisper models. Please refer to their respective licenses for usage terms.

## Contributing

Feel free to submit issues and enhancement requests!
