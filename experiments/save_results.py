"""
save_results.py

This module provides functionality to save experiment results, metadata, and 
optional waypoints to organized directories based on the scenario and user mode (automatic or conversational). 

The results include:
- Messages exchanged during the experiment.
- Metadata about the experiment configuration and execution.
- Waypoints generated during the experiment (if available).

The results are saved in unique files within a scenario-specific directory, ensuring that 
each experiment is logged separately.

Functions:
- save_results(pars, messages, task_accomplished, waypoints=None): Saves the experiment data to disk.
- save_messages(experiments_directory, experiment_id, messages): Saves exchanged messages to a JSON file.
- save_metadata(experiments_directory, experiment_id, messages, pars, task_accomplished): Saves experiment metadata to a JSON file.
- save_waypoints(experiments_directory, experiment_id, waypoints): Saves waypoints to a .npy file (if provided).
"""

import os
import json
from basics.logger import color_text
import numpy as np

def save_results(pars, messages, task_accomplished, waypoints=None):
    """
    Saves the results of an experiment, including messages, metadata, and optional waypoints.

    Parameters:
    - pars (object): Contains experiment parameters and settings, including scenario name and user mode.
    - messages (list): List of message objects exchanged during the experiment.
    - task_accomplished (bool): Indicates whether the experiment's task was successfully completed.
    - waypoints (numpy.ndarray, optional): Waypoints generated during the experiment. Defaults to None.

    This function creates an organized directory structure based on the scenario name and user mode
    (automatic or conversational). It sequentially saves the following files:
    - Messages exchanged during the experiment (<experiment_id>_messages.json).
    - Metadata about the experiment (<experiment_id>_METADATA.json).
    - Waypoints generated during the experiment, if available (<experiment_id>_waypoints.npy).

    Returns:
    None
    """

    print(color_text("Saving the results...", 'yellow')) # Print that the results are being saved     
    
    this_directory = os.path.dirname(os.path.abspath(__file__))         # Get the current directory
    user_mode = 'automatic' if pars.automated_user else 'conversation'  # Determine the user mode

    # Define the directory path for the experiment results
    experiments_directory = os.path.join(this_directory, user_mode, pars.scenario_name)

    # Create the directory if it does not exist
    if not os.path.exists(experiments_directory): os.makedirs(experiments_directory)

    # Determine the next available experiment ID
    last_experiment_id = 0                            
    for file in os.listdir(experiments_directory):         
        if file.endswith(".json"):                          
            filename = file.split('.')[0]                   
            last_experiment_id = max(last_experiment_id, int(filename.split('_')[0]))
    new_experiment_id = last_experiment_id + 1

    save_messages(experiments_directory, new_experiment_id, messages)                           # Save the messages to a file
    save_metadata(experiments_directory, new_experiment_id, messages, pars, task_accomplished)  # Save the metadata to a file
    save_waypoints(experiments_directory, new_experiment_id, waypoints)                         # Save the waypoints to a file

    print(color_text(f"Results saved in {experiments_directory}", 'yellow'))


def save_messages(experiments_directory, experiment_id, messages):
    """
    Saves experiment messages to a JSON file.

    Parameters:
    - experiments_directory (str): Directory where the results will be saved.
    - experiment_id (int): Unique identifier for the current experiment.
    - messages (list): List of message objects exchanged during the experiment.

    The file is named as <experiment_id>_messages.json and is saved in the specified directory.

    Returns:
    None
    """
    messages_file_name = f'{experiment_id}_messages.json'                           # Define the filename for the messages file
    messages_file_path = os.path.join(experiments_directory, messages_file_name)    # Define the full path for the messages file

    with open(messages_file_path, 'w') as f:
        json.dump(messages, f) # Save the messages to the messages file


def save_metadata(experiments_directory, experiment_id, messages, pars, task_accomplished):    
    """
    Saves metadata about the experiment to a JSON file.

    Parameters:
    - experiments_directory (str): Directory where the results will be saved.
    - experiment_id (int): Unique identifier for the current experiment.
    - messages (list): List of message objects exchanged during the experiment.
    - pars (object): Contains experiment parameters and settings.
    - task_accomplished (bool): Indicates whether the experiment's task was successfully completed.

    The metadata includes experiment parameters, the number of user messages, and task accomplishment status.
    The file is named as <experiment_id>_METADATA.json and is saved in the specified directory.

    Returns:
    None
    """

    # find and count number of user messages
    user_message_count = sum(1 for message in messages if message['role'] == 'user')

    metadata = {
        **vars(pars), # Include all parameters in `pars`
        "task_accomplished": task_accomplished,
        "user_message_count": user_message_count,
    }

    metadata_file_name = f'{experiment_id}_METADATA.json'
    metadata_file_path = os.path.join(experiments_directory, metadata_file_name)

    with open(metadata_file_path, 'w') as f:
        json.dump(metadata, f)
            
def save_waypoints(experiments_directory, experiment_id, waypoints):
    """
    Saves waypoints to a .npy file if they are provided.

    Parameters:
    - experiments_directory (str): Directory where the results will be saved.
    - experiment_id (int): Unique identifier for the current experiment.
    - waypoints (numpy.ndarray, optional): Waypoints generated during the experiment. Defaults to an empty array if None.

    The file is named as <experiment_id>_waypoints.npy and is saved in the specified directory.

    Returns:
    None
    """
    if waypoints is None:
        waypoints = np.array([])

    waypoints_file_name = f'{experiment_id}_waypoints.npy'
    waypoints_file_path = os.path.join(experiments_directory, waypoints_file_name)

    np.save(waypoints_file_path, waypoints)