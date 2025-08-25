"""
one_shot_automatic.py

This script runs the system automatically in a "one-shot" mode without interactive user input. 
It uses predefined parameters and task descriptions for the selected scenario to generate and execute a trajectory.

The results, including system messages, task success, and waypoints, can be saved if specified in the parameters.

This mode is particularly useful for testing and benchmarking system performance.
"""

from basics.config import One_shot_parameters               # Import the one-shot parameters
from main import main                                       # Import the main function
from experiments.save_results import save_results           # Import the save_results function
try:
    from deployment.deploy_on_drone import deploy
    deployment = True
except Exception as e:
    deployment = False
    print("Motion capturing not installed, no real deployment possible")
    print(e)

def run_one_shot(scenario_name="treasure_hunt"):

    pars = One_shot_parameters(scenario_name = scenario_name)   # Get the parameters

    try:
        messages, task_accomplished, waypoints, spec = main(pars)     # Run the main program
    except Exception as e:
        print(e)
        task_accomplished = False
        messages = []

    if pars.save_results:
        save_results(pars, messages, task_accomplished, waypoints, spec) # Save the results

    # TODO: ask user to load old feasible trajectory
    waypoints = None # remove this, once we add a trajectory checker
    if pars.deploy_on_drone & deployment:
         deploy(waypoints)

    return messages, task_accomplished, waypoints, spec


if __name__ == "__main__":
    # Allow running standalone
    _, task_accomplished, _ = run_one_shot()
    print("Task accomplished:", task_accomplished)