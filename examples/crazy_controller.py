# crazy_controller.py

import time
import logging
from cflib.crazyflie import Crazyflie
import cflib.crtp  # Initialize the low-level drivers
from cflib.crazyflie.commander import Commander

# Crazyflie radio URI
URI = "radio://0/80/2M"

# Flight behavior settings
FLIGHT_HEIGHT = 0.5  # meters (used for takeoff hover)
FLIGHT_SPEED = 0.5   # m/s
RETURN_HOME = True   # Go back to start after mission

logging.basicConfig(level=logging.ERROR)


def fly_waypoints(waypoints):
    if not waypoints:
        print("[ERROR] No waypoints to fly.")
        return

    cflib.crtp.init_drivers(enable_debug_driver=False)
    cf = Crazyflie(rw_cache="./cache")

    def connect_callback(link_uri):
        print(f"[INFO] Connected to {link_uri}")

    def disconnect_callback(link_uri):
        print(f"[INFO] Disconnected from {link_uri}")

    cf.connected.add_callback(connect_callback)
    cf.disconnected.add_callback(disconnect_callback)

    print("[INFO] Connecting to Crazyflie...")
    cf.open_link(URI)
    time.sleep(2)

    commander = cf.commander
    start = waypoints[0]

    try:
        print("[INFO] Taking off...")
        commander.send_hover_setpoint(0, 0, 0, FLIGHT_HEIGHT)
        time.sleep(2)

        for i, wp in enumerate(waypoints):
            x, y, z = wp[:3]
            commander.send_position_setpoint(x, y, z, 0)
            print(f"[INFO] Flying to waypoint {i+1}: ({x:.2f}, {y:.2f}, {z:.2f})")
            time.sleep(1.5)

        if RETURN_HOME:
            print("[INFO] Returning to home...")
            x, y, z = start
            commander.send_position_setpoint(x, y, z, 0)
            time.sleep(2)

        print("[INFO] Landing...")
        commander.send_hover_setpoint(0, 0, 0, 0)
        time.sleep(2)

    finally:
        cf.close_link()
        print("[INFO] Mission complete.")
