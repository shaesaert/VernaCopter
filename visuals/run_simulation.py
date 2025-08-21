from basics.logger import color_text
import numpy as np
from .pybullet_simulation import run
from basics.scenarios import *

def simulate(pars, scenario, all_x):
    """
    Animates the final trajectory simulation.

    Parameters:
    ----------
    pars : Namespace or dict-like object
        Contains configuration parameters for the simulation, including:
        - animate_final_trajectory (bool): Whether to animate the final trajectory.
        - save_animation (bool): Whether to save the simulation as an animation file.
    scenario : Scenario
        The scenario object defining the simulation environment.
    all_x : ndarray
        Array of waypoints with shape (n_dimensions, n_timesteps).
        The first three rows correspond to x, y, z positions of the waypoints.

    Notes:
    -----
    - Adds interpolated waypoints between trajectory points for smooth animations.
    - Initiates the simulation when the user presses Enter.
    """
    if pars.animate_final_trajectory:
            try:
                waypoints = all_x[:3].T
                N_waypoints = waypoints.shape[0]
                N_extra_points = 5 # extra waypoints to add between waypoints linearly

                # Add extra waypoints
                total_points = N_waypoints + (N_waypoints-1)*N_extra_points
                TARGET_POS = np.zeros((total_points,3))
                TARGET_POS[0] = waypoints[0]
                for i in range(N_waypoints-1):
                    TARGET_POS[(1+N_extra_points)*i] = waypoints[i]
                    for j in range(N_extra_points+1):
                        k = (j+1)/(N_extra_points+1)
                        TARGET_POS[(1+N_extra_points)*i + j] = (1-k)*waypoints[i] + k*waypoints[i+1]

                INIT_RPYS = np.array([[0, 0, 0]])

                # start simulation when the user presses enter
                input("Press Enter to start the simulation.")

                run(waypoints=TARGET_POS, 
                initial_rpys=INIT_RPYS,    
                scenario=scenario,
                save_animation=pars.save_animation)

            except Exception as e:
                print(color_text(f"Failed to animate the final trajectory: {e}", 'yellow'))