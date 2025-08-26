#!/usr/bin/env python3
"""
Voice-Enabled VernaCopter Launcher
Simple launcher for the voice-enabled VernaCopter system.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import and run the main function
from voiceCMD.voice_vernacopter_main import main

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

