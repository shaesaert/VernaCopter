# VoiceCMD - Voice-Enabled Interface for VernaCopter

A voice-enabled interface for the VernaCopter NL_to_STL system that provides real-time speech-to-text transcription and text-to-speech synthesis for AI responses.

## Features

- **Real-time Speech-to-Text**: Uses OpenAI Whisper for accurate voice transcription
- **Text-to-Speech**: Speaks AI responses using multiple TTS engines
- **GUI Interface**: Clean, modern interface for voice interaction
- **Integration**: Seamlessly integrates with existing NL_to_STL system
- **Performance Optimized**: Efficient audio processing and caching

## System Architecture

```
voiceCMD/
├── __init__.py              # Package initialization and exports
├── config.py                # Configuration settings
├── audio_processor.py       # Audio recording and processing
├── transcriber.py          # Whisper-based transcription
├── audio_loop.py           # Main audio processing loop
├── tts_engine.py           # Text-to-speech synthesis
├── gui_components.py       # Reusable GUI components
├── voice_gui.py            # Main voice-enabled GUI
├── voice_enabled_nl_to_stl.py  # Integration with NL_to_STL
├── voice_vernacopter_main.py   # Main application entry point
├── main_app.py             # Standalone voice application
├── run.py                  # Simple launcher script
└── requirements.txt        # Python dependencies
```

## Core Components

### 1. Audio Processing (`audio_processor.py`)
- Audio device initialization and sample rate detection
- Audio recording with fallback sample rates
- Resampling to 16kHz for Whisper compatibility
- Simple voice activity detection using RMS
- Audio caching for performance optimization

### 2. Transcription (`transcriber.py`)
- Whisper model loading and management
- Audio transcription with optimized settings
- Fallback to base model if loading fails
- Model switching capabilities

### 3. Audio Loop (`audio_loop.py`)
- Continuous audio recording and processing
- Voice activity detection and silence-based transcription
- Performance monitoring and statistics
- Session management for conversation flow

### 4. Text-to-Speech (`tts_engine.py`)
- Multiple TTS engine support (gTTS, Azure, ElevenLabs, pyttsx3)
- Audio device detection and management
- Speech synthesis with configurable speed and volume
- Automatic language detection

### 5. GUI Components (`gui_components.py`, `voice_gui.py`)
- Modern, responsive GUI interface
- Real-time transcription display
- Conversation history with color coding
- Control buttons for recording, TTS, and settings

## Configuration

The system is configured through `config.py` with the following main sections:

### Audio Configuration
- Sample rate: 16kHz (optimal for Whisper)
- Voice activity thresholds
- Silence detection parameters
- Audio device settings

### Whisper Model Configuration
- Default model: "medium" (good balance of speed/accuracy)
- Model options from tiny to large-v3
- Transcription parameters

### TTS Configuration
- Default engine: gTTS
- Speed and volume settings
- Engine priority list
- Auto-speak functionality

### GUI Configuration
- Window size and title
- Color theme for different message types
- Performance settings

## Usage

### Quick Start
```bash
# Run the main voice-enabled VernaCopter system
python run_voice_vernacopter.py

# Or run the standalone voice application
python voiceCMD/run.py
```

### Programmatic Usage
```python
from voiceCMD import VoiceEnabledNLtoSTL

# Initialize voice-enabled system
voice_system = VoiceEnabledNLtoSTL(objects, N, dt, GPT_model="gpt-3.5-turbo")

# Start voice conversation
messages, status = voice_system.start_voice_conversation(
    'ChatGPT_instructions.txt', 
    max_inputs=10, 
    auto_speak=True
)
```

## Dependencies

Install required packages:
```bash
pip install -r voiceCMD/requirements.txt
```

Key dependencies:
- `whisper`: OpenAI's speech recognition model
- `sounddevice`: Audio recording and playback
- `numpy`: Numerical computing
- `tkinter`: GUI framework
- `gtts`: Google Text-to-Speech
- `openai`: ChatGPT API integration

## Performance Optimization

The system includes several performance optimizations:
- Audio caching for resampled audio
- Optimized Whisper settings for speed/accuracy balance
- Efficient audio buffer management
- Performance monitoring and statistics
- Parallel processing where possible

## Troubleshooting

### Audio Issues
- Check audio device permissions
- Verify ALSA/PulseAudio configuration
- Test with different sample rates
- Ensure microphone is properly connected

### Transcription Issues
- Verify Whisper model is downloaded
- Check audio levels and thresholds
- Ensure clear speech input
- Monitor performance metrics

### TTS Issues
- Check internet connection for gTTS
- Verify audio output device
- Test with different TTS engines
- Check volume and speed settings

## Development

### Adding New Features
1. Follow the modular architecture
2. Add configuration options to `config.py`
3. Update documentation
4. Test with different audio devices

### Customization
- Modify color themes in `config.py`
- Adjust voice activity thresholds
- Change TTS engine preferences
- Customize GUI layout

## License

This project is part of the VernaCopter system and follows the same licensing terms.

## Contributing

When contributing to this system:
1. Maintain the modular architecture
2. Add proper documentation
3. Test with different audio configurations
4. Follow the existing code style
5. Update the README as needed
