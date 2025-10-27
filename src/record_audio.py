#!/usr/bin/env python3
"""
Audio Recording Module
Records system audio and/or microphone input simultaneously.

Usage:
    python record_audio.py [options]

Example:
    python record_audio.py --duration 60 --output meeting.wav
    python record_audio.py --microphone-only --duration 30
    python record_audio.py --system-only --output desktop_audio.wav
"""

import os
import sys
import argparse
import threading
import time
import wave
import numpy as np
from pathlib import Path
from datetime import datetime

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("Warning: pyaudio not installed. Install with: pip install pyaudio")

try:
    import soundcard as sc
    SOUNDCARD_AVAILABLE = True
except ImportError:
    SOUNDCARD_AVAILABLE = False
    print("Warning: soundcard not installed. Install with: pip install soundcard")


# Audio settings
SAMPLE_RATE = 44100  # Hz
CHANNELS = 2  # Stereo
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None


class AudioRecorder:
    """Handle audio recording from multiple sources."""
    
    def __init__(self, sample_rate=SAMPLE_RATE, channels=CHANNELS):
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_recording = False
        self.frames = []
        
    def record_microphone(self, duration=None, device_index=None):
        """
        Record from microphone using PyAudio.
        
        Args:
            duration: Recording duration in seconds (None for manual stop)
            device_index: Specific device index (None for default)
            
        Returns:
            list: Recorded audio frames
        """
        if not PYAUDIO_AVAILABLE:
            print("Error: PyAudio not available")
            return []
        
        audio = pyaudio.PyAudio()
        
        try:
            # List available devices
            print("\n📱 Available microphone devices:")
            for i in range(audio.get_device_count()):
                info = audio.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    print(f"  [{i}] {info['name']}")
            
            # Open stream
            if device_index is not None:
                print(f"\nUsing device [{device_index}]")
            else:
                print("\nUsing default microphone")
            
            stream = audio.open(
                format=FORMAT,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK_SIZE
            )
            
            print("\n🎤 Recording microphone...")
            print("Press Ctrl+C to stop" if duration is None else f"Recording for {duration} seconds...")
            
            self.frames = []
            self.is_recording = True
            start_time = time.time()
            
            while self.is_recording:
                if duration and (time.time() - start_time) >= duration:
                    break
                
                try:
                    data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                    self.frames.append(data)
                    
                    # Progress indicator
                    if duration:
                        elapsed = time.time() - start_time
                        print(f"\rRecording: {elapsed:.1f}s / {duration}s", end='', flush=True)
                except KeyboardInterrupt:
                    break
            
            print("\n✓ Microphone recording complete")
            
            stream.stop_stream()
            stream.close()
            
        finally:
            audio.terminate()
        
        return self.frames
    
    def record_system_audio(self, duration=None, loopback_device=None):
        """
        Record system audio (desktop audio) using soundcard.
        
        Args:
            duration: Recording duration in seconds (None for manual stop)
            loopback_device: Specific loopback device (None for default)
            
        Returns:
            numpy.ndarray: Recorded audio data
        """
        if not SOUNDCARD_AVAILABLE:
            print("Error: soundcard not available")
            return np.array([])
        
        try:
            # Get default loopback device
            if loopback_device is None:
                try:
                    loopback_device = sc.default_speaker()
                    print(f"\n🔊 Using default speaker (loopback): {loopback_device.name}")
                except:
                    print("\n⚠️ Warning: Could not access default speaker loopback")
                    print("Available speakers:")
                    for speaker in sc.all_speakers():
                        print(f"  - {speaker.name}")
                    return np.array([])
            
            print("\n🔊 Recording system audio...")
            print("Press Ctrl+C to stop" if duration is None else f"Recording for {duration} seconds...")
            
            # Record with context manager
            with loopback_device.recorder(samplerate=self.sample_rate, channels=self.channels) as recorder:
                if duration:
                    data = recorder.record(numframes=int(self.sample_rate * duration))
                else:
                    # Manual recording
                    recorded_data = []
                    start_time = time.time()
                    try:
                        while True:
                            data = recorder.record(numframes=CHUNK_SIZE)
                            recorded_data.append(data)
                            elapsed = time.time() - start_time
                            print(f"\rRecording: {elapsed:.1f}s", end='', flush=True)
                    except KeyboardInterrupt:
                        data = np.concatenate(recorded_data) if recorded_data else np.array([])
            
            print("\n✓ System audio recording complete")
            return data
            
        except Exception as e:
            print(f"Error recording system audio: {e}")
            return np.array([])
    
    def record_both(self, duration, mic_device=None, system_device=None):
        """
        Record both microphone and system audio simultaneously.
        
        Args:
            duration: Recording duration in seconds
            mic_device: Microphone device index
            system_device: System audio device
            
        Returns:
            tuple: (mic_frames, system_data)
        """
        print("\n" + "="*60)
        print("DUAL AUDIO RECORDING")
        print("="*60)
        print(f"\n⏱️  Duration: {duration} seconds")
        print("🎤 Recording microphone + 🔊 system audio simultaneously")
        
        mic_frames = []
        system_data = np.array([])
        
        # Threading for simultaneous recording
        def record_mic():
            nonlocal mic_frames
            mic_frames = self.record_microphone(duration, mic_device)
        
        def record_system():
            nonlocal system_data
            system_data = self.record_system_audio(duration, system_device)
        
        # Start both recordings
        mic_thread = threading.Thread(target=record_mic)
        system_thread = threading.Thread(target=record_system)
        
        mic_thread.start()
        system_thread.start()
        
        # Wait for both to complete
        mic_thread.join()
        system_thread.join()
        
        return mic_frames, system_data
    
    def save_wav(self, frames, output_file):
        """
        Save audio frames to WAV file (for PyAudio format).
        
        Args:
            frames: Audio frames from PyAudio
            output_file: Output file path
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with wave.open(str(output_path), 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))
        
        file_size = output_path.stat().st_size
        print(f"\n✓ Saved: {output_path}")
        print(f"  Size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    
    def save_numpy_wav(self, data, output_file):
        """
        Save numpy audio data to WAV file (for soundcard format).
        
        Args:
            data: Numpy array audio data
            output_file: Output file path
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Normalize to int16
        data_int16 = (data * 32767).astype(np.int16)
        
        with wave.open(str(output_path), 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(data_int16.tobytes())
        
        file_size = output_path.stat().st_size
        print(f"\n✓ Saved: {output_path}")
        print(f"  Size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    
    def merge_audio(self, mic_frames, system_data, output_file):
        """
        Merge microphone and system audio into single file.
        
        Args:
            mic_frames: Microphone audio frames
            system_data: System audio numpy data
            output_file: Output file path
        """
        print("\n🔀 Merging audio streams...")
        
        # Convert mic frames to numpy
        if mic_frames:
            mic_bytes = b''.join(mic_frames)
            mic_array = np.frombuffer(mic_bytes, dtype=np.int16)
            mic_float = mic_array.astype(np.float32) / 32767.0
            
            # Reshape to channels
            if self.channels == 2:
                mic_float = mic_float.reshape(-1, 2)
        else:
            mic_float = np.zeros_like(system_data)
        
        # Ensure same length
        min_len = min(len(mic_float), len(system_data))
        mic_float = mic_float[:min_len]
        system_data = system_data[:min_len]
        
        # Mix: 50% mic + 50% system
        mixed = (mic_float * 0.5 + system_data * 0.5)
        
        # Save merged audio
        self.save_numpy_wav(mixed, output_file)
        print("✓ Audio streams merged successfully")


def list_devices():
    """List all available audio devices."""
    print("\n" + "="*60)
    print("AVAILABLE AUDIO DEVICES")
    print("="*60)
    
    if PYAUDIO_AVAILABLE:
        print("\n📱 Input Devices (Microphones):")
        audio = pyaudio.PyAudio()
        for i in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                default = " [DEFAULT]" if i == audio.get_default_input_device_info()['index'] else ""
                print(f"  [{i}] {info['name']}{default}")
                print(f"      Channels: {info['maxInputChannels']}, Sample Rate: {int(info['defaultSampleRate'])} Hz")
        audio.terminate()
    
    if SOUNDCARD_AVAILABLE:
        print("\n🔊 Output Devices (Speakers - for loopback):")
        for i, speaker in enumerate(sc.all_speakers()):
            default = " [DEFAULT]" if speaker == sc.default_speaker() else ""
            print(f"  [{i}] {speaker.name}{default}")
    
    print("\n" + "="*60)


def record_audio(duration=None, output=None, microphone_only=False, system_only=False,
                mic_device=None, system_device=None):
    """
    Main recording function.
    
    Args:
        duration: Recording duration in seconds
        output: Output file path
        microphone_only: Record only microphone
        system_only: Record only system audio
        mic_device: Microphone device index
        system_device: System audio device index
    """
    # Check dependencies
    if not PYAUDIO_AVAILABLE and not SOUNDCARD_AVAILABLE:
        print("Error: Neither PyAudio nor soundcard is installed")
        print("\nInstall with:")
        print("  pip install pyaudio soundcard")
        sys.exit(1)
    
    # Generate output filename if not provided
    if not output:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if microphone_only:
            output = f"videos/recording_mic_{timestamp}.wav"
        elif system_only:
            output = f"videos/recording_system_{timestamp}.wav"
        else:
            output = f"videos/recording_mixed_{timestamp}.wav"
    
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*60)
    print("AUDIO RECORDER")
    print("="*60)
    print(f"\n📁 Output: {output}")
    print(f"⏱️  Duration: {'Manual (Ctrl+C to stop)' if duration is None else f'{duration} seconds'}")
    
    recorder = AudioRecorder()
    
    try:
        if microphone_only:
            # Record microphone only
            frames = recorder.record_microphone(duration, mic_device)
            recorder.save_wav(frames, output)
            
        elif system_only:
            # Record system audio only
            data = recorder.record_system_audio(duration, system_device)
            if len(data) > 0:
                recorder.save_numpy_wav(data, output)
            else:
                print("❌ No system audio recorded")
                sys.exit(1)
        
        else:
            # Record both and merge
            if not duration:
                print("\nError: Duration is required for dual recording")
                print("Use --duration <seconds>")
                sys.exit(1)
            
            mic_frames, system_data = recorder.record_both(duration, mic_device, system_device)
            
            if mic_frames and len(system_data) > 0:
                recorder.merge_audio(mic_frames, system_data, output)
            elif mic_frames:
                print("\n⚠️ Only microphone recorded, saving...")
                recorder.save_wav(mic_frames, output)
            elif len(system_data) > 0:
                print("\n⚠️ Only system audio recorded, saving...")
                recorder.save_numpy_wav(system_data, output)
            else:
                print("❌ No audio recorded")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Recording interrupted by user")
        if recorder.frames:
            print("Saving partial recording...")
            recorder.save_wav(recorder.frames, output)
    
    print("\n" + "="*60)
    print("RECORDING COMPLETE")
    print("="*60)
    print(f"\n✓ Audio saved to: {output}")
    print("\nNext steps:")
    print(f"  # Transcribe the recording:")
    print(f"  python src/process_video_complete.py \"{output}\"")
    print(f"\n  # Transcribe + translate:")
    print(f"  python src/process_video_complete.py \"{output}\" --translate English")
    
    return output


def main():
    parser = argparse.ArgumentParser(
        description='Record audio from microphone and/or system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Record both mic + system for 60 seconds:
  python record_audio.py --duration 60
  
  # Record microphone only for 30 seconds:
  python record_audio.py --duration 30 --microphone-only
  
  # Record system audio only:
  python record_audio.py --duration 60 --system-only
  
  # Custom output file:
  python record_audio.py --duration 120 --output videos/meeting.wav
  
  # Manual stop (press Ctrl+C):
  python record_audio.py --microphone-only
  
  # List available devices:
  python record_audio.py --list-devices
  
  # Use specific microphone:
  python record_audio.py --duration 60 --mic-device 1

Then process the recording:
  python src/process_video_complete.py videos/recording.wav --translate English
        """
    )
    
    parser.add_argument('--duration', '-d', type=int,
                       help='Recording duration in seconds (required for dual recording)')
    parser.add_argument('--output', '-o',
                       help='Output file path (default: auto-generated in videos/)')
    parser.add_argument('--microphone-only', '-m', action='store_true',
                       help='Record only microphone input')
    parser.add_argument('--system-only', '-s', action='store_true',
                       help='Record only system audio (desktop audio)')
    parser.add_argument('--mic-device', type=int,
                       help='Microphone device index (see --list-devices)')
    parser.add_argument('--system-device', type=int,
                       help='System audio device index (see --list-devices)')
    parser.add_argument('--list-devices', '-l', action='store_true',
                       help='List all available audio devices and exit')
    
    args = parser.parse_args()
    
    # List devices and exit
    if args.list_devices:
        list_devices()
        sys.exit(0)
    
    # Validate arguments
    if not args.microphone_only and not args.system_only:
        if not args.duration:
            print("Error: --duration is required for dual recording (mic + system)")
            print("Or use --microphone-only or --system-only for manual stop")
            sys.exit(1)
    
    # Start recording
    record_audio(
        duration=args.duration,
        output=args.output,
        microphone_only=args.microphone_only,
        system_only=args.system_only,
        mic_device=args.mic_device,
        system_device=args.system_device
    )


if __name__ == '__main__':
    main()
