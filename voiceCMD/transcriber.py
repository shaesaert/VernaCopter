"""
Transcription module for VoiceCMD
Handles Whisper model loading and audio transcription.

This module provides:
- Whisper model loading and management
- Audio transcription with optimized settings
- Fallback to base model if loading fails
- Model switching capabilities
"""

import whisper
import numpy as np
from .config import *

class Transcriber:
    """
    Whisper-based audio transcription system.
    
    Handles loading and managing Whisper models, and provides
    optimized transcription for voice input.
    """
    
    def __init__(self, model_name=DEFAULT_MODEL):
        """
        Initialize the transcriber with specified model.
        
        Args:
            model_name (str): Name of the Whisper model to load
        """
        self.model = None
        self.load_model(model_name)
    
    def load_model(self, model_name):
        """
        Load Whisper model with fallback to base model.
        
        Args:
            model_name (str): Name of the Whisper model to load
        """
        try:
            print(f"Loading {model_name} model...")
            self.model = whisper.load_model(model_name)
            print(f"Model {model_name} loaded successfully!")
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            # Fallback to base model
            print("Falling back to base model...")
            self.model = whisper.load_model("base")
    
    def transcribe_chunk(self, audio_chunk):
        """
        Transcribe an audio chunk using Whisper.
        
        Args:
            audio_chunk (numpy.ndarray): Audio data to transcribe
            
        Returns:
            str: Transcribed text, or empty string if no speech detected
        """
        try:
            # Check if audio chunk has sufficient content
            if len(audio_chunk) == 0 or np.max(np.abs(audio_chunk)) < MIN_VOICE_LEVEL:
                return ""
            
            # Use optimized Whisper settings for speed and accuracy balance
            result = self.model.transcribe(
                audio_chunk, 
                fp16=False,  # Keep fp16=False for better accuracy
                language="en",
                task="transcribe",
                verbose=False,  # Reduce console output
                condition_on_previous_text=False,  # Disable for faster processing
                # temperature=0.0,  # Use deterministic decoding for consistency
                best_of=1,  # Use best decoding
                beam_size=1,  # Use beam search for better results
                compression_ratio_threshold=2.4,  # Optimize for speed
                logprob_threshold=-1.0,  # Optimize for speed
                no_speech_threshold=0.6  # Optimize for speed
            )
            
            # Return the transcribed text
            return result["text"].strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def change_model(self, model_name):
        """
        Change the Whisper model.
        
        Args:
            model_name (str): Name of the new Whisper model to load
            
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            print(f"Loading {model_name} model...")
            self.model = whisper.load_model(model_name)
            print(f"Successfully loaded {model_name} model!")
            return True
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            return False
