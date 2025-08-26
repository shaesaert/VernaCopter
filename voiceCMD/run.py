#!/usr/bin/env python3
"""
VoiceLLM Launcher
Simple script to run the VoiceLLM application
"""

import tkinter as tk
import sounddevice as sd
from main_app import VoiceLLMApp

def main():
    """Main function to launch VoiceLLM"""
    # Print audio device information
    print("Available audio backends:")
    print(sd.query_hostapis())
    print("\nAvailable audio devices:")
    print(sd.query_devices())
    
    # Check default input device
    try:
        default_device = sd.query_devices(kind='input')
        print(f"\nDefault input device: {default_device['name']}")
        print(f"Supported sample rates: {default_device.get('default_samplerate', 'Unknown')}")
    except Exception as e:
        print(f"Error querying default device: {e}")
    
    # Create and run GUI
    root = tk.Tk()
    app = VoiceLLMApp(root)
    
    # Handle window close
    def on_closing():
        app.audio_loop.set_recording_state(False)
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
