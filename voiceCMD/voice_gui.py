#!/usr/bin/env python3
"""
Voice GUI for NL_to_STL Integration
A unified GUI interface for voice-enabled VernaCopter system
without modifying existing files.

Author: AI Assistant
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .voice_enabled_nl_to_stl import VoiceEnabledNLtoSTL
from .gui_components import GUIComponents
from .config import *

# Extended color scheme to include all needed colors
EXTENDED_COLORS = {
    "bg_color": "#1a1a2e",
    "secondary_bg": "#16213e", 
    "accent_color": "#0f3460",
    "text_color": "#e94560",
    "highlight_color": "#00d4ff",
    "success_color": "#00ff88",
    "warning_color": "#ffaa00",
    "error_color": "#ff4444",
    "muted_color": "#888888",
    "border_color": "#333333",
    "user_voice_color": "#ff6b6b",      # Red for user voice input
    "ai_response_color": "#4ecdc4",     # Teal for AI responses
    "transcription_color": "#ffe66d",   # Yellow for transcription
    "system_color": "#a8e6cf"          # Light green for system messages
}

# Use extended colors, fallback to original COLORS if available
try:
    COLORS = {**COLORS, **EXTENDED_COLORS}
except NameError:
    COLORS = EXTENDED_COLORS

class VoiceNLtoSTLGUI:
    """
    Unified GUI for voice-enabled NL_to_STL system.
    """
    
    def __init__(self, root, objects, N, dt, GPT_model="gpt-3.5-turbo", scenario_name="reach_avoid"):
        """
        Initialize the voice GUI.
        
        Parameters:
        -----------
        root : tk.Tk
            Root window
        objects : list
            List of objects for the scenario
        N : int
            Maximum time steps
        dt : float
            Time step size
        GPT_model : str
            GPT model to use
        scenario_name : str
            Name of the scenario for trajectory generation
        """
        self.root = root
        self.root.title("Voice-Enabled VernaCopter")
        self.root.geometry("1000x800")
        
        # Store scenario information
        self.scenario_name = scenario_name
        
        # Initialize voice-enabled NL_to_STL
        self.voice_nl_to_stl = VoiceEnabledNLtoSTL(objects, N, dt, GPT_model, scenario_name)
        
        # Set up GUI callbacks
        self.voice_nl_to_stl.set_gui_callbacks(
            transcription_callback=self._on_transcription_update,
            response_callback=self._on_ai_response,
            trajectory_callback=self._on_trajectory_generated
        )
        
        # GUI components
        self.gui = GUIComponents(root)
        
        # State
        self.conversation_active = False
        self.conversation_thread = None
        self.tts_enabled = True
        self.auto_speak = True
        
        # Text queues for real-time updates
        self.transcription_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Setup GUI
        self.setup_gui()
        
        # Start GUI update loop
        self.update_gui()
        
    def _on_transcription_update(self, text):
        """Callback for transcription updates."""
        self.root.after(0, lambda: self._update_transcription_display(text))
        self.root.after(0, lambda: self._add_to_display(f"You: {text}", "user"))
        
    def _on_ai_response(self, text):
        """Callback for AI response updates."""
        self.root.after(0, lambda: self._add_to_display(f"ChatGPT: {text}", "assistant"))
        
    def _on_trajectory_generated(self, trajectory, specification):
        """Callback for trajectory generation."""
        self.root.after(0, lambda: self._add_to_display(f"🚁 Trajectory generated successfully!", "system"))
        self.root.after(0, lambda: self._add_to_display(f"📋 Specification: {specification}", "system"))
        self.root.after(0, lambda: self._update_trajectory_status(True))
        
    def setup_gui(self):
        """Setup the complete GUI."""
        # Main frame
        main_frame = self.gui.create_main_frame(self.root)
        
        # Title
        title_label = tk.Label(main_frame, text="Voice-Enabled VernaCopter", 
                              font=("Arial", 18, "bold"), fg=COLORS["accent_color"])
        title_label.pack(pady=10)
        
        # Control panel
        control_frame = tk.Frame(main_frame, bg=COLORS["bg_color"])
        control_frame.pack(pady=10, fill=tk.X, padx=10)
        
        # Start/Stop conversation button
        self.conversation_button = tk.Button(
            control_frame,
            text="Start Voice Conversation",
            command=self.toggle_conversation,
            bg=COLORS["accent_color"],
            fg="white",
            font=("Arial", 12, "bold"),
            relief=tk.RAISED,
            bd=2
        )
        self.conversation_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # TTS toggle
        self.tts_button = tk.Button(
            control_frame,
            text="TTS: ON",
            command=self.toggle_tts,
            bg=COLORS["success_color"],
            fg="white",
            font=("Arial", 10),
            relief=tk.RAISED,
            bd=2
        )
        self.tts_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Auto-speak toggle
        self.auto_speak_button = tk.Button(
            control_frame,
            text="Auto-Speak: ON",
            command=self.toggle_auto_speak,
            bg=COLORS["success_color"],
            fg="white",
            font=("Arial", 10),
            relief=tk.RAISED,
            bd=2
        )
        self.auto_speak_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Test voice button
        self.test_button = tk.Button(
            control_frame,
            text="Test Voice",
            command=self.test_voice_components,
            bg=COLORS["warning_color"],
            fg="white",
            font=("Arial", 10),
            relief=tk.RAISED,
            bd=2
        )
        self.test_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Clear button
        self.clear_button = tk.Button(
            control_frame,
            text="Clear",
            command=self.clear_display,
            bg=COLORS["error_color"],
            fg="white",
            font=("Arial", 10),
            relief=tk.RAISED,
            bd=2
        )
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Status frame
        status_frame = tk.Frame(main_frame, bg=COLORS["bg_color"])
        status_frame.pack(pady=5, fill=tk.X, padx=10)
        
        # Status label
        self.status_label = tk.Label(status_frame, text="Ready to start voice conversation", 
                                   fg=COLORS["success_color"], font=("Arial", 10, "bold"))
        self.status_label.pack(side=tk.LEFT)
        
        # Trajectory status label
        self.trajectory_status_label = tk.Label(status_frame, text="Trajectory: Not generated", 
                                              fg=COLORS["muted_color"], font=("Arial", 10))
        self.trajectory_status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                          mode='indeterminate')
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Real-time transcription display
        transcription_frame = tk.Frame(main_frame)
        transcription_frame.pack(pady=5, padx=10, fill=tk.X)
        
        transcription_label = tk.Label(transcription_frame, text="Real-time Transcription:", 
                                     font=("Arial", 12, "bold"), fg=COLORS["transcription_color"])
        transcription_label.pack(anchor=tk.W)
        
        self.transcription_display = tk.Text(
            transcription_frame,
            height=3,
            font=("Consolas", 10),
            bg=COLORS["secondary_bg"],
            fg=COLORS["transcription_color"],
            insertbackground=COLORS["transcription_color"],
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.transcription_display.pack(fill=tk.X, pady=2)
        
        # Conversation display
        display_frame = tk.Frame(main_frame)
        display_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Display label
        display_label = tk.Label(display_frame, text="💬 Conversation History:", 
                               font=("Arial", 12, "bold"), fg=COLORS["text_color"])
        display_label.pack(anchor=tk.W)
        
        # Text display
        self.conversation_display = scrolledtext.ScrolledText(
            display_frame, 
            height=15, 
            width=80,
            font=("Consolas", 10),
            bg=COLORS["bg_color"],
            fg=COLORS["text_color"],
            insertbackground=COLORS["text_color"],
            selectbackground=COLORS["accent_color"],
            wrap=tk.WORD
        )
        self.conversation_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Configure text tags with enhanced colors
        self.conversation_display.tag_configure("timestamp", foreground=COLORS["muted_color"])
        self.conversation_display.tag_configure("user", foreground=COLORS["user_voice_color"], font=("Consolas", 10, "bold"))
        self.conversation_display.tag_configure("assistant", foreground=COLORS["ai_response_color"], font=("Consolas", 10, "bold"))
        self.conversation_display.tag_configure("system", foreground=COLORS["system_color"], font=("Consolas", 10, "italic"))
        self.conversation_display.tag_configure("error", foreground=COLORS["error_color"], font=("Consolas", 10, "bold"))
        self.conversation_display.tag_configure("transcription", foreground=COLORS["transcription_color"], font=("Consolas", 10, "italic"))
        
        # Instructions frame
        instructions_frame = tk.Frame(main_frame, bg=COLORS["bg_color"])
        instructions_frame.pack(pady=10, padx=10, fill=tk.X)
        
        instructions = """
        Voice Commands:
        • Say your task description clearly
        • Say 'quit' to end the conversation
        • Say 'clear' to clear conversation history
        
        Color Coding:
        • Yellow: Real-time transcription
        • Red: Your voice input
        • Teal: ChatGPT responses
        • Green: System messages
        
        Features:
        • Real-time speech-to-text using Whisper
        • Text-to-speech for ChatGPT responses
        • Automatic conversation flow
        • STL specification generation
        """
        
        instruction_label = tk.Label(instructions_frame, text=instructions, 
                                   justify=tk.LEFT, fg=COLORS["text_color"], 
                                   font=("Arial", 9), bg=COLORS["bg_color"])
        instruction_label.pack()
        
    def toggle_conversation(self):
        """Toggle voice conversation on/off."""
        if not self.conversation_active:
            self.start_conversation()
        else:
            self.stop_conversation()
            
    def start_conversation(self):
        """Start the voice conversation."""
        self.conversation_active = True
        self.conversation_button.config(text="Stop Conversation", bg=COLORS["error_color"])
        self.status_label.config(text="Starting conversation...", fg=COLORS["highlight_color"])
        self.progress_bar.start()
        
        # Start conversation in separate thread
        self.conversation_thread = threading.Thread(
            target=self._run_conversation,
            daemon=True
        )
        self.conversation_thread.start()
        
    def stop_conversation(self):
        """Stop the voice conversation."""
        self.conversation_active = False
        self.voice_nl_to_stl.stop_conversation()
        self.conversation_button.config(text="Start Voice Conversation", bg=COLORS["accent_color"])
        self.status_label.config(text="Conversation stopped", fg=COLORS["warning_color"])
        self.progress_bar.stop()
        
    def _run_conversation(self):
        """Run the voice conversation."""
        try:
            # Start voice conversation
            messages, status = self.voice_nl_to_stl.start_voice_conversation(
                'ChatGPT_instructions.txt', 
                max_inputs=10, 
                auto_speak=self.auto_speak
            )
            
            # Update GUI based on status
            if status == "completed":
                self.root.after(0, lambda: self._handle_conversation_complete(messages))
            elif status == "exited":
                self.root.after(0, lambda: self._handle_conversation_exit())
            else:
                self.root.after(0, lambda: self._handle_conversation_error(status))
                
        except Exception as e:
            self.root.after(0, lambda: self._handle_conversation_error(str(e)))
            
    def _handle_conversation_complete(self, messages):
        """Handle conversation completion."""
        self.conversation_active = False
        self.conversation_button.config(text="Start Voice Conversation", bg=COLORS["accent_color"])
        self.status_label.config(text="Specification generated successfully!", fg=COLORS["success_color"])
        self.progress_bar.stop()
        
        # Get final specification
        final_spec = self.voice_nl_to_stl.get_final_specification()
        if final_spec:
            self._display_final_spec(final_spec)
            
        # Speak completion message
        if self.tts_enabled:
            self.voice_nl_to_stl.speak_text("Specification generation completed successfully!")
            
    def _handle_conversation_exit(self):
        """Handle conversation exit."""
        self.conversation_active = False
        self.conversation_button.config(text="Start Voice Conversation", bg=COLORS["accent_color"])
        self.status_label.config(text="Conversation ended by user", fg=COLORS["warning_color"])
        self.progress_bar.stop()
        
    def _handle_conversation_error(self, error):
        """Handle conversation error."""
        self.conversation_active = False
        self.conversation_button.config(text="Start Voice Conversation", bg=COLORS["accent_color"])
        self.status_label.config(text=f"Error: {error}", fg=COLORS["error_color"])
        self.progress_bar.stop()
        
        self._add_to_display(f"ERROR: {error}", "error")
        
    def _display_final_spec(self, spec):
        """Display the final specification."""
        self._add_to_display("\n" + "="*60, "system")
        self._add_to_display("FINAL STL SPECIFICATION:", "system")
        self._add_to_display("="*60, "system")
        self._add_to_display(spec, "assistant")
        self._add_to_display("="*60, "system")
        
    def _add_to_display(self, text, tag="user"):
        """Add text to the conversation display."""
        timestamp = time.strftime("%H:%M:%S")
        self.conversation_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.conversation_display.insert(tk.END, f"{text}\n", tag)
        self.conversation_display.see(tk.END)
        
    def _update_transcription_display(self, text):
        """Update the real-time transcription display."""
        self.transcription_display.config(state=tk.NORMAL)
        self.transcription_display.delete(1.0, tk.END)
        self.transcription_display.insert(tk.END, text, "transcription")
        self.transcription_display.config(state=tk.DISABLED)
        
    def _update_trajectory_status(self, generated=False):
        """Update trajectory status display."""
        if generated:
            self.trajectory_status_label.config(
                text="Trajectory: Generated ✓", 
                fg=COLORS["success_color"]
            )
        else:
            self.trajectory_status_label.config(
                text="Trajectory: Not generated", 
                fg=COLORS["muted_color"]
            )
        
    def toggle_tts(self):
        """Toggle TTS on/off."""
        self.tts_enabled = not self.tts_enabled
        status = "ON" if self.tts_enabled else "OFF"
        color = COLORS["success_color"] if self.tts_enabled else COLORS["error_color"]
        
        self.tts_button.config(text=f"TTS: {status}", bg=color)
        self.status_label.config(text=f"TTS {status.lower()}", fg=COLORS["highlight_color"])
        
    def toggle_auto_speak(self):
        """Toggle auto-speak on/off."""
        self.auto_speak = not self.auto_speak
        status = "ON" if self.auto_speak else "OFF"
        color = COLORS["success_color"] if self.auto_speak else COLORS["error_color"]
        
        self.auto_speak_button.config(text=f"Auto-Speak: {status}", bg=color)
        self.status_label.config(text=f"Auto-speak {status.lower()}", fg=COLORS["highlight_color"])
        
    def test_voice_components(self):
        """Test voice components."""
        self.status_label.config(text="Testing voice components...", fg=COLORS["highlight_color"])
        
        def test_thread():
            try:
                success = self.voice_nl_to_stl.test_voice_components()
                if success:
                    self.root.after(0, lambda: self.status_label.config(
                        text="Voice components test passed!", fg=COLORS["success_color"]))
                else:
                    self.root.after(0, lambda: self.status_label.config(
                        text="Voice components test failed!", fg=COLORS["error_color"]))
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Test error: {e}", fg=COLORS["error_color"]))
                    
        threading.Thread(target=test_thread, daemon=True).start()
        
    def clear_display(self):
        """Clear the conversation display."""
        self.conversation_display.delete(1.0, tk.END)
        self.transcription_display.config(state=tk.NORMAL)
        self.transcription_display.delete(1.0, tk.END)
        self.transcription_display.config(state=tk.DISABLED)
        self.status_label.config(text="Display cleared", fg=COLORS["highlight_color"])
        
    def update_gui(self):
        """Update GUI elements."""
        # The main updates are now handled by callbacks
        # This loop is kept for any additional GUI updates if needed
        
        # Schedule next update
        self.root.after(100, self.update_gui)
        
    def on_closing(self):
        """Handle window closing."""
        if self.conversation_active:
            self.stop_conversation()
        self.root.destroy()
