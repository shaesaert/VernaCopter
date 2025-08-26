# -*- coding: utf-8 -*-
import time
from threading import Thread

import motioncapture
import numpy as np

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper
from cflib.utils.reset_estimator import reset_estimator


class MocapWrapper(Thread):
    def __init__(self, body_name: str, host_name: str, system_type: str = "vicon"):
        super().__init__(daemon=True)
        self.body_name = body_name
        self.host_name = host_name
        self.system_type = system_type
        self.on_pose = None
        self._stay_open = True
        self._mc = None
        self.start()

    def close(self):
        self._stay_open = False
        # Give run() loop a chance to exit
        self.join(timeout=1.0)
        try:
            if self._mc is not None:
                self._mc.disconnect()
        except Exception:
            pass

    def run(self):
        self._mc = motioncapture.connect(self.system_type, {'hostname': self.host_name})
        while self._stay_open:
            self._mc.waitForNextFrame()
            for name, obj in self._mc.rigidBodies.items():
                if name == self.body_name and self.on_pose:
                    pos = obj.position
                    self.on_pose([pos[0], pos[1], pos[2], obj.rotation])


def send_extpose_quat(cf, x, y, z, quat, send_full_pose: bool):
    if send_full_pose:
        cf.extpos.send_extpose(x, y, z, quat.x, quat.y, quat.z, quat.w)
    else:
        cf.extpos.send_extpos(x, y, z)


def adjust_orientation_sensitivity(cf, orientation_std_dev: float):
    cf.param.set_value('locSrv.extQuatStdDev', orientation_std_dev)


def activate_kalman_estimator(cf):
    cf.param.set_value('stabilizer.estimator', '2')  # Kalman
    # Enable high-level commander (needed for takeoff/go_to/land)
    cf.param.set_value('commander.enHighLevel', '1')


def activate_mellinger_controller(cf):
    cf.param.set_value('stabilizer.controller', '2')  # Mellinger


def transform_wp_to_projector(x_old, y_old, scale_xy=1.15/5.0):
    return x_old * scale_xy, y_old * scale_xy


def run_sequence(cf, waypoints: str, waypoint_duration: float = 0.75):
    commander = cf.high_level_commander

    if waypoints is None:
        waypoints = np.load("/home/amc/crazyflie-lib-python/examples/mocap/4_waypoints.npy")
    # Use first half if the array is concatenated
    # waypoints = waypoints[:, :waypoints.shape[1] // 2]

    # Takeoff
    commander.takeoff(0.15, 2.0)
    time.sleep(3.0)

    try:
        # Step through every other waypoint (matching your original [::2, :])
        for wp in waypoints.T[::2, :]:
            x, y = transform_wp_to_projector(wp[0], wp[1])
            z = 0.0 * wp[2] / 2 + 0.15  # matches your original expression
            commander.go_to(x, y, z, yaw=0.0, duration_s=waypoint_duration)
            time.sleep(waypoint_duration)
    except Exception:
        # Stop current setpoint stream if something goes wrong mid-flight
        commander.send_stop_setpoint()
        raise
    finally:
        # Land and stop either way
        commander.land(0.0, 2.0)
        time.sleep(2.0)
        commander.stop()


def deploy(
    waypoints = None,
    drone_name: str = 'cf2',
    host_name: str = '131.155.34.241',
    send_full_pose: bool = True,
    orientation_std_dev: float = 8.0e-3,
):
    """
    Connects to Crazyflie and Vicon, streams external pose, flies a waypoint sequence,
    and shuts everything down cleanly.
    """
    uri = uri_helper.uri_from_env(default='radio://0/80/2M/E7E7E7E702') # TODO: make this into a variable

    # Drivers once per process
    cflib.crtp.init_drivers()

    # Start mocap streaming thread
    mocap_wrapper = MocapWrapper(drone_name, host_name)

    try:
        with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            cf = scf.cf

            # Stream mocap poses into the estimator
            mocap_wrapper.on_pose = lambda pose: send_extpose_quat(
                cf, pose[0], pose[1], pose[2], pose[3], send_full_pose
            )

            # Estimator/controller setup
            adjust_orientation_sensitivity(cf, orientation_std_dev)
            activate_kalman_estimator(cf)
            # activate_mellinger_controller(cf)  # uncomment if you want Mellinger

            # Reset estimator to align with ext pose input
            reset_estimator(cf)

            # Arm (platform API present on newer firmwares; fall back to legacy if needed)
            try:
                cf.platform.send_arming_request(True)
            except Exception:
                pass
            time.sleep(1.0)

            # Run mission
            run_sequence(cf, waypoints)

            # Disarm
            try:
                cf.platform.send_arming_request(False)
            except Exception:
                pass

            # Make sure we stop sending setpoints
            cf.commander.send_stop_setpoint()

    finally:
        # Always close mocap thread
        mocap_wrapper.close()
