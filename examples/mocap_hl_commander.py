# -*- coding: utf-8 -*-
import time
from threading import Thread

import motioncapture
import numpy as np

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.mem import MemoryElement
from cflib.crazyflie.mem import Poly4D
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.utils.reset_estimator import reset_estimator

# URI to the Crazyflie to connect to
uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E702')
host_name = '131.155.34.241'
mocap_system_type = 'vicon'

# The name of the rigid body that represents the Crazyflie
rigid_body_name = 'cf2'

# True: send position and orientation; False: send position only
send_full_pose = True

# When using full pose, the estimator can be sensitive to noise in the orientation data when yaw is close to +/- 90
# degrees. If this is a problem, increase orientation_std_dev a bit. The default value in the firmware is 4.5e-3.
orientation_std_dev = 8.0e-3

class MocapWrapper(Thread):
    def __init__(self, body_name):
        Thread.__init__(self)

        self.body_name = body_name
        self.on_pose = None
        self._stay_open = True

        self.start()

    def close(self):
        self._stay_open = False

    def run(self):
        mc = motioncapture.connect(mocap_system_type, {'hostname': host_name})
        while self._stay_open:
            mc.waitForNextFrame()
            for name, obj in mc.rigidBodies.items():
                if name == self.body_name:
                    if self.on_pose:
                        pos = obj.position
                        self.on_pose([pos[0], pos[1], pos[2], obj.rotation])


def send_extpose_quat(cf, x, y, z, quat):
    """
    Send the current Crazyflie X, Y, Z position and attitude as a quaternion.
    This is going to be forwarded to the Crazyflie's position estimator.
    """
    if send_full_pose:
        cf.extpos.send_extpose(x, y, z, quat.x, quat.y, quat.z, quat.w)
    else:
        cf.extpos.send_extpos(x, y, z)


def adjust_orientation_sensitivity(cf):
    cf.param.set_value('locSrv.extQuatStdDev', orientation_std_dev)


def activate_kalman_estimator(cf):
    cf.param.set_value('stabilizer.estimator', '2')

    # Set the std deviation for the quaternion data pushed into the
    # kalman filter. The default value seems to be a bit too low.
    cf.param.set_value('locSrv.extQuatStdDev', 0.06)


def activate_mellinger_controller(cf):
    cf.param.set_value('stabilizer.controller', '2')


def transform_wp_to_projector(x_old, y_old):
    x_new = x_old * 1.15/5.0
    y_new = y_old * 1.15/5.0
    return x_new, y_new

def run_sequence(cf):
    commander = cf.high_level_commander

    waypoints = np.load("/home/amc/crazyflie-lib-python/examples/mocap/4_waypoints.npy") # divide values by 4 for easily fitting it in arena

    waypoints = waypoints[:, :waypoints.shape[1] // 2] # take only first half of array, because it is sort of concatenated?

    commander.takeoff(0.15, 2.0)
    time.sleep(3.0)
    waypoint_duration = 0.75 # sec
    
    # let the drone go to each corner
    # try:
        
    #     scaled_wp_x, scaled_wp_y = transform_wp_to_projector(5.0, 5.0)
    #     print(scaled_wp_x, scaled_wp_y)
    #     commander.go_to(scaled_wp_x, scaled_wp_y, 0.15, yaw=0.0, duration_s=waypoint_duration)
    #     time.sleep(waypoint_duration)

    #     time.sleep(2.0)

    #     scaled_wp_x, scaled_wp_y = transform_wp_to_projector(5.0, -5.0)
    #     print(scaled_wp_x, scaled_wp_y)
    #     commander.go_to(scaled_wp_x, scaled_wp_y, 0.15, yaw=0.0, duration_s=waypoint_duration)
    #     time.sleep(waypoint_duration)

    #     time.sleep(2.0)

    #     scaled_wp_x, scaled_wp_y = transform_wp_to_projector(-5.0, -5.0)
    #     print(scaled_wp_x, scaled_wp_y)
    #     commander.go_to(scaled_wp_x, scaled_wp_y, 0.15, yaw=0.0, duration_s=waypoint_duration)
    #     time.sleep(waypoint_duration)

    #     time.sleep(2.0)

    #     scaled_wp_x, scaled_wp_y = transform_wp_to_projector(-5.0, 5.0)
    #     print(scaled_wp_x, scaled_wp_y)
    #     commander.go_to(scaled_wp_x, scaled_wp_y, 0.15, yaw=0.0, duration_s=waypoint_duration)
    #     time.sleep(waypoint_duration)

    #     time.sleep(2.0)

    # except:
    #     commander.send_stop_setpoint()

    try:
        for _, wp in enumerate(waypoints.T[::2,:]):
            scaled_wp_x, scaled_wp_y = transform_wp_to_projector(wp[0], wp[1])
            print(scaled_wp_x, scaled_wp_y)
            commander.go_to(scaled_wp_x, scaled_wp_y, 0*wp[2]/2+0.15, yaw=0.0, duration_s=waypoint_duration)
            time.sleep(waypoint_duration)
    except:
        commander.send_stop_setpoint()


    commander.land(0.0, 2.0)
    time.sleep(2)
    commander.stop()


if __name__ == '__main__':
    cflib.crtp.init_drivers()

    # Connect to the mocap system
    mocap_wrapper = MocapWrapper(rigid_body_name)

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        cf = scf.cf

        # Set up a callback to handle data from the mocap system
        mocap_wrapper.on_pose = lambda pose: send_extpose_quat(cf, pose[0], pose[1], pose[2], pose[3])

        adjust_orientation_sensitivity(cf)
        activate_kalman_estimator(cf)
        # activate_mellinger_controller(cf)
        reset_estimator(cf)

        # Arm the Crazyflie
        cf.platform.send_arming_request(True)
        time.sleep(1.0)

        run_sequence(cf)

    mocap_wrapper.close()
    cf.commander.send_stop_setpoint()

        
