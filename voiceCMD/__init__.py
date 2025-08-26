"""
VoiceCMD Package
A voice-enabled interface for VernaCopter NL_to_STL system.

This package provides:
- Real-time speech-to-text transcription using Whisper
- Text-to-speech synthesis for AI responses
- GUI interface for voice interaction
- Integration with existing NL_to_STL system
"""

# Core components
from .audio_processor import AudioProcessor
from .transcriber import Transcriber
from .audio_loop import AudioProcessingLoop
from .tts_engine import TTSEngine

# GUI components
from .gui_components import GUIComponents
from .voice_gui import VoiceNLtoSTLGUI

# Main applications
from .main_app import VoiceLLMApp
from .voice_enabled_nl_to_stl import VoiceEnabledNLtoSTL
from .voice_vernacopter_main import main

# Configuration
from .config import *

__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "Voice-enabled interface for VernaCopter system"

