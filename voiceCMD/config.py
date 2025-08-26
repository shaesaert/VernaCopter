"""
Configuration settings for VoiceCMD speech-to-text system
A voice-enabled interface for VernaCopter NL_to_STL system.

This module contains all configuration parameters for:
- Audio processing and recording
- Whisper transcription settings
- Text-to-speech configuration
- GUI appearance and behavior
- Performance optimization
"""

# =============================================================================
# AUDIO CONFIGURATION
# =============================================================================
SAMPLERATE = 16000  # Optimal sample rate for Whisper (native rate)
CHUNK_DURATION = 3  # Audio chunk duration in seconds
MIN_VOICE_LEVEL = 0.001  # Minimum voice activity threshold
SILENCE_THRESHOLD = 0.0005  # Silence detection threshold
TRANSCRIPTION_COOLDOWN = 0.3  # Cooldown between transcriptions
SILENCE_PAUSE_THRESHOLD = 1.0  # Silence duration to trigger transcription

# Audio device configuration
AUDIO_TEST_RATES = [16000, 44100, 48000, 22050, 8000]  # Prioritize 16kHz
AUDIO_CHANNELS = 1  # Mono audio for speech recognition
AUDIO_DTYPE = 'float32'  # Audio data type

# =============================================================================
# WHISPER MODEL CONFIGURATION
# =============================================================================
DEFAULT_MODEL = "medium"  # Default Whisper model (good balance of speed/accuracy)
MODEL_OPTIONS = [
    ("Tiny (Fast)", "tiny"),
    ("Base (Balanced)", "base"), 
    ("Small (Good)", "small"),
    ("Medium (Better)", "medium"),
    ("Large (Best)", "large"),
    ("Large-v2 (Latest)", "large-v2"),
    ("Large-v3 (Latest)", "large-v3")
]

# =============================================================================
# TEXT-TO-SPEECH CONFIGURATION
# =============================================================================
TTS_DEFAULT_ENGINE = "gtts"  # Default TTS engine
TTS_SPEED_FACTOR = 1.05  # Speech speed multiplier
TTS_VOLUME = 0.85  # Audio volume level
TTS_AUTO_SPEAK = True  # Automatically speak AI responses
TTS_LANGUAGE_DETECTION = True  # Enable automatic language detection

# TTS engine priority (order of preference)
TTS_ENGINE_PRIORITY = ["gtts", "azure", "elevenlabs", "pyttsx3"]

# =============================================================================
# GUI CONFIGURATION
# =============================================================================
WINDOW_SIZE = "1000x800"
WINDOW_TITLE = "Voice-Enabled VernaCopter"

# Color theme for GUI
COLORS = {
    # Background colors
    "bg_color": "#1a1a2e",
    "secondary_bg": "#16213e", 
    "accent_color": "#0f3460",
    
    # Text colors
    "text_color": "#e94560",
    "highlight_color": "#00d4ff",
    
    # Status colors
    "success_color": "#00ff88",
    "warning_color": "#ffaa00",
    "error_color": "#ff4444",
    "muted_color": "#888888",
    "border_color": "#333333",
    
    # Conversation colors
    "user_voice_color": "#ff6b6b",      # Red for user voice input
    "ai_response_color": "#4ecdc4",     # Teal for AI responses
    "transcription_color": "#ffe66d",   # Yellow for transcription
    "system_color": "#a8e6cf"          # Light green for system messages
}

# =============================================================================
# PERFORMANCE OPTIMIZATION
# =============================================================================
ENABLE_AUDIO_CACHING = True  # Cache resampled audio for performance
MAX_AUDIO_BUFFER_SIZE = 10  # Maximum audio chunks to buffer
ENABLE_PARALLEL_PROCESSING = True  # Enable parallel audio processing
GUI_UPDATE_INTERVAL = 30  # GUI update interval in milliseconds
ENABLE_PERFORMANCE_MONITORING = True  # Track performance metrics
