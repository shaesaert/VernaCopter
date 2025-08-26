#!/usr/bin/env python3
"""
Debug script for VoiceCMD transcription system
Utility script to test and debug transcription functionality.

This script provides:
- Direct transcription testing
- Audio recording verification
- Whisper model testing
- Voice activity detection testing
"""

import sys
import os
import numpy as np

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_transcription_directly():
    """Test transcription directly with sample audio."""
    
    print("🔍 Testing transcription directly...")
    
    try:
        from .transcriber import Transcriber
        from .audio_processor import AudioProcessor
        
        # Initialize components
        transcriber = Transcriber()
        audio_processor = AudioProcessor()
        
        print(f"✅ Transcriber initialized")
        print(f"✅ Audio processor initialized: {audio_processor.samplerate}Hz")
        
        # Record a test audio chunk
        print("🎙️ Recording test audio (3 seconds)...")
        print("   Please speak clearly: 'Hello, this is a test'")
        
        audio_chunk = audio_processor.record_chunk(3.0)
        
        if len(audio_chunk) == 0:
            print("❌ No audio recorded")
            return False
        
        print(f"✅ Audio recorded: {len(audio_chunk)} samples")
        
        # Check audio properties
        audio_level = np.max(np.abs(audio_chunk))
        print(f"📊 Audio level: {audio_level:.6f}")
        print(f"📊 Audio range: {np.min(audio_chunk):.6f} to {np.max(audio_chunk):.6f}")
        
        # Resample to 16kHz
        audio_16k = audio_processor.resample_to_16k(audio_chunk, audio_processor.samplerate)
        print(f"✅ Resampled to 16kHz: {len(audio_16k)} samples")
        
        # Check if audio is valid for Whisper
        if len(audio_16k) == 0:
            print("❌ Resampled audio is empty")
            return False
        
        # Test voice activity detection
        voice_level = audio_processor.detect_voice_activity(audio_16k)
        print(f"🎤 Voice level: {voice_level:.6f}")
        
        # Test transcription directly
        print("🤖 Testing transcription...")
        try:
            text = transcriber.transcribe_chunk(audio_16k)
            print(f"📝 Transcription result: '{text}'")
            
            if text and text.strip():
                print("✅ Transcription successful!")
                return True
            else:
                print("❌ Transcription returned empty result")
                return False
                
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_whisper_directly():
    """Test Whisper directly with a simple audio."""
    
    print("\n🤖 Testing Whisper directly...")
    
    try:
        import whisper
        
        # Load model
        print("🔄 Loading Whisper model...")
        model = whisper.load_model("base")  # Use base model for faster testing
        print("✅ Whisper model loaded")
        
        # Create a simple test audio (sine wave)
        print("🎵 Creating test audio...")
        sample_rate = 16000
        duration = 2.0
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        test_audio = np.sin(2 * np.pi * frequency * t) * 0.1  # Low amplitude
        test_audio = test_audio.astype(np.float32)
        
        print(f"✅ Test audio created: {len(test_audio)} samples")
        
        # Test transcription
        print("🔄 Testing transcription...")
        result = model.transcribe(test_audio)
        print(f"📝 Test result: '{result['text']}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct Whisper test failed: {e}")
        return False

def main():
    """Main debug function."""
    print("🔧 VoiceCMD Transcription Debug Tool")
    print("=" * 50)
    
    # Test 1: Direct Whisper
    whisper_ok = test_whisper_directly()
    
    # Test 2: Full transcription pipeline
    transcription_ok = test_transcription_directly()
    
    print("\n" + "=" * 50)
    print("Debug Results:")
    print(f"Whisper Test: {'✅ PASSED' if whisper_ok else '❌ FAILED'}")
    print(f"Transcription Test: {'✅ PASSED' if transcription_ok else '❌ FAILED'}")
    
    if whisper_ok and transcription_ok:
        print("\n🎉 All tests passed! Transcription system is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()
