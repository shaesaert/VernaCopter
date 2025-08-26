"""
Main Application module for VoiceLLM
Main application class that coordinates all components
"""

import tkinter as tk
import queue
import time
from .audio_processor import AudioProcessor
from .transcriber import Transcriber
from .audio_loop import AudioProcessingLoop
from .gui_components import GUIComponents
from .tts_engine import TTSEngine
from .config import *

class VoiceLLMApp:
    def __init__(self, root):
        self.root = root
        
        # Initialize components
        self.audio_processor = AudioProcessor()
        self.transcriber = Transcriber()
        self.tts_engine = TTSEngine()
        
        # Initialize TTS audio devices
        if not self.tts_engine.audio_devices:
            self.tts_engine.debug_audio_devices()
        
        self.text_queue = queue.Queue()
        self.audio_loop = AudioProcessingLoop(self.audio_processor, self.transcriber, self.text_queue)
        
        # GUI components
        self.gui = GUIComponents(root)
        
        # Application state
        self.is_recording = False
        self.tts_enabled = TTS_AUTO_SPEAK
        
        # Setup GUI
        self.setup_gui()
        
        # Start audio processing
        self.audio_loop.start_processing()
        
        # Start GUI update loop
        self.update_gui()
    
    def setup_gui(self):
        """Setup the complete GUI"""
        # Create main frame
        main_frame = self.gui.create_main_frame(self.root)
        
        # Create title
        self.gui.create_title_frame(main_frame)
        
        # Create TTS control panel
        tts_frame = self.gui.create_tts_control_panel(
            main_frame, 
            self.tts_engine,
            self.toggle_tts,
            self.speak_last_text
        )
        
        # Create control panel
        control_frame, self.record_button = self.gui.create_control_panel(
            main_frame, self.toggle_recording, self.clear_text
        )
        
        # Create status indicator
        self.status_frame, self.status_indicator, self.status_label = self.gui.create_status_indicator(control_frame)
        
        # Create text display
        self.text_display = self.gui.create_text_display(main_frame)
        
        # Create instructions
        self.gui.create_instructions(main_frame)
        
        # Configure text tags
        self.root.after(100, lambda: self.gui.configure_text_tags(self.text_display))
        
        # Update TTS button state
        self.gui.update_tts_toggle_button(self.tts_enabled)
    
    def toggle_recording(self):
        """Toggle recording on/off"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start recording"""
        self.is_recording = True
        self.audio_loop.set_recording_state(True)
        
                # Update GUI
        self.record_button.config(text="Stop Recording", bg="#ff4444")
        self.status_label.config(text="Listening...", fg=COLORS["highlight_color"])
        self.gui.update_status_indicator(self.status_indicator, True)
    
    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
        self.audio_loop.set_recording_state(False)
        
                # Update GUI
        self.record_button.config(text="Start Recording", bg=COLORS["accent_color"])
        self.status_label.config(text="Ready to listen", fg=COLORS["success_color"])
        self.gui.update_status_indicator(self.status_indicator, False)
    
    def toggle_tts(self):
        """Toggle TTS on/off"""
        self.tts_enabled = not self.tts_enabled
        status = "enabled" if self.tts_enabled else "disabled"
        self.status_label.config(text=f"TTS {status}", fg=COLORS["highlight_color"])
        self.gui.update_tts_toggle_button(self.tts_enabled)
        print(f"TTS {status}")
    
    def speak_last_text(self):
        """Speak the last transcribed text"""
        # Get the last line of text from the display
        text_content = self.text_display.get(1.0, tk.END).strip()
        if text_content:
            # Extract the last message (after the last timestamp)
            lines = text_content.split('\n')
            last_message = ""
            for line in reversed(lines):
                if line.strip() and not line.startswith('[') and not line.startswith('TTS'):
                    last_message = line.strip()
                    break
            
            if last_message:
                self.tts_engine.speak(last_message, self.tts_status_callback)
            else:
                self.status_label.config(text="No text to speak", fg=COLORS["warning_color"])
        else:
            self.status_label.config(text="No text to speak", fg=COLORS["warning_color"])
    
    def tts_status_callback(self, status):
        """Callback for TTS status updates"""
        self.status_label.config(text=status, fg=COLORS["highlight_color"])
    
    def clear_text(self):
        """Clear the text display"""
        self.text_display.delete(1.0, tk.END)
    
    def update_gui(self):
        """Update GUI elements from queue"""
        try:
            while True:
                msg_data = self.text_queue.get_nowait()
                
                if msg_data[0] == "full":
                    # Add timestamp with formatting
                    timestamp = time.strftime("%H:%M:%S")
                    text = msg_data[1]
                    
                    try:
                        # Insert with styling
                        self.text_display.insert(tk.END, f"[{timestamp}]\n", "timestamp")
                        self.text_display.insert(tk.END, f"{text}\n\n", "message")
                        self.text_display.see(tk.END)  # Auto-scroll to bottom
                        
                        # Auto-speak if TTS is enabled
                        if self.tts_enabled and text.strip():
                            self.tts_engine.speak(text, self.tts_status_callback)
                            
                    except Exception as e:
                        print(f"Error inserting text: {e}")
                        # Fallback: insert without tags
                        self.text_display.insert(tk.END, f"[{timestamp}]\n{text}\n\n")
                        self.text_display.see(tk.END)
                    
        except queue.Empty:
            pass
        except Exception as e:
            print(f"Error in update_gui: {e}")
        
        # Update status indicator animation
        if self.is_recording:
            self.gui.update_status_indicator(self.status_indicator, True)
        
        # Schedule next update (faster updates)
        self.root.after(GUI_UPDATE_INTERVAL, self.update_gui)
