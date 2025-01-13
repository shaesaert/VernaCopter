import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from matplotlib import animation
from basics.scenarios import Scenarios

class Visualizer:
    """
    A class for visualizing trajectories, animating them, and calculating distances to objects.

    Attributes
    ----------
    x : numpy.ndarray
        Waypoints (only positions).
    scenario_name : str
        Name of the scenario.
    objects : dict
        Dictionary containing object boundaries.
    dt : float
        Time step.
    dT : float
        Time to reach target.
    n_points : int
        Number of targets.
    times : numpy.ndarray
        Array of time steps between two targets.
    N : int
        Total number of time steps.
    """
    def __init__(self, x, scenario): 
        """
        Initialize the Visualizer object.

        Parameters
        ----------
        x : numpy.ndarray
            Array of waypoints.
        scenario : Scenarios
            The scenario object containing objects and scenario name.
        animate : bool, optional
            Whether to enable animation (default is False).
        """
        self.x = x[:3, :]                               # waypoints (only positions)
        self.scenario_name = scenario.scenario_name     # scenario name
        self.objects = scenario.objects                 # objects
        self.dt = 0.05                                  # time step
        self.dT = 1                                     # time to reach target
        n = int(self.dT/self.dt)                        # number of time steps between two targets
        self.n_points = self.x.shape[1]                 # number of targets
        self.times = np.linspace(0, self.dT, n)         # time array
        T = (self.n_points-1)*self.dT                   # total time
        self.N = int(T/self.dt)                         # number of time steps
    
    def visualize_trajectory(self):
        """
        Visualize the trajectory in a 3D plot with scenario-specific object representations.

        The function plots the trajectory waypoints, start position, and scenario-specific objects 
        (e.g., obstacles, goals, walls) using color-coded surfaces. Axes limits and visibility 
        are set according to the scenario.

        Returns
        -------
        tuple
            Matplotlib figure and axis objects for further customization or saving.
        """

        # Create the figure and 3D axis
        fig = plt.figure(figsize=(10,10))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title('Trajectory')

        # Plot the trajectory and starting point
        ax.scatter(self.x[0,:], self.x[1,:], self.x[2,:], c='b', label='Trajectory')
        ax.scatter(self.x[0,0], self.x[1,0], self.x[2,0], c='g', label='Start', s=10)

        # Plot scenario-specific objects      
        if self.scenario_name == "reach_avoid": 
            self._visualize_reach_avoid(ax)
        elif self.scenario_name == "treasure_hunt":
            self._visualize_treasure_hunt(ax)

        ax.set_axis_off() # disable axes

        return fig, ax
    
    def _visualize_reach_avoid(self, ax):
        """
        Visualize objects specific to the 'reach_avoid' scenario.
        """
        for object in self.objects:
            center, length, width, height = self.get_clwh(object)
            X, Y, Z = self.make_cuboid(center, (length, width, height))
            color = 'r' if 'obstacle' in object else '#28d778' # red for obstacles, green for goals
            
            ax.plot_surface(X, Y, Z, color=color, rstride=1, cstride=1, alpha=0.2, linewidth=1., edgecolor='k')

        ax.set_xlim(-4.5, 4.5)
        ax.set_ylim(-4, 5)
        ax.set_zlim(0, 5)


    def _visualize_treasure_hunt(self, ax):
        """
        Visualize objects specific to the 'treasure_hunt' scenario.
        """

        colors = {
            'wall': '#a3a3a3',
            'key': '#28d778',
            'door': '#c2853d',
            'chest': '#FFD700',
            'bounds': '#a3a3a3',
        }

        alphas = {
            'wall': 0.05,
            'key': 0.5,
            'door': 0.5,
            'chest': 0.5,
            'bounds': 0.02,
        }

        for object in self.objects:
            # Determine the object type
            keywords = ['key', 'wall', 'chest', 'door', 'bounds']
            for keyword in keywords:
                if keyword in object:
                    object_type = keyword
                    break
            
            # Plot the object
            center, length, width, height = self.get_clwh(object)
            X, Y, Z = self.make_cuboid(center, (length, width, height))
            ax.plot_surface(X, Y, Z, color=colors[object_type], rstride=1, cstride=1, alpha=alphas[object_type], linewidth=1., edgecolor='k')          

            # Add text label
            text_positions = {
                'key': (center[0], center[1], center[2] + 1.2),
                'door': (center[0], center[1] - 2, center[2] + 0.5),
                'chest': (center[0] - 1.5, center[1], center[2] - 0.2),
            }

            if object_type in text_positions:
                ax.text(*text_positions[object_type], object, horizontalalignment='center', verticalalignment='center')

        ax.set_xlim(-4.5, 4.5)
        ax.set_ylim(-4.5, 4.5)
        ax.set_zlim(0, 6.4)

    def get_clwh(self, object):
        """
        Get the center, length, width, and height of an object.

        Parameters
        ----------
        object : str
            The name of the object.

        Returns
        -------
        tuple
            Center, length, width, and height of the object.
        """
        xmin, xmax, ymin, ymax, zmin, zmax = self.objects[object]
        center = ((xmin + xmax)/2, (ymin + ymax)/2, (zmin + zmax)/2)
        length = xmax - xmin
        width = ymax - ymin
        height = zmax - zmin
        return center, length, width, height

    def make_cuboid(self, center, size):
        """
        Create data arrays for cuboid plotting.

        Parameters
        ----------
        center : tuple
            Center of the cuboid (x, y, z).
        size : tuple
            Dimensions of the cuboid (length, width, height).

        Returns
        -------
        tuple
            Arrays for cuboid coordinates (X, Y, Z).
        """

        # suppose axis direction: x: to left; y: to inside; z: to upper
        # get the (left, outside, bottom) point
        o = [a - b / 2 for a, b in zip(center, size)]
        # get the length, width, and height
        l, w, h = size
        x = [[o[0], o[0] + l, o[0] + l, o[0], o[0]],                # x coordinate of points in bottom surface
            [o[0], o[0] + l, o[0] + l, o[0], o[0]],                 # x coordinate of points in upper surface
            [o[0], o[0] + l, o[0] + l, o[0], o[0]],                 # x coordinate of points in outside surface
            [o[0], o[0] + l, o[0] + l, o[0], o[0]]]                 # x coordinate of points in inside surface
        y = [[o[1], o[1], o[1] + w, o[1] + w, o[1]],                # y coordinate of points in bottom surface
            [o[1], o[1], o[1] + w, o[1] + w, o[1]],                 # y coordinate of points in upper surface
            [o[1], o[1], o[1], o[1], o[1]],                         # y coordinate of points in outside surface
            [o[1] + w, o[1] + w, o[1] + w, o[1] + w, o[1] + w]]     # y coordinate of points in inside surface
        z = [[o[2], o[2], o[2], o[2], o[2]],                        # z coordinate of points in bottom surface
            [o[2] + h, o[2] + h, o[2] + h, o[2] + h, o[2] + h],     # z coordinate of points in upper surface
            [o[2], o[2], o[2] + h, o[2] + h, o[2]],                 # z coordinate of points in outside surface
            [o[2], o[2], o[2] + h, o[2] + h, o[2]]]                 # z coordinate of points in inside surface
        return np.asarray(x), np.asarray(y), np.asarray(z)