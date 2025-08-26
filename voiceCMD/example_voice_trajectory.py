#!/usr/bin/env python3
"""
Example: Voice-Enabled Trajectory Generation
Demonstrates the complete workflow from voice input to trajectory generation and visualization.

This script shows how to:
1. Use voice commands to describe a drone task
2. Convert natural language to STL specification
3. Generate trajectory from the specification
4. Visualize the trajectory with matplotlib

Author: AI Assistant
"""

import sys
import os
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from voice_enabled_nl_to_stl import VoiceEnabledNLtoSTL
from basics.logger import color_text

def main():
    """Main example function."""
    
    print("🎤 Voice-Enabled Trajectory Generation Example")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your_api_key_here'")
        return 1
    
    # Scenario configuration
    scenario_name = "reach_avoid"
    objects = ["drone", "goal", "obstacle1"]  # Use correct object names
    N = 50  # Maximum time steps
    dt = 0.7  # Time step size
    gpt_model = "gpt-5-mini"
    
    print(f"📋 Configuration:")
    print(f"   Scenario: {scenario_name}")
    print(f"   Objects: {objects}")
    print(f"   Time steps: {N}")
    print(f"   Time step size: {dt}")
    print(f"   GPT Model: {gpt_model}")
    print("=" * 60)
    
    try:
        # Initialize voice-enabled system
        print("🔧 Initializing voice-enabled system...")
        voice_system = VoiceEnabledNLtoSTL(
            objects=objects,
            N=N,
            dt=dt,
            GPT_model=gpt_model,
            scenario_name=scenario_name
        )
        
        # Enable advanced features (optional)
        print("🔧 Configuring advanced features...")
        voice_system.enable_specification_checking(enabled=True, max_iterations=3)
        voice_system.enable_syntax_checking(enabled=True, max_iterations=3)
        
        # Test voice components
        print("🧪 Testing voice components...")
        if not voice_system.test_voice_components():
            print("❌ Voice components test failed!")
            return 1
        
        print("✅ Voice components test passed!")
        print("=" * 60)
        
        # Start voice conversation
        print("🎙️ Starting voice conversation...")
        print("💡 Voice Commands:")
        print("   - Say 'generate trajectory' to manually generate trajectory")
        print("   - Say 'clear' to clear conversation history")
        print("   - Say 'quit' to end conversation")
        print("   - Just describe your task naturally!")
        print("=" * 60)
        
        # Start the conversation
        messages, status = voice_system.start_voice_conversation(
            instructions_file='one_shot_ChatGPT_instructions.txt',
            max_inputs=10,
            auto_speak=True
        )
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 CONVERSATION RESULTS")
        print("=" * 60)
        print(f"Status: {status}")
        
        if status == "completed":
            # Get final specification
            final_spec = voice_system.get_final_specification()
            if final_spec:
                print("\n🎯 FINAL STL SPECIFICATION:")
                print("-" * 40)
                print(final_spec)
                print("-" * 40)
            
            # Get generated trajectory
            trajectory = voice_system.get_current_trajectory()
            if trajectory is not None:
                print("\n🚁 TRAJECTORY GENERATION:")
                print("-" * 40)
                print(f"Trajectory shape: {trajectory.shape}")
                print("Visualization windows should be open")
                print("-" * 40)
                
                # Keep the script running to show visualizations
                print("\n📈 Visualization windows are open.")
                print("Press Ctrl+C to exit...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n👋 Exiting...")
            else:
                print("❌ No trajectory was generated")
        else:
            print(f"Conversation ended with status: {status}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
