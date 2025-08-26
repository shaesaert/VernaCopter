"""
Audio Processing Loop module for VoiceCMD
Handles the main audio processing and transcription loop.

This module provides:
- Continuous audio recording and processing
- Voice activity detection and silence-based transcription
- Performance monitoring and statistics
- Session management for conversation flow
"""

import threading
import queue
import time
import re
import numpy as np
from .config import *

class AudioProcessingLoop:
    """
    Main audio processing loop for voice transcription.
    
    Handles continuous audio recording, voice activity detection,
    and transcription triggering based on silence patterns.
    """
    
    def __init__(self, audio_processor, transcriber, text_queue):
        """
        Initialize the audio processing loop.
        Args:
            audio_processor (AudioProcessor): Audio processing instance
            transcriber (Transcriber): Transcription instance
            text_queue (queue.Queue): Queue for transcribed text output
        """
        self.audio_processor = audio_processor
        self.transcriber = transcriber
        self.text_queue = text_queue
        self.is_recording = False
        self.last_transcription_time = 0
        self.audio_thread = None
        
        # Performance monitoring
        if ENABLE_PERFORMANCE_MONITORING:
            self.transcription_count = 0
            self.total_processing_time = 0.0
            self.last_performance_update = time.time()
    
    def start_processing(self):
        """Start the audio processing thread."""
        self.audio_thread = threading.Thread(target=self.audio_processing_loop, daemon=True)
        self.audio_thread.start()
    
    def set_recording_state(self, is_recording):
        """
        Set the recording state.
        
        Args:
            is_recording (bool): True to start recording, False to stop
        """
        self.is_recording = is_recording
    
    def audio_processing_loop(self):
        """
        Main audio processing loop with silence-based transcription.
        
        Continuously records audio, detects voice activity, and triggers
        transcription when sufficient silence is detected (indicating
        the end of a sentence or phrase).
        """
        current_session_text = []
        audio_buffer = []  # Buffer to accumulate audio
        last_voice_time = 0  # Track when we last heard voice
        
        while True:
            if self.is_recording:
                try:
                    current_time = time.time()
                    
                    # Record audio chunk
                    audio_chunk = self.audio_processor.record_chunk(CHUNK_DURATION)
                    
                    # Skip processing if no audio data
                    if len(audio_chunk) == 0:
                        continue
                    
                    # Add to audio buffer (limit size for performance)
                    audio_buffer.append(audio_chunk)
                    if len(audio_buffer) > MAX_AUDIO_BUFFER_SIZE:
                        audio_buffer.pop(0)  # Remove oldest chunk
                    
                    # Resample to 16kHz
                    audio_chunk_16k = self.audio_processor.resample_to_16k(audio_chunk, self.audio_processor.samplerate)
                    
                    # Voice activity detection
                    voice_level = self.audio_processor.detect_voice_activity(audio_chunk_16k)
                    
                    # Update voice timing
                    if voice_level > MIN_VOICE_LEVEL:
                        last_voice_time = current_time
                    
                    # Calculate silence duration
                    silence_duration = current_time - last_voice_time
                    
                    # Transcribe when there's been enough silence (indicating end of sentence)
                    if (len(audio_buffer) > 0 and 
                        silence_duration > SILENCE_PAUSE_THRESHOLD and 
                        current_time - self.last_transcription_time > TRANSCRIPTION_COOLDOWN):
                        
                        # Combine all buffered audio for complete sentence
                        combined_audio = np.concatenate(audio_buffer)
                        combined_audio_16k = self.audio_processor.resample_to_16k(combined_audio, self.audio_processor.samplerate)
                        
                        # Transcribe the audio with performance monitoring
                        start_time = time.time()
                        text = self.transcriber.transcribe_chunk(combined_audio_16k)
                        processing_time = time.time() - start_time
                        
                        if text:
                            print(f"Transcribed: {text} (Time: {processing_time:.3f}s)")
                            
                            # Update performance metrics
                            if ENABLE_PERFORMANCE_MONITORING:
                                self.transcription_count += 1
                                self.total_processing_time += processing_time
                                
                                # Print performance stats every 10 transcriptions
                                if self.transcription_count % 10 == 0:
                                    avg_time = self.total_processing_time / self.transcription_count
                                    print(f"Performance: Avg transcription time: {avg_time:.3f}s, Total: {self.transcription_count}")
                            
                            # Add to current session
                            current_session_text.append(text)
                            
                            # Update last transcription time
                            self.last_transcription_time = current_time
                        
                        # Clear audio buffer after transcription
                        audio_buffer = []
                        
                except Exception as e:
                    print(f"Audio processing error: {e}")
            else:
                # When recording stops, process any remaining audio
                if len(audio_buffer) > 0:
                    try:
                        # Process any remaining audio
                        combined_audio = np.concatenate(audio_buffer)
                        combined_audio_16k = self.audio_processor.resample_to_16k(combined_audio, self.audio_processor.samplerate)
                        text = self.transcriber.transcribe_chunk(combined_audio_16k)
                        
                        if text:
                            current_session_text.append(text)
                    except Exception as e:
                        print(f"Error processing final audio: {e}")
                
                # Process the complete session
                if current_session_text:
                    full_message = re.sub(r"\s+", " ", " ".join(current_session_text)).strip()
                    if full_message:
                        print(f"Complete session: {full_message}")
                        self.text_queue.put(("full", full_message))
                
                # Reset for next session
                current_session_text = []
                audio_buffer = []
                last_voice_time = 0
                
                time.sleep(0.05)  # Reduced delay for faster response
