"""
trajectory_analysis.py

This module provides the `TrajectoryAnalyzer` class, which handles tasks related to analyzing trajectories of drones in defined scenarios. 
It supports:
- Checking task specifications using GPT-based evaluation.
- Visualizing trajectories relative to predefined objects.
- Validating task completion based on scenario-specific rules.

Dependencies:
- numpy
- matplotlib
- GPT (custom class for interacting with ChatGPT)
- NL_to_STL (custom class for NL-to-STL conversion)
"""

import numpy as np
import matplotlib.pyplot as plt
from LLM.GPT import GPT
from LLM.NL_to_STL import NL_to_STL
from basics.logger import color_text

class TrajectoryAnalyzer:
    """
    A class to analyze drone trajectories with respect to predefined objects and scenarios.

    Attributes:
    - objects (dict): Dictionary defining the boundaries of objects in the environment.
    - x (ndarray): Array of drone positions at each time step.
    - N (int): Number of time steps.
    - dt (float): Time interval between steps.

    Methods:
    - GPT_spec_check: Uses GPT to validate task specifications based on the drone's trajectory.
    - visualize_spec: Visualizes the drone's trajectory relative to predefined objects.
    - task_accomplished_check: Validates if the task was completed successfully based on scenario-specific conditions.
    - get_inside_objects_text: Generates a text summary of the drone's interactions with objects.
    - get_inside_objects_array: Creates a binary array indicating whether the drone is inside each object at each time step.
    - is_inside: Checks if a point is within a defined object's boundaries.
    """
    def __init__(self, objects, x, N, dt):
        """
        Initializes the TrajectoryAnalyzer with objects, trajectory data, and simulation parameters.

        Parameters:
        - objects (dict): Dictionary with object names as keys and boundary tuples as values.
        - x (ndarray): Array of drone positions at each time step (shape: 3xN).
        - N (int): Number of time steps in the trajectory.
        - dt (float): Time interval between steps.
        """
        self.objects = objects
        self.x = x
        self.N = N
        self.dt = dt

    def GPT_spec_check(self, objects, inside_objects_array, previous_messages):
        """
        Uses GPT to validate task specifications based on the drone's trajectory.

        Parameters:
        - objects (dict): Dictionary defining objects in the environment.
        - inside_objects_array (ndarray): Binary array indicating if the drone is inside objects over time.
        - previous_messages (list): List of previous conversation messages for GPT.

        Returns:
        - str: GPT's response to the specification check.
        """
        gpt = GPT()
        translator = NL_to_STL(objects, self.N, self.dt, print_instructions=True)
        messages=previous_messages[1:-1] # all previous messages except the instructions and final message
    
        instructions_template = translator.load_chatgpt_instructions('spec_check_instructions.txt') # load the instructions template
        instructions = translator.insert_instruction_variables(instructions_template) # insert variables into the instructions template
        messages.insert(0, {"role": "system", "content": instructions}) # insert the instructions at the beginning of the messages

        inside_objects_text = self.get_inside_objects_text(inside_objects_array) # get text description of the inside objects array
        messages.append({"role": "system", "content": inside_objects_text}) # append the inside objects text to the messages  

        print("Instruction messages:", messages)
        response = gpt.chatcompletion(messages) # get response from GPT

        messages.append({"role": "assistant", "content": f"{response}"})

        print(color_text("Specification checker:", 'purple'), response)

        return response

    def visualize_spec(self, inside_objects_array):
        """
        Visualizes the drone's interaction with predefined objects over time.

        Parameters:
        - inside_objects_array (ndarray): Binary array indicating if the drone is inside objects over time.

        Returns:
        - tuple: The created figure and axes objects.
        """
        # Show black and white image of the points inside the objects
        N = inside_objects_array.shape[0]
        T = inside_objects_array.shape[1]
        fig, ax = plt.subplots(figsize=(10,6))
        ax.imshow(inside_objects_array, aspect='auto', cmap='gray')
        ax.set_xlabel('Time Steps')
        # set yticks to object names
        ax.set_yticks(range(N))
        ax.set_yticklabels(self.objects.keys())
        # show color bar
        cbar = ax.figure.colorbar(ax.imshow(inside_objects_array, aspect='auto', cmap='gray'))
        cbar.set_label('Inside Object')
        #show lines between the objects
        for i in range(N-1):
            ax.axhline(i+0.5, color='gray', linewidth=0.5)
        # show vertical lines for every 5 time steps
        for i in range(0,T,5):
            ax.axvline(i, color='gray', linewidth=0.5)

        return fig, ax
    
    def task_accomplished_check(self, inside_objects_array, scenario_name):
        """
        Validates whether the task was accomplished based on the scenario.

        Parameters:
        - inside_objects_array (ndarray): Binary array indicating if the drone is inside objects over time.
        - scenario_name (str): Name of the scenario ('reach_avoid' or 'treasure_hunt').

        Returns:
        - bool: True if the task was accomplished, False otherwise.
        """
        objects_inside = {}
        for i, object in enumerate(self.objects.keys()):
            objects_inside[object] = inside_objects_array[i,:]

        if scenario_name == "reach_avoid":
            # test if goal is reached
            goal_reached = 1 in objects_inside['goal']

            # test if any obstacle is crossed
            obstacles_avoided = True
            for object in self.objects.keys():
                if 'obstacle' in object:
                    obstacle_crossed = 1 in objects_inside[object]
                    if obstacle_crossed: obstacles_avoided = False

            task_accomplished = False
            if goal_reached and obstacles_avoided:
                print(color_text("Task accomplished:", 'green'), "All conditions are met.")
                task_accomplished = True
            elif not goal_reached:
                print(color_text("Task failed:", 'red'), "The goal was not reached.")
            elif not obstacles_avoided:
                print(color_text("Task failed:", 'red'), "An obstacle was crossed.")
            else:
                print(color_text("Task failed:", 'red'), "Unknown failure.")
                
            return task_accomplished
        
        elif scenario_name == "treasure_hunt":
            # test if chest is reached
            chest_reached = 1 in objects_inside['chest']
            
            # test if all the walls are avoided
            walls_avoided = True
            for object in self.objects.keys():
                if 'wall' in object:
                    wall_crossed = 1 in objects_inside[object]
                    if wall_crossed: walls_avoided = False

            # test if the door is crossed before the key is reached
            key_time = np.where(objects_inside['door_key'] == 1)[0]
            if key_time.size != 0:
                key_crossed = True
                key_time = key_time[0]
            else: 
                key_crossed = False

            door_time = np.where(objects_inside['door'] == 1)[0]
            if door_time.size != 0:
                door_crossed = True
                door_time = door_time[0]
            else:
                door_crossed = False

            door_before_key = door_crossed and key_crossed and door_time < key_time

            task_accomplished = False
            if chest_reached and walls_avoided and not door_before_key:
                print(color_text("Task accomplished:", 'green'), "All conditions are met.")
                task_accomplished = True
            elif not chest_reached:
                print(color_text("Task failed:", 'red'), "The chest was not reached.")
            elif not walls_avoided:
                print(color_text("Task failed:", 'red'), "A wall was crossed.")
            elif door_before_key:
                print(color_text("Task failed:", 'red'), "The door was crossed before the key was reached.")
            else:
                print(color_text("Task failed:", 'red'), "Unknown failure.")

            return task_accomplished

    def get_inside_objects_text(self, inside_objects_array):
        """
        Generates a textual summary of the drone's interactions with objects.

        Parameters:
        - inside_objects_array (ndarray): Binary array indicating if the drone is inside objects over time.

        Returns:
        - str: Text summary of interactions.
        """

        N = inside_objects_array.shape[0]
        T = inside_objects_array.shape[1]
        output = ""
        for i, object in enumerate(self.objects.keys()):
            if np.all(inside_objects_array[i,:] == 1):
                output += f"The drone is always inside the {object}.\n"
            elif np.all(inside_objects_array[i,:] == 0):
                output += f"The drone is never inside the {object}.\n"
            else:
                inside_times = np.where(inside_objects_array[i,:] == 1)[0] # get the times when the drone is inside the object
                output += f"The drone is inside the {object} at times {inside_times}.\n"
        return output
    
    def get_inside_objects_array(self):
        """
        Creates a binary array indicating whether the drone is inside each object at each time step.

        Returns:
        - ndarray: Binary array (shape: NxT) for N objects over T time steps.
        """
        T = self.x.shape[1]
        N = len(self.objects)
        inside_array = np.zeros((N,T))
        for i, object in enumerate(self.objects.values()):
            for j in range(T):
                inside_array[i,j] = self.is_inside(self.x[:3,j], object)

        return inside_array

    def is_inside(self, point, object):
        """
        Checks if a given point is inside a specified object's boundaries.

        Parameters:
        - point (ndarray): 3D coordinates of the point (x, y, z).
        - object (tuple): Object boundaries as (xmin, xmax, ymin, ymax, zmin, zmax).

        Returns:
        - int: 1 if the point is inside the object, 0 otherwise.
        """
        x, y, z = point[:3]
        xmin, xmax, ymin, ymax, zmin, zmax = object
        inside_boolean = x >= xmin and x <= xmax and y >= ymin and y <= ymax and z >= zmin and z <= zmax
        return inside_boolean*1