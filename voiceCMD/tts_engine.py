"""
Text-to-Speech Engine module for VoiceLLM
Handles TTS generation with multiple engines and language detection
"""

import threading
import tempfile
import os
import re
from typing import Optional, Dict, List

# TTS Engines
try:
    from gtts import gTTS
    from gtts.lang import tts_langs
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

try:
    from elevenlabs import generate, save, set_api_key, voices
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    from pydub import AudioSegment
    from pydub.playback import play
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    import sounddevice as sd
    AUDIO_DEVICE_AVAILABLE = True
except ImportError:
    AUDIO_DEVICE_AVAILABLE = False

class TTSEngine:
    """Text-to-Speech Engine with multiple backend support"""
    
    def __init__(self):
        self.current_engine = "gtts"
        self.current_audio_device = None
        self.audio_devices = []
        self.speed_factor = 1.05  # Default 5% faster
        self.volume = 0.85
        
        # API keys
        self.azure_api_key = None
        self.azure_region = "eastus"
        self.elevenlabs_api_key = None
        
        self.setup_audio_devices()
        self.setup_engines()
    
    def setup_audio_devices(self):
        """Detect and setup available audio devices"""
        if not AUDIO_DEVICE_AVAILABLE:
            print("⚠️  sounddevice not available for audio device detection")
            return
        
        try:
            devices = sd.query_devices()
            print(f"🔍 Found {len(devices)} total audio devices")
            
            # Debug: Print device structure for first device
            if devices:
                print(f"📋 Sample device structure: {list(devices[0].keys())}")
            
            self.audio_devices = []
            
            for i, device in enumerate(devices):
                # Check if device has output capabilities
                # Different systems may have different device structures
                has_output = False
                
                # Try different possible field names for output channels
                if 'max_outputs' in device:
                    has_output = device['max_outputs'] > 0
                elif 'output_channels' in device:
                    has_output = device['output_channels'] > 0
                elif 'channels' in device:
                    # Some systems only show total channels
                    has_output = device['channels'] > 0
                elif 'name' in device:
                    # Fallback: check if device name suggests it's an output device
                    name_lower = device['name'].lower()
                    output_keywords = ['speaker', 'headphone', 'output', 'playback', 'audio']
                    has_output = any(keyword in name_lower for keyword in output_keywords)
                
                if has_output:
                    device_info = {
                        'id': i,
                        'name': device.get('name', f'Device {i}'),
                        'channels': device.get('max_outputs', device.get('output_channels', device.get('channels', 2))),
                        'sample_rate': device.get('default_samplerate', 44100),
                        'is_default': False  # Will be set below
                    }
                    self.audio_devices.append(device_info)
                    print(f"✅ Output device {i}: {device_info['name']}")
            
            # Try to identify default output device
            try:
                default_output = sd.query_devices(kind='output')
                default_name = default_output.get('name', '')
                print(f"🎯 System default output: {default_name}")
                
                # Mark the default device
                for device in self.audio_devices:
                    if device['name'] == default_name:
                        device['is_default'] = True
                        break
                else:
                    # If no match found, mark first device as default
                    if self.audio_devices:
                        self.audio_devices[0]['is_default'] = True
                        
            except Exception as e:
                print(f"Warning: Could not determine default output device: {e}")
                # Mark first device as default
                if self.audio_devices:
                    self.audio_devices[0]['is_default'] = True
            
            if self.audio_devices:
                default_device = next((d for d in self.audio_devices if d['is_default']), self.audio_devices[0])
                self.current_audio_device = default_device
                print(f"✅ TTS Audio device: {default_device['name']}")
                print(f"   Available devices: {len(self.audio_devices)}")
                for device in self.audio_devices:
                    default_marker = " (Default)" if device['is_default'] else ""
                    print(f"   - {device['name']}{default_marker}")
            else:
                print("⚠️  No audio output devices found")
                
        except Exception as e:
            print(f"❌ Error detecting audio devices: {e}")
            print("   Continuing without audio device selection...")
            # Create a fallback device
            self.audio_devices = [{
                'id': 0,
                'name': 'System Default',
                'channels': 2,
                'sample_rate': 44100,
                'is_default': True
            }]
            self.current_audio_device = self.audio_devices[0]
    
    def debug_audio_devices(self):
        """Debug function to print detailed audio device information"""
        if not AUDIO_DEVICE_AVAILABLE:
            print("sounddevice not available")
            return
        
        try:
            print("\n🔍 Audio Device Debug Information:")
            print("=" * 50)
            
            # Get all devices
            devices = sd.query_devices()
            print(f"Total devices found: {len(devices)}")
            
            for i, device in enumerate(devices):
                print(f"\nDevice {i}:")
                print(f"  Name: {device.get('name', 'Unknown')}")
                print(f"  Keys: {list(device.keys())}")
                
                # Print all available information
                for key, value in device.items():
                    print(f"  {key}: {value}")
            
            # Try to get default devices
            try:
                default_input = sd.query_devices(kind='input')
                print(f"\nDefault input: {default_input.get('name', 'Unknown')}")
            except Exception as e:
                print(f"Could not get default input: {e}")
            
            try:
                default_output = sd.query_devices(kind='output')
                print(f"Default output: {default_output.get('name', 'Unknown')}")
            except Exception as e:
                print(f"Could not get default output: {e}")
                
        except Exception as e:
            print(f"Error in debug_audio_devices: {e}")
    
    def setup_engines(self):
        """Initialize available TTS engines"""
        self.engines = {}
        
        if GTTS_AVAILABLE:
            self.engines["gtts"] = {
                "name": "Google TTS",
                "description": "High-quality neural voices, 100+ languages",
                "quality": "Excellent"
            }
        
        if AZURE_AVAILABLE:
            self.engines["azure"] = {
                "name": "Azure Speech",
                "description": "Professional neural voices, SSML support",
                "quality": "Professional"
            }
        
        if ELEVENLABS_AVAILABLE:
            self.engines["elevenlabs"] = {
                "name": "ElevenLabs AI",
                "description": "Ultra-realistic AI voices, voice cloning",
                "quality": "Ultra-Realistic"
            }
        
        if PYTTSX3_AVAILABLE:
            self.engines["pyttsx3"] = {
                "name": "Local System",
                "description": "Offline voices, system-dependent quality",
                "quality": "Basic"
            }
    
    def detect_language(self, text: str) -> str:
        """Detect language from text for TTS"""
        text_lower = text.lower()
        
        # Language detection patterns
        lang_patterns = {
            'es': ['hola', 'gracias', 'por favor', 'buenos días', 'adiós'],
            'fr': ['bonjour', 'merci', 's\'il vous plaît', 'au revoir'],
            'de': ['hallo', 'danke', 'bitte', 'auf wiedersehen'],
            'it': ['ciao', 'grazie', 'per favore', 'arrivederci'],
            'pt': ['olá', 'obrigado', 'por favor', 'adeus'],
            'ru': ['привет', 'спасибо', 'пожалуйста', 'до свидания'],
            'ja': ['こんにちは', 'ありがとう', 'お願い', 'さようなら'],
            'ko': ['안녕하세요', '감사합니다', '부탁합니다', '안녕히 가세요'],
            'zh': ['你好', '谢谢', '请', '再见']
        }
        
        for lang, patterns in lang_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                return lang
        
        return 'en'  # Default to English
    
    def set_engine(self, engine_name: str):
        """Set the TTS engine"""
        if engine_name in self.engines:
            self.current_engine = engine_name
            print(f"✅ TTS Engine set to: {self.engines[engine_name]['name']}")
            return True
        return False
    
    def set_audio_device(self, device_name: str):
        """Set the audio output device"""
        if not self.audio_devices:
            return False
        
        for device in self.audio_devices:
            if device['name'] == device_name:
                self.current_audio_device = device
                print(f"✅ TTS Audio device set to: {device['name']}")
                return True
        return False
    
    def set_speed(self, speed_factor: float):
        """Set speech speed (0.5 to 2.0)"""
        self.speed_factor = max(0.5, min(2.0, speed_factor))
    
    def set_volume(self, volume: float):
        """Set speech volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
    
    def set_azure_config(self, api_key: str, region: str = "eastus"):
        """Set Azure Speech configuration"""
        self.azure_api_key = api_key
        self.azure_region = region
    
    def set_elevenlabs_config(self, api_key: str):
        """Set ElevenLabs configuration"""
        self.elevenlabs_api_key = api_key
    
    def speak(self, text: str, callback=None) -> bool:
        """Speak text using the selected engine"""
        if not text.strip():
            return False
        
        # Run in separate thread to avoid blocking
        threading.Thread(
            target=self._speak_thread, 
            args=(text, callback), 
            daemon=True
        ).start()
        return True
    
    def _speak_thread(self, text: str, callback=None):
        """Thread function for speaking text"""
        try:
            if callback:
                callback("Generating speech...")
            
            if self.current_engine == "gtts":
                success = self._speak_gtts(text)
            elif self.current_engine == "azure":
                success = self._speak_azure(text)
            elif self.current_engine == "elevenlabs":
                success = self._speak_elevenlabs(text)
            elif self.current_engine == "pyttsx3":
                success = self._speak_pyttsx3(text)
            else:
                success = False
            
            if callback:
                callback("Speech completed!" if success else "Speech failed!")
                
        except Exception as e:
            print(f"TTS Error: {e}")
            if callback:
                callback(f"TTS Error: {str(e)}")
    
    def _speak_gtts(self, text: str) -> bool:
        """Speak text using Google TTS"""
        if not GTTS_AVAILABLE:
            return False
        
        try:
            lang = self.detect_language(text)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                temp_path = tmp_file.name
            
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(temp_path)
            
            if AUDIO_AVAILABLE:
                audio = AudioSegment.from_mp3(temp_path)
                
                # Apply speed adjustment
                if self.speed_factor != 1.0:
                    new_frame_rate = int(audio.frame_rate * self.speed_factor)
                    audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_frame_rate})
                    audio = audio.set_frame_rate(audio.frame_rate)
                
                # Apply volume adjustment
                if self.volume != 1.0:
                    audio = audio + (20 * (self.volume - 1.0))  # Convert to dB
                
                # Play through selected device
                if AUDIO_DEVICE_AVAILABLE and self.current_audio_device:
                    try:
                        import numpy as np
                        samples = np.array(audio.get_array_of_samples())
                        if audio.channels == 2:
                            samples = samples.reshape((-1, 2))
                        
                        sd.play(samples, audio.frame_rate, device=self.current_audio_device['id'])
                        sd.wait()
                    except Exception as e:
                        print(f"Warning: Could not play through selected device: {e}")
                        print("Falling back to default audio playback...")
                        play(audio)
                else:
                    play(audio)
            else:
                os.system(f"start {temp_path}" if os.name == 'nt' else f"open {temp_path}")
            
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
            return True
            
        except Exception as e:
            print(f"Google TTS Error: {e}")
            return False
    
    def _speak_azure(self, text: str) -> bool:
        """Speak text using Azure Speech"""
        if not AZURE_AVAILABLE or not self.azure_api_key:
            return False
        
        try:
            speech_config = speechsdk.SpeechConfig(
                subscription=self.azure_api_key, 
                region=self.azure_region
            )
            speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
            
            # Apply speed adjustment using SSML
            if self.speed_factor != 1.0:
                ssml_text = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US"><voice name="en-US-JennyNeural"><prosody rate="{self.speed_factor}">{text}</prosody></voice></speak>'
                speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
                result = speech_synthesizer.speak_ssml_async(ssml_text).get()
            else:
                speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
                result = speech_synthesizer.speak_text_async(text).get()
            
            return result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted
            
        except Exception as e:
            print(f"Azure TTS Error: {e}")
            return False
    
    def _speak_elevenlabs(self, text: str) -> bool:
        """Speak text using ElevenLabs"""
        if not ELEVENLABS_AVAILABLE or not self.elevenlabs_api_key:
            return False
        
        try:
            set_api_key(self.elevenlabs_api_key)
            available_voices = voices()
            if not available_voices:
                return False
            
            voice_id = available_voices[0].voice_id
            audio = generate(text=text, voice=voice_id)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                temp_path = tmp_file.name
            
            save(audio, temp_path)
            
            if AUDIO_AVAILABLE:
                audio_segment = AudioSegment.from_mp3(temp_path)
                
                # Apply speed adjustment
                if self.speed_factor != 1.0:
                    new_frame_rate = int(audio_segment.frame_rate * self.speed_factor)
                    audio_segment = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_frame_rate})
                    audio_segment = audio_segment.set_frame_rate(audio_segment.frame_rate)
                
                # Apply volume adjustment
                if self.volume != 1.0:
                    audio_segment = audio_segment + (20 * (self.volume - 1.0))
                
                # Play through selected device
                if AUDIO_DEVICE_AVAILABLE and self.current_audio_device:
                    try:
                        import numpy as np
                        samples = np.array(audio_segment.get_array_of_samples())
                        if audio_segment.channels == 2:
                            samples = samples.reshape((-1, 2))
                        
                        sd.play(samples, audio_segment.frame_rate, device=self.current_audio_device['id'])
                        sd.wait()
                    except Exception as e:
                        print(f"Warning: Could not play through selected device: {e}")
                        print("Falling back to default audio playback...")
                        play(audio_segment)
                else:
                    play(audio_segment)
            else:
                os.system(f"start {temp_path}" if os.name == 'nt' else f"open {temp_path}")
            
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            
            return True
            
        except Exception as e:
            print(f"ElevenLabs TTS Error: {e}")
            return False
    
    def _speak_pyttsx3(self, text: str) -> bool:
        """Speak text using pyttsx3"""
        if not PYTTSX3_AVAILABLE:
            return False
        
        try:
            engine = pyttsx3.init()
            
            # Apply speed adjustment
            base_rate = 150
            adjusted_rate = int(base_rate * self.speed_factor)
            engine.setProperty('rate', adjusted_rate)
            engine.setProperty('volume', self.volume)
            
            engine.say(text)
            engine.runAndWait()
            return True
            
        except Exception as e:
            print(f"pyttsx3 TTS Error: {e}")
            return False
    
    def get_available_engines(self) -> Dict[str, Dict]:
        """Get available TTS engines"""
        return self.engines
    
    def get_available_devices(self) -> List[Dict]:
        """Get available audio devices"""
        return self.audio_devices
    
    def get_current_engine(self) -> str:
        """Get current TTS engine name"""
        return self.current_engine
    
    def get_current_device(self) -> Optional[Dict]:
        """Get current audio device"""
        return self.current_audio_device
