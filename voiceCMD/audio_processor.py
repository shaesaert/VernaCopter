"""
Audio processing module for VoiceCMD
Handles audio recording, resampling, and voice activity detection.

This module provides:
- Audio device initialization and sample rate detection
- Audio recording with fallback sample rates
- Resampling to 16kHz for Whisper compatibility
- Simple voice activity detection using RMS
- Audio caching for performance optimization
"""

import sounddevice as sd
import numpy as np
import time
from .config import *

class AudioProcessor:
    """
    Audio processor for voice recording and processing.
    
    Handles audio device initialization, recording, resampling,
    and voice activity detection for the voice-enabled system.
    """
    
    def __init__(self):
        """Initialize the audio processor with optimal settings."""
        self.samplerate = SAMPLERATE
        self.audio_cache = {}  # Cache for resampled audio
        self.initialize_audio()
    
    def initialize_audio(self):
        """
        Initialize audio system and find compatible sample rate.
        
        Tests different sample rates in order of preference and
        selects the first one that works with the current audio device.
        """
        print("Initializing audio system...")
        
        for rate in AUDIO_TEST_RATES:
            try:
                # Try to record a very short test chunk
                test_audio = sd.rec(int(0.1 * rate), samplerate=rate, 
                                  channels=AUDIO_CHANNELS, dtype=AUDIO_DTYPE, blocking=True)
                if test_audio is not None and len(test_audio) > 0:
                    print(f"Audio system initialized successfully with sample rate: {rate}")
                    self.samplerate = rate
                    return
            except Exception as e:
                print(f"Sample rate {rate} failed: {e}")
                continue
        
        print(f"Using default sample rate: {self.samplerate}")
    
    def record_chunk(self, duration):
        """
        Record an audio chunk with fallback sample rates.
        
        Args:
            duration (float): Duration of audio to record in seconds
            
        Returns:
            numpy.ndarray: Recorded audio data as float32 array
        """
        # Try different sample rates if the primary one fails
        sample_rates = [self.samplerate, 48000, 44100, 22050, 16000]
        
        for sr in sample_rates:
            try:
                audio = sd.rec(int(duration * sr), 
                              samplerate=sr, 
                              channels=AUDIO_CHANNELS, 
                              dtype=AUDIO_DTYPE,
                              blocking=True)
                result = audio.flatten().astype(np.float32)
                
                if sr != self.samplerate:
                    print(f"Recording successful with sample rate {sr} (fallback from {self.samplerate})")
                return result
                
            except Exception as e:
                print(f"Recording failed with sample rate {sr}: {e}")
                continue
        
        print("All sample rates failed, returning empty audio")
        return np.array([], dtype=np.float32)
    
    def resample_to_16k(self, x, sr):
        """
        Optimized resampling to 16kHz with caching.
        
        Args:
            x (numpy.ndarray): Input audio data
            sr (int): Source sample rate
            
        Returns:
            numpy.ndarray: Resampled audio data at 16kHz
        """
        target_sr = 16000
        if sr == target_sr:
            return x.astype(np.float32)

        # Create cache key
        cache_key = f"{len(x)}_{sr}"
        
        # Check cache first
        if ENABLE_AUDIO_CACHING and cache_key in self.audio_cache:
            return self.audio_cache[cache_key]

        # Optimized resampling for common sample rates
        if sr == 44100:
            # Fast decimation for 44.1kHz
            step = int(sr / target_sr)
            y = x[::step].astype(np.float32)
        elif sr == 48000:
            # Fast decimation for 48kHz
            y = x[::3].astype(np.float32)
        else:
            # Fallback to simple interpolation
            n_new = int(round(len(x) * target_sr / sr))
            if n_new == 0:
                return np.array([], dtype=np.float32)
            
            # Simple linear interpolation
            t_old = np.linspace(0, 1, num=len(x), endpoint=False, dtype=np.float64)
            t_new = np.linspace(0, 1, num=n_new, endpoint=False, dtype=np.float64)
            y = np.interp(t_new, t_old, x).astype(np.float32)
        
        # Cache the result
        if ENABLE_AUDIO_CACHING:
            self.audio_cache[cache_key] = y
            # Limit cache size
            if len(self.audio_cache) > 100:
                # Remove oldest entries
                oldest_key = next(iter(self.audio_cache))
                del self.audio_cache[oldest_key]
        
        return y
    
    def detect_voice_activity(self, audio_chunk):
        """
        Simple voice activity detection using RMS.
        
        Args:
            audio_chunk (numpy.ndarray): Audio data to analyze
            
        Returns:
            float: Voice activity level (RMS value)
        """
        if len(audio_chunk) == 0:
            return 0.0
        
        # Simple RMS calculation
        rms = np.sqrt(np.mean(audio_chunk**2))
        return rms
