"""
GUI Components module for VoiceLLM
Handles all GUI elements and layouts
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import time
import threading
import math
from .config import *

class GUIComponents:
    def __init__(self, root):
        self.root = root
        self.setup_root_window()
        self.colors = COLORS
        
    def setup_root_window(self):
        """Setup the main window configuration"""
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        
        # Configure root window
        self.root.configure(bg=COLORS["bg_color"])
        self.root.option_add('*TFrame*background', COLORS["bg_color"])
        self.root.option_add('*TLabel*background', COLORS["bg_color"])
        self.root.option_add('*TButton*background', COLORS["accent_color"])
    
    def create_main_frame(self, parent):
        """Create the main frame"""
        main_frame = tk.Frame(parent, bg=COLORS["bg_color"], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        return main_frame
    
    def create_title_frame(self, parent):
        """Create the title section"""
        title_frame = tk.Frame(parent, bg=COLORS["bg_color"])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame, 
                              text="VoiceLLM: Speech-to-Text with TTS",
                              font=("Arial", 24, "bold"),
                              fg=COLORS["highlight_color"],
                              bg=COLORS["bg_color"])
        title_label.pack()
        
        return title_frame
    
    def create_tts_control_panel(self, parent, tts_engine, toggle_tts_command, speak_command):
        """Create the TTS control panel"""
        tts_frame = tk.Frame(parent, bg=COLORS["bg_color"])
        tts_frame.pack(fill=tk.X, pady=(0, 20))
        
        # TTS Title
        tts_title = tk.Label(tts_frame, 
                            text="Text-to-Speech Controls", 
                            font=("Arial", 14, "bold"),
                            fg=COLORS["text_color"],
                            bg=COLORS["bg_color"])
        tts_title.pack(anchor=tk.W, pady=(0, 10))
        
        # TTS Controls Frame
        tts_controls = tk.Frame(tts_frame, bg=COLORS["bg_color"])
        tts_controls.pack(fill=tk.X)
        
        # TTS Toggle Button
        self.tts_toggle_button = tk.Button(tts_controls, 
                                          text="TTS: ON", 
                                          command=toggle_tts_command,
                                          font=("Arial", 12, "bold"),
                                          bg=COLORS["success_color"],
                                          fg="white",
                                          relief="flat",
                                          padx=15,
                                          pady=5,
                                          cursor="hand2")
        self.tts_toggle_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Speak Last Text Button
        speak_button = tk.Button(tts_controls, 
                                text="Speak Last Text", 
                                command=speak_command,
                                font=("Arial", 12, "bold"),
                                bg=COLORS["accent_color"],
                                fg="white",
                                relief="flat",
                                padx=15,
                                pady=5,
                                cursor="hand2")
        speak_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # TTS Engine Selection
        if tts_engine.get_available_engines():
            engine_frame = tk.Frame(tts_controls, bg=COLORS["bg_color"])
            engine_frame.pack(side=tk.LEFT, padx=(20, 0))
            
            tk.Label(engine_frame, text="TTS Engine:", 
                    font=("Arial", 10, "bold"), 
                    fg=COLORS["text_color"], 
                    bg=COLORS["bg_color"]).pack(side=tk.LEFT)
            
            self.engine_var = tk.StringVar(value=tts_engine.get_current_engine())
            engine_combo = ttk.Combobox(engine_frame, 
                                       textvariable=self.engine_var,
                                       state="readonly", 
                                       width=15)
            
            # Populate engine options
            engines = tts_engine.get_available_engines()
            engine_options = []
            for engine_id, engine_info in engines.items():
                engine_options.append(f"{engine_info['name']} ({engine_info['quality']})")
            
            engine_combo['values'] = engine_options
            engine_combo.pack(side=tk.LEFT, padx=(10, 0))
            
            # Bind engine selection
            def on_engine_selected(event):
                selected = self.engine_var.get()
                # Extract engine ID from display name
                for engine_id, engine_info in engines.items():
                    if f"{engine_info['name']} ({engine_info['quality']})" == selected:
                        tts_engine.set_engine(engine_id)
                        break
            
            engine_combo.bind('<<ComboboxSelected>>', on_engine_selected)
        
        # Speed Control
        speed_frame = tk.Frame(tts_controls, bg=COLORS["bg_color"])
        speed_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        tk.Label(speed_frame, text="Speed:", 
                font=("Arial", 10, "bold"), 
                fg=COLORS["text_color"], 
                bg=COLORS["bg_color"]).pack(side=tk.LEFT)
        
        self.speed_var = tk.DoubleVar(value=TTS_SPEED_FACTOR)
        speed_scale = tk.Scale(speed_frame, 
                              from_=0.5, to=2.0, 
                              orient=tk.HORIZONTAL,
                              variable=self.speed_var, 
                              bg=COLORS["bg_color"], 
                              fg=COLORS["text_color"],
                              highlightbackground=COLORS["bg_color"],
                              command=lambda v: tts_engine.set_speed(float(v)),
                              resolution=0.05, 
                              length=100)
        speed_scale.pack(side=tk.LEFT, padx=(10, 0))
        
        return tts_frame
    
    def update_tts_toggle_button(self, enabled):
        """Update TTS toggle button appearance"""
        if enabled:
            self.tts_toggle_button.config(text="TTS: ON", bg=COLORS["success_color"])
        else:
            self.tts_toggle_button.config(text="TTS: OFF", bg=COLORS["warning_color"])
    
    def create_control_panel(self, parent, record_command, clear_command):
        """Create the control panel with buttons"""
        control_frame = tk.Frame(parent, bg=COLORS["bg_color"])
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Record button
        record_button = tk.Button(control_frame, 
                                 text="Start Recording",
                                 command=record_command,
                                 font=("Arial", 14, "bold"),
                                 bg=COLORS["accent_color"],
                                 fg="white",
                                 relief="flat",
                                 padx=20,
                                 pady=10,
                                 cursor="hand2")
        record_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Clear button
        clear_button = tk.Button(control_frame, 
                                text="🗑️ Clear Text", 
                                command=clear_command,
                                font=("Arial", 14, "bold"),
                                bg=COLORS["accent_color"],
                                fg="white",
                                relief="flat",
                                padx=20,
                                pady=10,
                                cursor="hand2")
        clear_button.pack(side=tk.LEFT, padx=(0, 15))
        
        return control_frame, record_button
    
    def create_status_indicator(self, parent):
        """Create the status indicator section"""
        status_frame = tk.Frame(parent, bg=COLORS["bg_color"])
        status_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        status_indicator = tk.Canvas(status_frame, width=20, height=20, 
                                   bg=COLORS["bg_color"], highlightthickness=0)
        status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        status_label = tk.Label(status_frame, 
                               text="Ready to listen", 
                               font=("Arial", 12, "bold"),
                               fg=COLORS["success_color"],
                               bg=COLORS["bg_color"])
        status_label.pack(side=tk.LEFT)
        
        return status_frame, status_indicator, status_label
    
    def create_text_display(self, parent):
        """Create the main text display area"""
        text_container = tk.Frame(parent, bg=COLORS["secondary_bg"], relief="flat", bd=2)
        text_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Text area header
        text_header = tk.Frame(text_container, bg=COLORS["accent_color"])
        text_header.pack(fill=tk.X)
        
        tk.Label(text_header, text="Recognized Text",
                font=("Arial", 14, "bold"),
                fg="white",
                bg=COLORS["accent_color"],
                padx=10,
                pady=5).pack(side=tk.LEFT)
        
        # Scrolled text widget
        text_display = scrolledtext.ScrolledText(
            text_container, 
            wrap=tk.WORD, 
            font=("Arial", 16),
            bg=COLORS["secondary_bg"],
            fg=COLORS["text_color"],
            insertbackground=COLORS["highlight_color"],
            selectbackground=COLORS["accent_color"],
            relief="flat",
            padx=15,
            pady=15
        )
        text_display.pack(fill=tk.BOTH, expand=True)
        
        return text_display
    
    def create_instructions(self, parent):
        """Create the instructions section"""
        instructions_frame = tk.Frame(parent, bg=COLORS["bg_color"])
        instructions_frame.pack(fill=tk.X)
        
        instructions = tk.Label(instructions_frame, 
                               text="Tip: Click 'Start Recording' to begin and 'Stop Recording' to end. Your speech will be transcribed in real-time.",
                               font=("Arial", 11),
                               fg=COLORS["warning_color"],
                               bg=COLORS["bg_color"])
        instructions.pack()
        
        return instructions_frame
    
    def update_status_indicator(self, status_indicator, is_recording):
        """Update the animated status indicator"""
        status_indicator.delete("all")
        
        if is_recording:
            # Create pulsing circle
            radius = 8
            center_x, center_y = 10, 10
            pulse = abs(math.sin(time.time() * 4)) * 0.3 + 0.7
            color = self.interpolate_color(COLORS["highlight_color"], "#ffffff", pulse)
            status_indicator.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill=color, outline=""
            )
        else:
            # Create static circle
            radius = 6
            center_x, center_y = 10, 10
            status_indicator.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill=COLORS["success_color"], outline=""
            )
    
    def interpolate_color(self, color1, color2, ratio):
        """Interpolate between two hex colors"""
        # Convert hex to RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(*rgb)
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        rgb_result = tuple(int(rgb1[i] + (rgb2[i] - rgb1[i]) * ratio) for i in range(3))
        return rgb_to_hex(rgb_result)
    
    def configure_text_tags(self, text_display):
        """Configure text styling tags"""
        try:
            text_display.tag_configure("timestamp", 
                                      font=("Arial", 12, "bold"),
                                      foreground=COLORS["highlight_color"])
            text_display.tag_configure("message", 
                                      font=("Arial", 16),
                                      foreground=COLORS["text_color"])
        except Exception as e:
            print(f"Error configuring text tags: {e}")
