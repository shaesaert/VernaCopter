"""
main.py

This script runs the VernaCopter framework, translating natural language commands
into drone trajectories using Signal Temporal Logic (STL). It includes conversation 
handling, STL translation, trajectory generation, and visualization.

Modules:
- NL_to_STL: Handles natural language to STL translation.
- STLSolver: Generates drone trajectories from STL specifications.
- TrajectoryAnalyzer: Validates the trajectory using user-defined rules.
- Visualizer and simulate: Handles trajectory visualization and animation.

Author: Teun van de Laar
"""
import logging
from LLM.NL_to_STL import NL_to_STL
from STL.STL_to_path import STLSolver, STL_formulas
from STL.trajectory_analysis import TrajectoryAnalyzer
from basics.logger import color_text
from basics.scenarios import Scenarios
from basics.config import Default_parameters
from visuals.run_simulation import simulate
from visuals.visualization import Visualizer

import numpy as np
import matplotlib.pyplot as plt

def main(pars=Default_parameters()):
    """
    Orchestrates the VernaCopter framework. Sets up a scenario, handles conversations 
    for task specification, generates trajectories, and visualizes results.

    Parameters:
        pars (Default_parameters): Configurable parameters for the system, including 
        scenario details, solver limits, and user settings.

    Returns:
        tuple: (messages, task_accomplished, all_x)
            - messages: The conversation history during the session.
            - task_accomplished: Boolean, True if the task was completed successfully.
            - all_x: Numpy array of the final trajectory.
    """ 

    # Initializations
    scenario = Scenarios(pars.scenario_name)    # Set up the scenario
    T = scenario.T_initial                      # Time horizon in seconds
    N = int(T/pars.dt)                          # total number of time steps
    previous_messages = []                      # Initialize the conversation
    status = "active"                           # Initialize the status of the conversation
    x0 = scenario.x0                            # Initial position
    all_x = np.expand_dims(x0, axis=1)          # Initialize the full trajectory
    processing_feedback = False                 # Initialize the feedback processing flag
    syntax_checked_spec = None                  # Initialize the syntax checked specification
    spec_checker_iteration = 0                  # Initialize the specification check iteration
    syntax_checker_iteration = 0                # Initialize the syntax check iteration

    if pars.show_map: scenario.show_map()       # Display the map if enabled

    # Translator for natural language to STL
    translator = NL_to_STL(scenario.objects, 
                           N, 
                           pars.dt, 
                           print_instructions=pars.print_ChatGPT_instructions, 
                           GPT_model = pars.GPT_model,)

    ### Main loop ###
    while status == "active":
        """
        Main workflow for trajectory generation and validation:
        1. Handles conversations for task input.
        2. Converts natural language to STL.
        3. Solves trajectory optimization problem.
        4. Validates and visualizes results.
        """

        # Initialize/reset flags for validation and feedback
        trajectory_accepted = False

        # Generate STL specification
        if syntax_checked_spec is None: 
            messages, status = translator.gpt_conversation(
                instructions_file=pars.instructions_file, 
                previous_messages=previous_messages, 
                processing_feedback=processing_feedback, 
                status=status, automated_user=pars.automated_user, 
                automated_user_input=scenario.automated_user_input,
                )
            
            if status == "exited": # Break loop if user exits
                break
            
            # Translate conversation into STL specification
            spec = translator.get_specs(messages)
            processing_feedback = False

        else:
            # Use syntax-checked STL specification
            spec = syntax_checked_spec
            syntax_checked_spec = None
        print("Extracted specification: ", spec)

        # Initialize the solver with the STL specification
        solver = STLSolver(spec, scenario.objects, x0, T,)

        print(color_text("Generating the trajectory...", 'yellow'))
        try:
            # Generate trajectory
            x,_ = solver.generate_trajectory(
                pars.dt, 
                pars.max_acc, 
                pars.max_speed, 
                verbose=pars.solver_verbose, 
                include_dynamics=True
                )
            trajectory_analyzer = TrajectoryAnalyzer(scenario.objects, x, N, pars.dt)    # Initialize the specification checker
            inside_objects_array = trajectory_analyzer.get_inside_objects_array()  # Get array with trajectory analysis
            visualizer = Visualizer(x, scenario)                            # Initialize the visualizer
            fig, ax = visualizer.visualize_trajectory()                     # Visualize the trajectory
            plt.pause(1)                                                    # Pause for visualization
            fig, ax = trajectory_analyzer.visualize_spec(inside_objects_array) # Visualize the trajectory analysis
            plt.pause(1)                                                    # Pause for visualization

            # Specification checker
            if pars.spec_checker_enabled and spec_checker_iteration < pars.spec_check_limit:
                # Check the specification
                spec_check_response = trajectory_analyzer.GPT_spec_check(
                    scenario.objects, 
                    inside_objects_array, 
                    messages)
                # Check if the trajectory is accepted
                trajectory_accepted = translator.spec_accepted_check(spec_check_response)

                # Add the checker message to the conversation if the trajectory is rejected
                if not trajectory_accepted:
                    print(color_text("The trajectory is rejected by the checker.", 'yellow'))
                    spec_checker_message = {"role": "system", "content": f"Specification checker: {spec_check_response}"}
                    messages.append(spec_checker_message)
                    processing_feedback = True
                spec_checker_iteration += 1
            
            # Terminate the program if the maximum number of spec check iterations is reached
            elif spec_checker_iteration > pars.spec_check_limit:
                print(color_text("The program is terminated.", 'yellow'), "Exceeded the maximum number of spec check iterations.")
                break
            
            # Raise an exception if no meaningful trajectory is generated
            if np.isnan(x).all():
                raise Exception("The trajectory is infeasible.")
        
            if pars.manual_trajectory_check_enabled:
                # Ask the user to accept or reject the trajectory
                while True:
                    response = input("Accept the trajectory? (y/n): ")
                    if response.lower() == 'y':
                        print(color_text("The trajectory is accepted.", 'yellow'))
                        trajectory_accepted = True
                        break  # Exit the loop since the trajectory is accepted
                    elif response.lower() == 'n':
                        print(color_text("The trajectory is rejected.", 'yellow'))
                        trajectory_accepted = False
                        break  # Exit the loop since the trajectory is rejected
                    else:
                        print("Invalid input. Please enter 'y' or 'n'.")

            if trajectory_accepted:
                # Add the trajectory to the full trajectory
                all_x = np.hstack((all_x, x[:,1:]))
                x0 = x[:, -1] # Update the initial position for the next trajectory
                print("New position after trajectory: ", x0)

        # If the trajectory generation fails, break the loop
        except Exception as e:
            logging.error('Error at trajectory generation and checking %s', 'division', exc_info=e)
            print(color_text("The trajectory is infeasible.", 'yellow'))
            if pars.syntax_checker_enabled and syntax_checker_iteration <= pars.syntax_check_limit: 
                # Check the syntax of the specification
                print(color_text("Checking the syntax of the specification...", 'yellow')) 
                syntax_checked_spec = translator.gpt_syntax_checker(spec)
                syntax_checker_iteration += 1
            
            # Terminate the program if the maximum number of syntax check iterations is reached
            elif syntax_checker_iteration > pars.syntax_check_limit:
                print(color_text("The program is terminated.", 'yellow'), "Exceeded the maximum number of syntax check iterations.")
                break


        previous_messages = messages # Update the conversation history

        # Exit the loop directly if the automated user is enabled and the trajectory is accepted
        if pars.automated_user and (trajectory_accepted or not pars.spec_checker_enabled):
            if x is not None:
                all_x = np.hstack((all_x, x[:,1:]))
            break
        
    # Visualize the full trajectory
    plt.close('all')
    if all_x.shape[1] == 1:
        print(color_text("No trajectories were accepted. Exiting the program.", 'yellow'))
    else:
        print(color_text("The full trajectory is generated.", 'yellow'))
        simulate(pars, scenario, all_x) # Animate the final trajectory if enabled

    # Check if the task is accomplished using the specification checker module
    trajectory_analyzer = TrajectoryAnalyzer(scenario.objects, all_x, N, pars.dt)
    inside_objects_array = trajectory_analyzer.get_inside_objects_array()
    task_accomplished = trajectory_analyzer.task_accomplished_check(inside_objects_array, pars.scenario_name)

    print(color_text("The program is completed.", 'yellow'))

    return messages, task_accomplished, all_x

if __name__ == "__main__":
    pars = Default_parameters()
    main()