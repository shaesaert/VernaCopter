import numpy as np
from stlpy.systems import LinearSystem
from stlpy.STL import LinearPredicate, NonlinearPredicate
from stlpy.solvers import GurobiMICPSolver

class drone_dynamics:
    """
    A class representing the linear dynamics of a drone using a discrete-time state-space model.

    The state-space equations are defined as:
        x_dot = Ax + Bu
            y = Cx + Du

    where:
        x = [x, y, z, vx, vy, vz] (position and velocity states)
        u = [ax, ay, az] (acceleration inputs)

    The matrices A, B, C, and D are defined as:

    A =    [[0., 0., 0., 1., 0., 0.],   B = [[0., 0., 0.],
            [0., 0., 0., 0., 1., 0.],        [0., 0., 0.],
            [0., 0., 0., 0., 0., 1.],        [0., 0., 0.],
            [0., 0., 0., 0., 0., 0.],        [1., 0., 0.],
            [0., 0., 0., 0., 0., 0.],        [0., 1., 0.],
            [0., 0., 0., 0., 0., 0.]]        [0., 0., 1.]]

    C =    [[1., 0., 0., 0., 0., 0.],   D = [[0., 0., 0.],
            [0., 1., 0., 0., 0., 0.],        [0., 0., 0.],
            [0., 0., 1., 0., 0., 0.],        [0., 0., 0.],
            [0., 0., 0., 0., 0., 0.],        [0., 0., 0.],
            [0., 0., 0., 0., 0., 0.],        [0., 0., 0.],
            [0., 0., 0., 0., 0., 0.]]        [0., 0., 0.]]

    Parameters:
        dt (float): Discretization time step for the dynamics. Default is 0.1.
        max_acc (float): Maximum absolute acceleration for the drone. Default is 10.

    Attributes:
        dt (float): Time step for discretization.
        max_acc (float): Maximum absolute acceleration.
        A (numpy.ndarray): Continuous-time state-space matrix A.
        B (numpy.ndarray): Continuous-time input matrix B.
        C (numpy.ndarray): Output matrix C.
        D (numpy.ndarray): Feedforward matrix D.
        A_tilde (numpy.ndarray): Discretized state-space matrix A.
        B_tilde (numpy.ndarray): Discretized input matrix B.  
    
    Methods:
        getSystem():
            Returns the discrete-time system dynamics as a LinearSystem object
            from the `stlpy` library.
    """

    def __init__(self, dt=0.1, max_acc=10):
        self.dt = dt                            # time step
        self.max_acc = max_acc                  # maximum absolute acceleration

        self.A = np.zeros((6,6))
        self.A[0,3] = 1
        self.A[1,4] = 1
        self.A[2,5] = 1

        self.B = np.zeros((6,3))
        self.B[3,0] = 1
        self.B[4,1] = 1
        self.B[5,2] = 1

        self.C = np.zeros((6,6))
        for i in range(3):  
            self.C[i,i] = 1

        self.D = np.zeros((6,3))

        self.A_tilde = np.eye(6) + self.A*self.dt
        self.B_tilde = self.B*self.dt
    
    def getSystem(self):
        sys = LinearSystem(self.A_tilde,self.B_tilde,self.C,self.D)
        return sys
    

class STLSolver:
    """
    A solver for generating trajectories that satisfy Signal Temporal Logic (STL) specifications
    using the `stlpy` library and Gurobi mixed-integer optimization.

    Parameters:
        spec (str): STL specification as a string that defines the desired behavior.
        objects (dict): Dictionary containing obstacle or goal definitions.
        x0 (numpy.ndarray): Initial state vector [x, y, z, vx, vy, vz]. Default is zeros.
        T (float): Total simulation time in seconds. Default is 10.

    Methods:
        generate_trajectory(dt, max_acc, max_speed, verbose=False, include_dynamics=True):
            Generates a trajectory that satisfies the STL specification.

    Returns:
        x (numpy.ndarray): State trajectory as a function of time.
        u (numpy.ndarray): Control inputs (accelerations) as a function of time.
    """

    def __init__(self, spec, objects, x0 = np.zeros(6,), T=10):
        self.objects = objects
        self.spec = spec
        self.x0 = x0
        self.T = T

    def generate_trajectory(self, dt, max_acc, max_speed, verbose = False, include_dynamics=True):
        self.dt = dt
        self.verbose = verbose
        self.max_acc = max_acc
        self.max_speed = max_speed
        objects = self.objects
        N = int(self.T/self.dt)

        dynamics = drone_dynamics(dt=self.dt, max_acc=max_acc)
            
        sys = dynamics.getSystem()      

        Q = np.zeros((6,6))     # state cost   : penalize position error
        R = np.eye(3)           # control cost : penalize control effort

        N = int(self.T/self.dt)
        solver = GurobiMICPSolver(eval(self.spec), sys, self.x0, N, verbose=self.verbose)
        solver.AddQuadraticCost(Q=Q, R=R)
        u_min = -dynamics.max_acc*np.ones(3,)  # minimum acceleration
        u_max = dynamics.max_acc*np.ones(3,)   # maximum acceleration
        solver.AddControlBounds(u_min, u_max)
        state_bounds = np.array([np.inf, np.inf, np.inf, self.max_speed, self.max_speed, self.max_speed])
        solver.AddStateBounds(-state_bounds, state_bounds)
        
        try:
            x, u, _, _ = solver.Solve()
        except Exception as e:
            raise RuntimeError(f"Solver failed: {e}")

        return x, u


class STL_formulas:
    """
    A utility class for creating Signal Temporal Logic (STL) formulas related to spatial constraints.

    This class provides static methods to generate STL formulas that describe whether
    a point (or system state) is inside or outside a defined cuboid in 3D space. These formulas
    can be used in trajectory planning, constraint satisfaction, or system verification tasks.

    Methods:
        inside_cuboid(bounds, tolerance=0.1):
            Creates an STL formula specifying that the state is inside a defined cuboid.

        outside_cuboid(bounds, tolerance=0.1):
            Creates an STL formula specifying that the state is outside a defined cuboid.
    """
    
    def inside_cuboid(bounds, tolerance=0.1):
        """
        Create an STL formula for being inside a cuboid with specified bounds.

                    +-------------------+ z_max
                   / |                 /|
                  /  |                / |
                 +-------------------+  |
          y_max  |   +               |  + z_min
                 |  /                | /
                 | /                 |/
        y_min    +-------------------+
                 x_min              x_max

        Parameters:
            bounds (tuple): Tuple of the form (x_min, x_max, y_min, y_max, z_min, z_max),
                            defining the cuboid boundaries.
            tolerance (float): Optional spatial tolerance for the cuboid. Default is 0.1.

        Returns:
            STLFormula: An STL formula specifying specifying being inside the cuboid.
        """

        # Unpack the bounds
        x_min, x_max, y_min, y_max, z_min, z_max = bounds

        # Create predicates a*y >= b for each side of the cuboid
        a1 = np.zeros((1,6)); a1[:,0] = 1
        right = LinearPredicate(a1, x_min + tolerance)
        left = LinearPredicate(-a1, -x_max + tolerance)

        a2 = np.zeros((1,6)); a2[:,1] = 1
        front = LinearPredicate(a2, y_min + tolerance)
        back = LinearPredicate(-a2, -y_max + tolerance)

        a3 = np.zeros((1,6)); a3[:,2] = 1
        top = LinearPredicate(a3, z_min + tolerance)
        bottom = LinearPredicate(-a3, -z_max + tolerance)

        # Take the conjuction across all the sides
        inside_cuboid = right & left & front & back & top & bottom

        return inside_cuboid


    def outside_cuboid(bounds, tolerance=0.1):
        """
        Create an STL formula for being outside a cuboid with specified bounds.

                    +-------------------+ z_max
                   / |                 /|
                  /  |                / |
                 +-------------------+  |
          y_max  |   +               |  + z_min
                 |  /                | /
                 | /                 |/
        y_min    +-------------------+
                 x_min              x_max

        Parameters:
            bounds (tuple): Tuple of the form (x_min, x_max, y_min, y_max, z_min, z_max),
                            defining the cuboid boundaries.
            tolerance (float): Optional spatial tolerance for the cuboid. Default is 0.1.

        Returns:
            STLFormula: An STL formula specifying specifying being outside the cuboid.
        """

        # Unpack the bounds
        x_min, x_max, y_min, y_max, z_min, z_max = bounds

        # Create predicates a*y >= b for each side of the rectangle
        a1 = np.zeros((1,6)); a1[:,0] = 1
        right = LinearPredicate(a1, x_max + tolerance)
        left = LinearPredicate(-a1, -x_min + tolerance)

        a2 = np.zeros((1,6)); a2[:,1] = 1
        front = LinearPredicate(a2, y_max + tolerance)
        back = LinearPredicate(-a2, -y_min + tolerance)

        a3 = np.zeros((1,6)); a3[:,2] = 1
        top = LinearPredicate(a3, z_max + tolerance)
        bottom = LinearPredicate(-a3, -z_min + tolerance)

        # Take the disjuction across all the sides
        outside_cuboid = right | left | front | back | top | bottom

        return outside_cuboid