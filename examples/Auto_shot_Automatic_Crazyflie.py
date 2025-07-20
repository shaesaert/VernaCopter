"""
Auto_shot_Automatic_Crazyflie.py

Runs the full VernaCopter + Crazyflie pipeline automatically using predefined parameters.
"""

from basics.config import One_shot_parameters
from main import main
from experiments.save_results import save_results
from crazy_controller import fly_waypoints

import numpy as np

scenario_name = "treasure_hunt"  # or "reach_avoid"
pars = One_shot_parameters(scenario_name=scenario_name)

try:
    # Step 1: Run the VernaCopter planner (generates trajectory as all_x)
    messages, task_accomplished, all_x = main(pars)

    # Step 2: Convert all_x (3xN NumPy array) to list of (x, y, z) tuples
    waypoints = list(zip(all_x[0], all_x[1], all_x[2]))

    # Step 3: Scale for physical environment
    SCALE_FOR_REAL_ENV = True
    SCALE_FACTOR = 0.3
    if SCALE_FOR_REAL_ENV:
        waypoints = [(x * SCALE_FACTOR, y * SCALE_FACTOR, z * SCALE_FACTOR) for (x, y, z) in waypoints]

    # Step 4: Fly waypoints with Crazyflie (only if task succeeded)
    if task_accomplished:
        fly_waypoints(waypoints)
    else:
        print("[WARNING] Task was not accomplished. Skipping flight.")

except Exception as e:
    print("[ERROR]", e)
    task_accomplished = False
    messages = []
    waypoints = []

# Step 5: Save experiment results (optional)
if pars.save_results:
    save_results(pars, messages, task_accomplished, waypoints)
