# Voice-Enabled Trajectory Generation for VernaCopter

This enhanced voice-enabled system allows you to control drone trajectories using natural language voice commands. It integrates the original NL_to_STL functionality with voice input/output and automatic trajectory generation and visualization.

## Features

- 🎤 **Voice Input**: Speak natural language commands to describe drone tasks
- 🧠 **AI Processing**: Uses GPT models to convert voice commands to STL specifications
- 🚁 **Trajectory Generation**: Automatically generates drone trajectories from STL specifications
- 📊 **Visualization**: Displays trajectory plots and analysis
- 🔍 **Specification Checking**: GPT-based validation of generated trajectories
- 🔧 **Syntax Checking**: Automatic error recovery for invalid STL specifications
- 🔊 **Voice Feedback**: TTS (Text-to-Speech) provides audio feedback
- 🖥️ **GUI Interface**: Optional graphical user interface for easy interaction
- 🛠️ **Error Handling**: Robust error handling and recovery mechanisms

## Quick Start

### Prerequisites

1. **OpenAI API Key**: Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY='your_api_key_here'
   ```

2. **Python Dependencies**: Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Audio System**: Ensure your microphone and speakers are working

### Basic Usage

#### Command Line Mode

Run the voice-enabled system in command line mode:

```bash
# Basic usage with default settings
python voice_vernacopter_main.py --no-gui

# With specific scenario
python voice_vernacopter_main.py --no-gui --scenario reach_avoid

# With different GPT model
python voice_vernacopter_main.py --no-gui --model gpt-3.5-turbo
```

#### GUI Mode

Run with graphical interface:

```bash
python voice_vernacopter_main.py
```

#### Example Scripts

Run the basic example:

```bash
python example_voice_trajectory.py
```

Run the complete workflow demonstration:

```bash
python example_complete_workflow.py
```

## Voice Commands

### Natural Language Commands

Simply describe what you want the drone to do:

- *"The drone should reach the goal and avoid obstacles"*
- *"Fly to the target while staying away from the red zone"*
- *"Navigate to the treasure without hitting any walls"*

### System Commands

- **"generate trajectory"**: Manually trigger trajectory generation
- **"clear"**: Clear conversation history
- **"quit"**: End the conversation

### Advanced Features

- **Specification Checking**: Automatically validates generated trajectories
- **Syntax Checking**: Recovers from invalid STL specifications
- **Error Recovery**: Handles trajectory generation failures gracefully
- **Trajectory Analysis**: Provides detailed trajectory statistics and analysis

## Workflow

1. **Voice Input**: Speak your task description
2. **Transcription**: System converts speech to text
3. **AI Processing**: GPT converts natural language to STL specification
4. **Trajectory Generation**: System generates optimal drone trajectory
5. **Specification Checking**: GPT validates trajectory against original requirements
6. **Visualization**: Trajectory is plotted and analyzed
7. **Error Recovery**: Syntax checking for failed trajectories
8. **Voice Feedback**: System confirms completion via TTS

## Scenarios

### Reach-Avoid Scenario
- **Goal**: Reach a target while avoiding obstacles
- **Objects**: Goal, multiple obstacles
- **Voice Example**: *"Go to the goal while avoiding all obstacles"*

### Treasure Hunt Scenario
- **Goal**: Navigate through a complex environment to find treasure
- **Objects**: Door key, chest, door, walls
- **Voice Example**: *"Find the key, open the door, and reach the treasure"*

## Configuration

### Command Line Options

```bash
python voice_vernacopter_main.py [OPTIONS]

Options:
  --scenario, -s     Scenario to use (reach_avoid, treasure_hunt)
  --model, -m        GPT model to use (gpt-5-mini, gpt-3.5-turbo)
  --instructions, -i Instructions file to use
  --test-only, -t    Test voice components only
  --no-gui           Run without GUI (command line only)
```

### Environment Variables

```bash
export OPENAI_API_KEY='your_openai_api_key'
export PYTHONPATH='/path/to/vernacopter:$PYTHONPATH'
```

## API Usage

### Basic Integration

```python
from voice_enabled_nl_to_stl import VoiceEnabledNLtoSTL

# Initialize system
voice_system = VoiceEnabledNLtoSTL(
    objects=["drone", "goal", "obstacle"],
    N=50,  # time steps
    dt=0.7,  # time step size
    GPT_model="gpt-5-mini",
    scenario_name="reach_avoid"
)

# Start conversation
messages, status = voice_system.start_voice_conversation(
    instructions_file='one_shot_ChatGPT_instructions.txt'
)

# Get results
if status == "completed":
    spec = voice_system.get_final_specification()
    trajectory = voice_system.get_current_trajectory()

# Enable advanced features
voice_system.enable_specification_checking(enabled=True, max_iterations=3)
voice_system.enable_syntax_checking(enabled=True, max_iterations=3)

### Advanced Integration

```python
# Set up GUI callbacks
def on_transcription(text):
    print(f"User said: {text}")

def on_response(text):
    print(f"AI responded: {text}")

def on_trajectory(trajectory, spec):
    print(f"Trajectory generated with spec: {spec}")

# Enable advanced features
voice_system.enable_specification_checking(enabled=True, max_iterations=3)
voice_system.enable_syntax_checking(enabled=True, max_iterations=3)

voice_system.set_gui_callbacks(
    transcription_callback=on_transcription,
    response_callback=on_response,
    trajectory_callback=on_trajectory
)
```

## Troubleshooting

### Common Issues

1. **"No module named 'stlpy'"**
   - Install stlpy: `pip install stlpy`
   - Note: Requires Gurobi license

2. **"OpenAI API key not set"**
   - Set environment variable: `export OPENAI_API_KEY='your_key'`

3. **"Audio device not found"**
   - Check microphone permissions
   - Install audio dependencies: `pip install pyaudio`

4. **"Trajectory generation failed"**
   - Check STL specification syntax
   - Verify scenario objects are correctly defined
   - Run object names test: `python test_object_names.py`

5. **"Object not found in objects dictionary"**
   - Use correct object names from scenarios
   - For reach_avoid: use "goal", "obstacle1", "obstacle2", etc.
   - For treasure_hunt: use "door_key", "chest", "door", etc.

### Testing

Test voice components:

```bash
python voice_vernacopter_main.py --test-only
```

Test specific scenario:

```bash
python voice_vernacopter_main.py --no-gui --scenario reach_avoid
```

Test object names configuration:

```bash
python test_object_names.py
```

## File Structure

```
voiceCMD/
├── voice_enabled_nl_to_stl.py      # Main voice-enabled class
├── voice_vernacopter_main.py       # Main entry point
├── voice_gui.py                    # GUI interface
├── example_voice_trajectory.py     # Basic example usage
├── example_complete_workflow.py    # Complete workflow demonstration
├── test_integration.py             # Integration test script
├── transcriber.py                  # Speech-to-text
├── tts_engine.py                   # Text-to-speech
├── audio_processor.py              # Audio processing
├── audio_loop.py                   # Audio loop management
└── README_VOICE_TRAJECTORY.md      # This file
```

## Dependencies

- **Core**: numpy, matplotlib, tkinter
- **Voice**: pyaudio, speechrecognition, pyttsx3
- **AI**: openai
- **STL**: stlpy, gurobi
- **GUI**: tkinter, ttk

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the VernaCopter framework. See the main LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the example scripts
3. Check the main VernaCopter documentation
4. Open an issue on the repository
