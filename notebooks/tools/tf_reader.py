import os
import argparse
import rtde_receive
import rtde_control
import time
import websockets
import json
import csv
import asyncio
import datetime
import os
import time
import json
import socket

#
#
# START EDIT PARAMETERS
#
#

ENABLE_WS = True # Enable WebSocket server. Disable if not using websocket. Script will crash otherwise.
SAMPLE_FREQUENCY = 500 # Sample frequency in Hz

#
#
# END EDIT PARAMETERS
#
#

def read_and_publish_tf_sensor_sync(rtde_r, name, que):
    t0 = time.time()

    # Define the UDP server address and port
    udp_server_address = ('localhost', 9870)

    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with open( os.path.join(os.path.dirname(os.path.realpath(__file__)), f'../../data/raw/TF/table_calibration/{name}.csv'), 'w', newline='') as csvfile:
        
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["t_wall [s]", "t_robot [s]", "F_x [N]", "F_y [N]", "F_z [N]", "T_x [Nm]", "T_y [Nm]", "T_z [Nm]", "X [m]", "Y [m]", "Z [m]", "R_x [Nm]", "R_y [Nm]", "R_z [Nm]"])  # Header row
    
        while que.empty(): 

            x, y, z, rx, ry, rz = rtde_r.getActualTCPPose()
            fx, fy, fz, tx, ty, tz = rtde_r.getActualTCPForce()
            t = rtde_r.getTimestamp()

            t0 = time.time()        

            # Construct data dictionary
            data = {
                "t_wall": t0,
                "t_robot": t,
                "F_x": fx,
                "F_y": fy,
                "F_z": fz,
                "T_x": tx,
                "T_y": ty,
                "T_z": tz,
                "x": x,
                "y": y,
                "z": z,
                "rx": rx,
                "ry": ry,
                "rz": rz
            }
            
            csv_writer.writerow([t0, t, fx, fy, fz, tx, ty, tz, x, y, z, rx, ry, rz]) 

            # Convert data dictionary to JSON string
            json_data = json.dumps(data)

            # Send JSON data to the UDP server
            udp_socket.sendto(json_data.encode(), udp_server_address)

            time.sleep(1 / SAMPLE_FREQUENCY)

    # Close the UDP socket when done
    udp_socket.close()
