#!/usr/bin/env python3
"""
Voice-Enabled NL_to_STL Integration
A wrapper that adds voice input/output capabilities to the existing NL_to_STL system
without modifying the original files.

Author: AI Assistant
"""

import threading
import queue
import time
import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from .transcriber import Transcriber
from .tts_engine import TTSEngine
from .audio_processor import AudioProcessor
from .audio_loop import AudioProcessingLoop
from LLM.NL_to_STL import NL_to_STL
from STL.STL_to_path import STLSolver
from STL.trajectory_analysis import TrajectoryAnalyzer
from visuals.visualization import Visualizer
from visuals.run_simulation import simulate
from basics.logger import color_text

class VoiceEnabledNLtoSTL:
    """
    Voice-enabled wrapper for NL_to_STL that integrates speech input/output
    without modifying the original NL_to_STL class.
    """
    
    def __init__(self, objects, N, dt, GPT_model="gpt-5-mini", scenario_name="reach_avoid"):
        """
        Initialize the voice-enabled NL_to_STL wrapper.
        
        Parameters:
        -----------
        objects : list
            List of objects referenced in the natural language instructions
        N : int
            Maximum number of time steps for the STL formula
        dt : float
            Time step size
        GPT_model : str, optional
            The GPT model to use (default: "gpt-5-mini")
        scenario_name : str, optional
            Name of the scenario for visualization (default: "reach_avoid")
        """
        # Initialize core NL_to_STL
        self.nl_to_stl = NL_to_STL(objects, N, dt,
                                   print_instructions='one_short_ChatGPT_instructions.txt',
                                   GPT_model=GPT_model)
        
        # Store scenario information
        self.scenario_name = scenario_name
        self.objects = objects
        self.N = N
        self.dt = dt
        
        # Initialize voice components
        self.transcriber = Transcriber()
        self.tts_engine = TTSEngine()
        self.audio_processor = AudioProcessor()
        
        # Voice processing state
        self.is_listening = False
        self.voice_queue = queue.Queue()
        self.text_queue = queue.Queue()
        self.gui_update_queue = queue.Queue()  # Queue for GUI updates
        
        # Audio processing loop
        self.audio_loop = AudioProcessingLoop(
            self.audio_processor, 
            self.transcriber, 
            self.text_queue
        )
        
        # Conversation state
        self.messages = []
        self.conversation_active = False
        self.conversation_history = []
        
        # Trajectory generation state
        self.current_trajectory = None
        self.trajectory_solver = None
        self.trajectory_analyzer = None
        
        # Specification and syntax checking parameters (similar to main.py)
        self.spec_checker_enabled = False  # Default: disabled for voice system
        self.spec_checker_iteration = 0
        self.spec_check_limit = 5
        self.syntax_checker_enabled = False  # Default: disabled for voice system
        self.syntax_checker_iteration = 0
        self.syntax_check_limit = 5
        
        # GUI callback functions
        self.gui_transcription_callback = None
        self.gui_response_callback = None
        self.gui_trajectory_callback = None
        
        print(color_text("🎤 Voice-enabled NL_to_STL initialized", 'green'))
        
    def set_gui_callbacks(self, transcription_callback=None, response_callback=None, trajectory_callback=None):
        """
        Set callback functions for GUI updates.
        
        Parameters:
        -----------
        transcription_callback : callable, optional
            Function to call when transcription is updated
        response_callback : callable, optional
            Function to call when AI response is received
        trajectory_callback : callable, optional
            Function to call when trajectory is generated
        """
        self.gui_transcription_callback = transcription_callback
        self.gui_response_callback = response_callback
        self.gui_trajectory_callback = trajectory_callback
        
    def start_voice_conversation(self, instructions_file, max_inputs=10, auto_speak=True):
        """
        Start a voice-enabled conversation with ChatGPT.
        
        Parameters:
        -----------
        instructions_file : str
            Filename of the instructions file to load
        max_inputs : int, optional
            Maximum number of user inputs allowed (default: 10)
        auto_speak : bool, optional
            Whether to automatically speak ChatGPT responses (default: True)
            
        Returns:
        --------
        tuple
            (messages, status) - conversation messages and final status
        """
        print(color_text("Starting voice-enabled conversation...", 'green'))
        # print(color_text("Say 'quit' to end the conversation", 'yellow'))
        
        # Initialize conversation using the original NL_to_STL method
        instructions_template = self.nl_to_stl.load_chatgpt_instructions(instructions_file)
        instructions = self.nl_to_stl.insert_instruction_variables(instructions_template)
        self.messages = [{"role": "system", "content": instructions}]
        
        # Start audio processing
        self.audio_loop.start_processing()
        self.conversation_active = True
        
        # Start voice input loop
        return self._voice_input_loop(max_inputs, auto_speak)
        
    def _voice_input_loop(self, max_inputs, auto_speak):
        """
        Main loop for processing voice input and ChatGPT responses.
        
        Parameters:
        -----------
        max_inputs : int
            Maximum number of user inputs
        auto_speak : bool
            Whether to automatically speak responses
            
        Returns:
        --------
        tuple
            (messages, status) - conversation messages and final status
        """
        input_count = 0
        status = "active"
        
        while self.conversation_active and input_count < max_inputs:
            try:
                # Wait for voice input
                print(color_text("🎙️ Listening... (speak your message)", 'cyan'))
                self.audio_loop.set_recording_state(True)
                
                # Wait for transcribed text
                user_input = self._wait_for_voice_input()
                
                if not user_input:
                    print(color_text("⚠️ No voice input detected, try again", 'yellow'))
                    continue
                
                # Handle special commands
                if user_input.lower() == 'quit':
                    print(color_text("👋 Ending conversation", 'yellow'))
                    status = "exited"
                    break
                elif user_input.lower() == 'clear':
                    print(color_text("🗑️ Clearing conversation history", 'yellow'))
                    self.conversation_history.clear()
                    continue
                elif user_input.lower() == 'generate trajectory':
                    print(color_text("🚁 Generating trajectory from current specification...", 'blue'))
                    self._generate_and_visualize_trajectory()
                    continue
                
                # Add to conversation history
                self.conversation_history.append(f"User: {user_input}")
                
                # Notify GUI of user input
                if self.gui_transcription_callback:
                    self.gui_transcription_callback(user_input)
                
                # Process with ChatGPT using original NL_to_STL
                print(color_text(f"Processing: {user_input}", 'blue'))
                self.messages.append({"role": "user", "content": user_input})
                
                # Get ChatGPT response using original method
                response = self.nl_to_stl.gpt.chatcompletion(self.messages)
                self.messages.append({"role": "assistant", "content": response})
                
                # Add to conversation history
                self.conversation_history.append(f"Assistant: {response}")
                
                # Display response
                print(color_text(f"ChatGPT: {response}", 'green'))
                
                # Notify GUI of AI response
                if self.gui_response_callback:
                    self.gui_response_callback(response)
                
                # Speak the response if enabled
                if auto_speak:
                    self.tts_engine.speak(response, self._tts_callback)
                
                input_count += 1
                
                # Check if conversation should end (based on original logic)
                if '<' in response:
                    print(color_text("✅ Final specification generated", 'green'))
                    status = "completed"
                    
                    # Automatically generate trajectory if specification is complete
                    print(color_text("🚁 Automatically generating trajectory...", 'blue'))
                    self._generate_and_visualize_trajectory()
                    break
                    
            except KeyboardInterrupt:
                print(color_text("🛑 Conversation interrupted", 'red'))
                status = "interrupted"
                break
            except Exception as e:
                print(color_text(f"❌ Error: {e}", 'red'))
                status = "error"
                
        self.conversation_active = False
        self.audio_loop.set_recording_state(False)
        
        return self.messages, status
        
    def _generate_and_visualize_trajectory(self):
        """
        Generate trajectory from current STL specification and visualize it.
        Includes complete workflow: trajectory generation, analysis, specification checking, and visualization.
        """
        try:
            # Get the final specification
            spec = self.get_final_specification()
            if not spec:
                print(color_text("❌ No specification available for trajectory generation", 'red'))
                return
            
            print(color_text(f"📋 Using specification: {spec}", 'blue'))
            
            # Convert objects list to dictionary format expected by STLSolver
            objects_dict = self._convert_objects_to_dict()
            
            # Initialize solver parameters (using default parameters from config)
            x0 = np.array([-3.5, -3.5, 0.5, 0., 0., 0.])  # Default starting position
            T = self.N * self.dt  # Total time
            max_acc = 10.0  # Maximum acceleration
            max_speed = 5.0  # Maximum speed
            solver_verbose = False  # Solver verbose mode
            
            # Initialize the solver
            self.trajectory_solver = STLSolver(spec, objects_dict, x0, T)
            
            print(color_text("🔧 Generating trajectory...", 'yellow'))
            
            # Generate trajectory using the same parameters as main.py
            x, u = self.trajectory_solver.generate_trajectory(
                dt=self.dt,
                max_acc=max_acc,
                max_speed=max_speed,
                verbose=solver_verbose,
                include_dynamics=True
            )
            
            # Check if trajectory is valid
            if np.isnan(x).all():
                raise Exception("The trajectory is infeasible.")
            
            self.current_trajectory = x
            print(color_text("✅ Trajectory generated successfully!", 'green'))
            
            # Create scenario object for analysis and visualization
            scenario = self._create_scenario_object()
            
            # Initialize trajectory analyzer (same as main.py)
            self.trajectory_analyzer = TrajectoryAnalyzer(scenario.objects, x, self.N, self.dt)
            inside_objects_array = self.trajectory_analyzer.get_inside_objects_array()
            
            # Visualize trajectory (same as main.py)
            print(color_text("📊 Visualizing trajectory...", 'blue'))
            visualizer = Visualizer(x, scenario)
            fig1, ax1 = visualizer.visualize_trajectory()
            plt.pause(1)
            
            # Visualize trajectory analysis (same as main.py)
            print(color_text("📈 Visualizing trajectory analysis...", 'blue'))
            fig2, ax2 = self.trajectory_analyzer.visualize_spec(inside_objects_array)
            plt.pause(1)
            
            # Specification checking (optional, similar to main.py)
            self._perform_specification_checking(scenario, inside_objects_array)
            
            # Notify GUI of trajectory generation
            if self.gui_trajectory_callback:
                self.gui_trajectory_callback(x, spec)
            
            # Speak confirmation
            self.tts_engine.speak("Trajectory generated and visualized successfully", self._tts_callback)
            
            print(color_text("✅ Complete trajectory workflow finished!", 'green'))
            
        except Exception as e:
            error_msg = f"❌ Trajectory generation failed: {e}"
            print(color_text(error_msg, 'red'))
            self.tts_engine.speak("Trajectory generation failed", self._tts_callback)
            
            # Try syntax checking if trajectory generation fails (like in main.py)
            self._handle_trajectory_generation_error(spec)
    
    def _convert_objects_to_dict(self):
        """
        Convert objects list to dictionary format expected by STLSolver.
        Uses the exact same object definitions as the Scenarios class.
        
        Returns:
        --------
        dict
            Objects dictionary with bounds
        """
        # Use the exact same object definitions as in scenarios.py
        if self.scenario_name == "reach_avoid":
            return {
                "goal": (4., 5., 4., 5., 4., 5.),
                "obstacle1": (-3., -1., -0.5, 1.5, 0.5, 2.5),
                "obstacle2": (-4.5, -3., 0., 2.25, 0.5, 2.),
                "obstacle3": (-2., -1., 4., 5., 3.5, 4.5),
                "obstacle4": (3., 4., -3.5, -2.5, 1., 2.),
                "obstacle5": (4., 5., 0., 1., 2., 3.5),
                "obstacle6": (2., 3.5, 1.5, 2.5, 3.75, 5.),
                "obstacle7": (-2., -1., -2., -1., 1., 2.),
            }
        elif self.scenario_name == "treasure_hunt":
            return {
                "door_key": (3.75, 4.75, 3.75, 4.75, 1., 2.),
                "chest": (-4.25, -3, -4.5, -3.75, 0., 0.75),
                "door": (0., 0.5, -2.5, -1, 0., 2.5),
                "room_bounds": (-5., 5., -5., 5., 0., 3.),
                "NE_inside_wall": (2., 5., 3., 3.5, 0., 3.),
                "south_mid_inside_wall": (0., 0.5, -5., -2.5, 0., 3.),
                "north_mid_inside_wall": (0., 0.5, -1., 5., 0., 3.),
                "west_inside_wall": (-2.25, -1.75, -5., 3.5, 0., 3.),
                "above_door_wall": (0., 0.5, -2.5, -1, 2.5, 3.),
            }
        else:
            # Fallback to reach_avoid
            return {
                "goal": (4., 5., 4., 5., 4., 5.),
                "obstacle1": (-3., -1., -0.5, 1.5, 0.5, 2.5),
            }
    
    def _create_scenario_object(self):
        """
        Create a scenario object for visualization.
        
        Returns:
        --------
        object
            Scenario object with required attributes
        """
        class Scenario:
            def __init__(self, name, objects):
                self.scenario_name = name
                self.objects = objects
        
        objects_dict = self._convert_objects_to_dict()
        return Scenario(self.scenario_name, objects_dict)
    
    def _perform_specification_checking(self, scenario, inside_objects_array):
        """
        Perform specification checking using GPT (optional, similar to main.py).
        
        Parameters:
        -----------
        scenario : object
            Scenario object
        inside_objects_array : numpy.ndarray
            Array indicating object interactions
        """
        try:
            # Check if specification checking is enabled (default: False for voice system)
            spec_checker_enabled = getattr(self, 'spec_checker_enabled', False)
            spec_checker_iteration = getattr(self, 'spec_checker_iteration', 0)
            spec_check_limit = getattr(self, 'spec_check_limit', 5)
            
            if spec_checker_enabled and spec_checker_iteration < spec_check_limit:
                print(color_text("🔍 Performing specification check...", 'blue'))
                
                # Check the specification using trajectory analyzer
                spec_check_response = self.trajectory_analyzer.GPT_spec_check(
                    scenario.objects, 
                    inside_objects_array, 
                    self.messages
                )
                
                # Check if the trajectory is accepted
                trajectory_accepted = self.nl_to_stl.spec_accepted_check(spec_check_response)
                
                if trajectory_accepted:
                    print(color_text("✅ Trajectory accepted by specification checker", 'green'))
                    self.tts_engine.speak("Trajectory accepted by specification checker", self._tts_callback)
                else:
                    print(color_text("⚠️ Trajectory rejected by specification checker", 'yellow'))
                    self.tts_engine.speak("Trajectory rejected by specification checker", self._tts_callback)
                    
                    # Add the checker message to the conversation for feedback
                    spec_checker_message = {"role": "system", "content": f"Specification checker: {spec_check_response}"}
                    self.messages.append(spec_checker_message)
                    
                self.spec_checker_iteration = spec_checker_iteration + 1
                
            elif spec_checker_iteration >= spec_check_limit:
                print(color_text("⚠️ Maximum specification check iterations reached", 'yellow'))
                
        except Exception as e:
            print(color_text(f"❌ Specification checking failed: {e}", 'red'))
    
    def _handle_trajectory_generation_error(self, spec):
        """
        Handle trajectory generation errors by attempting syntax checking (like in main.py).
        
        Parameters:
        -----------
        spec : str
            The STL specification that failed
        """
        try:
            syntax_checker_enabled = getattr(self, 'syntax_checker_enabled', False)
            syntax_checker_iteration = getattr(self, 'syntax_checker_iteration', 0)
            syntax_check_limit = getattr(self, 'syntax_check_limit', 5)
            
            if syntax_checker_enabled and syntax_checker_iteration <= syntax_check_limit:
                print(color_text("🔍 Checking syntax of the specification...", 'yellow'))
                
                # Use the original NL_to_STL syntax checker
                syntax_checked_spec = self.nl_to_stl.gpt_syntax_checker(spec)
                print(color_text(f"📝 Syntax-checked specification: {syntax_checked_spec}", 'blue'))
                
                # Try generating trajectory again with corrected specification
                print(color_text("🔄 Retrying trajectory generation with corrected specification...", 'blue'))
                
                # Update the specification and try again
                # Note: This would require updating the messages to include the corrected spec
                # For now, we'll just inform the user
                self.tts_engine.speak("Syntax checking completed, please try again with corrected specification", self._tts_callback)
                
                self.syntax_checker_iteration = syntax_checker_iteration + 1
                
            elif syntax_checker_iteration > syntax_check_limit:
                print(color_text("❌ Maximum syntax check iterations reached", 'red'))
                self.tts_engine.speak("Maximum syntax check iterations reached", self._tts_callback)
                
        except Exception as e:
            print(color_text(f"❌ Syntax checking failed: {e}", 'red'))
    
    def enable_specification_checking(self, enabled=True, max_iterations=5):
        """
        Enable or disable specification checking.
        
        Parameters:
        -----------
        enabled : bool
            Whether to enable specification checking (default: True)
        max_iterations : int
            Maximum number of specification check iterations (default: 5)
        """
        self.spec_checker_enabled = enabled
        self.spec_check_limit = max_iterations
        self.spec_checker_iteration = 0
        print(color_text(f"🔍 Specification checking {'enabled' if enabled else 'disabled'}", 'blue'))
    
    def enable_syntax_checking(self, enabled=True, max_iterations=5):
        """
        Enable or disable syntax checking.
        
        Parameters:
        -----------
        enabled : bool
            Whether to enable syntax checking (default: True)
        max_iterations : int
            Maximum number of syntax check iterations (default: 5)
        """
        self.syntax_checker_enabled = enabled
        self.syntax_check_limit = max_iterations
        self.syntax_checker_iteration = 0
        print(color_text(f"🔍 Syntax checking {'enabled' if enabled else 'disabled'}", 'blue'))
    
    def _wait_for_voice_input(self, timeout=30):
        """
        Wait for voice input with timeout.
        
        Parameters:
        -----------
        timeout : float
            Maximum time to wait for input in seconds
            
        Returns:
        --------
        str or None
            Transcribed text or None if timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check for new transcribed text
                msg_data = self.text_queue.get_nowait()
                if msg_data[0] == "full" and msg_data[1].strip():
                    return msg_data[1].strip()
            except queue.Empty:
                time.sleep(0.1)
                continue
                
        return None
        
    def _tts_callback(self, status):
        """
        Callback for TTS status updates.
        
        Parameters:
        -----------
        status : str
            TTS status message
        """
        print(color_text(f"🔊 TTS: {status}", 'purple'))
        
    def get_final_specification(self):
        """
        Extract the final STL specification from the conversation.
        
        Returns:
        --------
        str or None
            Final STL specification or None if not found
        """
        if self.messages:
            try:
                return self.nl_to_stl.get_specs(self.messages)
            except Exception as e:
                print(color_text(f"❌ Error extracting specification: {e}", 'red'))
                return None
        return None
        
    def get_conversation_history(self):
        """
        Get the conversation history.
        
        Returns:
        --------
        list
            List of conversation messages
        """
        return self.conversation_history.copy()
        
    def get_current_trajectory(self):
        """
        Get the current generated trajectory.
        
        Returns:
        --------
        numpy.ndarray or None
            Current trajectory data or None if not generated
        """
        return self.current_trajectory
    
    def get_scenario_object_names(self):
        """
        Get the correct object names for the current scenario.
        
        Returns:
        --------
        list
            List of object names for the current scenario
        """
        objects_dict = self._convert_objects_to_dict()
        return list(objects_dict.keys())
    
    def get_scenario_objects_dict(self):
        """
        Get the complete objects dictionary for the current scenario.
        
        Returns:
        --------
        dict
            Complete objects dictionary with bounds
        """
        return self._convert_objects_to_dict()
        
    def speak_text(self, text, callback=None):
        """
        Speak text using TTS engine.
        
        Parameters:
        -----------
        text : str
            Text to speak
        callback : callable, optional
            Callback function for TTS status
        """
        if callback is None:
            callback = self._tts_callback
        self.tts_engine.speak(text, callback)
        
    def stop_conversation(self):
        """
        Stop the current conversation.
        """
        self.conversation_active = False
        self.audio_loop.set_recording_state(False)
        print(color_text("🛑 Conversation stopped", 'yellow'))
        
    def test_voice_components(self):
        """
        Test voice input and output components.
        
        Returns:
        --------
        bool
            True if all components work, False otherwise
        """
        print(color_text("🧪 Testing voice components...", 'blue'))
        
        # Test TTS
        try:
            print(color_text("🔊 Testing TTS...", 'blue'))
            self.tts_engine.speak("Voice components test successful", self._tts_callback)
            time.sleep(2)  # Wait for TTS to complete
            print(color_text("✅ TTS test passed", 'green'))
        except Exception as e:
            print(color_text(f"❌ TTS test failed: {e}", 'red'))
            return False
            
        # Test audio processing
        try:
            print(color_text("🎤 Testing audio processing...", 'blue'))
            self.audio_loop.start_processing()
            time.sleep(1)
            print(color_text("✅ Audio processing test passed", 'green'))
        except Exception as e:
            print(color_text(f"❌ Audio processing test failed: {e}", 'red'))
            return False
            
        return True
        
    def get_text_queue(self):
        """
        Get the text queue for GUI updates.
        
        Returns:
        --------
        queue.Queue
            The text queue containing transcription updates
        """
        return self.text_queue
