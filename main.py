#!/usr/bin/env python3
"""
WhisperX Offline Transcription Script

This script uses WhisperX to transcribe audio from video files offline with GPU acceleration.

Usage:
    python main.py <video_file_path>

Example:
    python main.py test.mkv
"""

import sys
import os
import argparse
import re
from pathlib import Path

# Add FFmpeg to PATH for Windows
if os.name == 'nt':  # Windows
    ffmpeg_path = r"C:\Users\Admin\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin"
    if os.path.exists(ffmpeg_path):
        os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ.get("PATH", "")

import whisperx
import torch

# Import confidential terms configuration
try:
    from confidential_terms import CONFIDENTIAL_TERMS, ADVANCED_PATTERNS
except ImportError:
    # Fallback to default terms if config file not found
    CONFIDENTIAL_TERMS = {
        r'Anh chị': 'AC',
        r'anh chị': 'AC',
        r'Kiến thức': 'KT',
        r'kiến thức': 'KT',
    }
    ADVANCED_PATTERNS = []


def check_gpu_availability():
    """Check if GPU is available for PyTorch."""
    if torch.cuda.is_available():
        print(f"GPU available: {torch.cuda.get_device_name(0)}")
        return "cuda"
    else:
        print("GPU not available, falling back to CPU")
        return "cpu"


def sanitize_text(text):
    """
    Replace confidential information in the transcribed text.
    
    Args:
        text (str): Original text to sanitize
    
    Returns:
        str: Sanitized text with confidential information replaced
    """
    sanitized_text = text
    
    # Apply replacements from CONFIDENTIAL_TERMS (case-insensitive)
    for pattern, replacement in CONFIDENTIAL_TERMS.items():
        sanitized_text = re.sub(pattern, replacement, sanitized_text, flags=re.IGNORECASE)
    
    # Apply advanced patterns
    for pattern, replacement in ADVANCED_PATTERNS:
        sanitized_text = re.sub(pattern, replacement, sanitized_text)
    
    return sanitized_text


def transcribe_video(video_path, output_path=None, sanitize=True):
    """
    Transcribe video file using WhisperX.
    
    Args:
        video_path (str): Path to the input video file
        output_path (str, optional): Path for output text file. If None, uses video filename with .txt extension
        sanitize (bool, optional): Whether to sanitize confidential information. Default is True.
    
    Returns:
        bool: True if transcription successful, False otherwise
    """
    try:
        # Check if input file exists
        if not os.path.exists(video_path):
            print(f"Error: Video file '{video_path}' not found.")
            return False
        
        # Determine device
        device = check_gpu_availability()
        
        # Set up output path
        if output_path is None:
            video_name = Path(video_path).stem
            output_path = f"{video_name}.txt"
        
        print(f"Input video: {video_path}")
        print(f"Output text: {output_path}")
        print(f"Using device: {device}")
        
        # Load WhisperX model
        print("Loading WhisperX model...")
        model = whisperx.load_model("large-v2", device, compute_type="float16" if device == "cuda" else "int8")
        
        # Load audio from video
        print("Loading audio from video...")
        audio = whisperx.load_audio(video_path)
        
        # Transcribe
        print("Transcribing audio...")
        result = model.transcribe(audio, batch_size=16)
        
        # Load alignment model
        print("Loading alignment model...")
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        
        # Align whisper output
        print("Aligning transcription...")
        result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
        
        # Extract text from segments
        transcription_text = ""
        for segment in result["segments"]:
            transcription_text += segment["text"] + "\n"
        
        # Save original transcription to text file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transcription_text.strip())
        
        print(f"Original transcription saved to: {output_path}")
        
        # Sanitize and save redacted version if sanitize is enabled
        if sanitize:
            sanitized_text = sanitize_text(transcription_text)
            
            # Create sanitized filename
            base_name = Path(output_path).stem
            extension = Path(output_path).suffix
            sanitized_output_path = f"{base_name}_sanitized{extension}"
            
            # Save sanitized version
            with open(sanitized_output_path, 'w', encoding='utf-8') as f:
                f.write(sanitized_text.strip())
            
            print(f"Sanitized transcription saved to: {sanitized_output_path}")
        
        print(f"Transcription completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return False


def main():
    """Main function to handle command line arguments and run transcription."""
    parser = argparse.ArgumentParser(
        description="Transcribe video files using WhisperX offline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py test.mkv
    python main.py path/to/video.mp4
    python main.py "video with spaces.avi"
        """
    )
    
    parser.add_argument(
        "video_path",
        help="Path to the video file to transcribe"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output text file path (default: video_name.txt)",
        default=None
    )
    
    parser.add_argument(
        "--no-sanitize",
        help="Disable sanitization of confidential information",
        action="store_true"
    )
    
    # Parse arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    args = parser.parse_args()
    
    # Run transcription
    success = transcribe_video(args.video_path, args.output, sanitize=not args.no_sanitize)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()