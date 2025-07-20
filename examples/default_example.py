"""
default_example.py

This script demonstrates the full system in action using a default example.
It initializes parameters for a chosen scenario, runs the main program to 
generate and execute a task, and optionally saves the results.

The default example can be used interactively with the system and is ideal
for showcasing its capabilities.
"""

from basics.config import Default_parameters                # Import the default parameters
from main import main                                       # Import the main program
from experiments.save_results import save_results           # Import the save_results function

scenario_name = "treasure_hunt"                             # "reach_avoid", or "treasure_hunt"
pars = Default_parameters(scenario_name = scenario_name)    # Get the parameters

try:
    messages, task_accomplished, waypoints = main(pars)     # Run the main program
except Exception as e: 
    print(e)
    task_accomplished = False 
    messages = []  

if pars.save_results:
        save_results(pars, messages, task_accomplished, waypoints) # Save the results