#!/usr/bin/env python3
"""
Voice-Enabled VernaCopter Main Script
Main entry point for the voice-enabled VernaCopter system
without modifying existing files.

Author: AI Assistant
"""

import tkinter as tk
import sys
import os
import argparse

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .voice_gui import VoiceNLtoSTLGUI
from .voice_enabled_nl_to_stl import VoiceEnabledNLtoSTL

def get_scenario_objects(scenario_name="reach_avoid"):
    """
    Get scenario objects based on scenario name.
    
    Parameters:
    -----------
    scenario_name : str
        Name of the scenario ("reach_avoid" or "treasure_hunt")
        
    Returns:
    --------
    list
        List of objects for the scenario
    """
    if scenario_name == "reach_avoid":
        return ["drone", "goal", "obstacle1"]  # Use correct object names
    elif scenario_name == "treasure_hunt":
        return ["drone", "door_key", "chest"]  # Use correct object names
    else:
        print(f"Warning: Unknown scenario '{scenario_name}', using default objects")
        return ["drone", "goal", "obstacle1"]  # Use correct object names

def get_scenario_parameters(scenario_name="reach_avoid"):
    """
    Get scenario parameters.
    
    Parameters:
    -----------
    scenario_name : str
        Name of the scenario
        
    Returns:
    --------
    tuple
        (N, dt) - time steps and time step size
    """
    # Default parameters
    N = 50  # Maximum time steps
    dt = 0.7  # Time step size
    
    if scenario_name == "reach_avoid":
        N = 50
        dt = 0.7
    elif scenario_name == "treasure_hunt":
        N = 60
        dt = 0.7
        
    return N, dt

def main():
    """Main function for voice-enabled VernaCopter."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Voice-Enabled VernaCopter")
    parser.add_argument("--scenario", "-s", default="reach_avoid",
                       choices=["reach_avoid", "treasure_hunt"],
                       help="Scenario to use (default: reach_avoid)")
    parser.add_argument("--model", "-m", default="gpt-5-mini",
                       help="GPT model to use (default: gpt-5-mini, gpt-3.5-turbo)")
    parser.add_argument("--test-only", "-t", action="store_true",
                       help="Test voice components only")
    parser.add_argument("--no-gui", action="store_true",
                       help="Run without GUI (command line only)")
    parser.add_argument("--instructions", "-i", default="one_shot_ChatGPT_instructions.txt",
                       help="Instructions file to use (default: one_shot_ChatGPT_instructions.txt)")
    
    args = parser.parse_args()
    
    # Get scenario parameters
    objects = get_scenario_objects(args.scenario)
    N, dt = get_scenario_parameters(args.scenario)
    
    print("🎤 Voice-Enabled VernaCopter")
    print("=" * 50)
    print(f"Scenario: {args.scenario}")
    print(f"Objects: {objects}")
    print(f"Time steps: {N}")
    print(f"Time step size: {dt}")
    print(f"GPT Model: {args.model}")
    print(f"Instructions: {args.instructions}")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ ERROR: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your_api_key_here'")
        return 1
    
    # Test-only mode
    if args.test_only:
        print("🧪 Testing voice components only...")
        try:
            voice_system = VoiceEnabledNLtoSTL(objects, N, dt, args.model, args.scenario)
            success = voice_system.test_voice_components()
            if success:
                print("✅ Voice components test passed!")
                return 0
            else:
                print("❌ Voice components test failed!")
                return 1
        except Exception as e:
            print(f"❌ Test error: {e}")
            return 1
    
    # Command line mode
    if args.no_gui:
        print("🎤 Starting command line voice conversation...")
        try:
            voice_system = VoiceEnabledNLtoSTL(objects, N, dt, args.model, args.scenario)
            
            # Test components first
            print("🧪 Testing voice components...")
            if not voice_system.test_voice_components():
                print("❌ Voice components test failed!")
                return 1
            
            # Start conversation
            print(color_text("🎙️ Starting voice conversation...", 'green'))
            print(color_text("💡 Voice Commands:", 'cyan'))
            print(color_text("   - Say 'generate trajectory' to manually generate trajectory", 'cyan'))
            print(color_text("   - Say 'clear' to clear conversation history", 'cyan'))
            print(color_text("   - Say 'quit' to end conversation", 'cyan'))
            print(color_text("   - Just describe your task naturally!", 'cyan'))
            
            messages, status = voice_system.start_voice_conversation(args.instructions)
            
            # Display results
            if status == "completed":
                final_spec = voice_system.get_final_specification()
                trajectory = voice_system.get_current_trajectory()
                
                if final_spec:
                    print("\n" + "="*60)
                    print("🎯 FINAL STL SPECIFICATION:")
                    print("="*60)
                    print(final_spec)
                    print("="*60)
                    
                    if trajectory is not None:
                        print("\n" + "="*60)
                        print("🚁 TRAJECTORY GENERATED SUCCESSFULLY!")
                        print("="*60)
                        print(f"Trajectory shape: {trajectory.shape}")
                        print("Visualization windows should be open")
                        print("="*60)
                    
                    return 0
                else:
                    print("❌ No specification generated")
                    return 1
            else:
                print(f"Conversation ended with status: {status}")
                return 0
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    # GUI mode (default)
    try:
        # Create root window
        root = tk.Tk()
        
        # Create voice GUI
        app = VoiceNLtoSTLGUI(root, objects, N, dt, args.model, args.scenario)
        
        # Handle window close
        def on_closing():
            app.on_closing()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Center window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Start GUI
        print("🎤 Starting GUI...")
        root.mainloop()
        
    except Exception as e:
        print(f"❌ GUI Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
