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
import serial
from .mlx import *

#
#
# START EDIT PARAMETERS
#
#

GAIN = 7 # Gain setting (same as firmware)
RESOLUTION = 0 # Resolution setting (same as firmware)
BAUD = 115200 # Baud rate
COM = '/dev/ttyACM0' # Serial port
ENABLE_WS = True # Enable WebSocket server. Disable if not using websocket. Script will crash otherwise.

#
#
# END EDIT PARAMETERS
#
#

ser = serial.Serial(COM, BAUD) 

def read_and_publish_sensor_sync(name, que):

    # Define the UDP server address and port
    udp_server_address = ('localhost', 9870)

    # Create a UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with open( os.path.join(os.path.dirname(os.path.realpath(__file__)), f'../../data/raw/sensor/table_calibration/{name}.csv'), 'w', newline='') as csvfile:

        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["t_wall [s]", "X0 [uT]", "Y0 [uT]", "Z0 [uT]", "X1 [uT]", "Y1 [uT]", "Z1 [uT]", "X2 [uT]", "Y2 [uT]", "Z2 [uT]", "X3 [uT]", "Y3 [uT]", "Z3 [uT]"])  # Header row
        
        while que.empty():
            data = ser.read(1)
            if data == b'\xAA':
                data_bytes = ser.read(6 * 4)
                row = {"t": time.time()}

                for i in range(4):
                    x = (data_bytes[i * 3 * 2] << 8) + data_bytes[i * 3 * 2 + 1] - 32768
                    y = (data_bytes[i * 3 * 2 + 2] << 8) + data_bytes[i * 3 * 2 + 3] - 32768
                    z = (data_bytes[i * 3 * 2 + 4] << 8) + data_bytes[i * 3 * 2 + 5] - 32768

                    x *= mlx90393_lsb_lookup[0][GAIN][RESOLUTION][0] 
                    y *= mlx90393_lsb_lookup[0][GAIN][RESOLUTION][0] 
                    z *= mlx90393_lsb_lookup[0][GAIN][RESOLUTION][1] 

                    row[f"X{i}"] = x
                    row[f"Y{i}"] = y
                    row[f"Z{i}"] = z
                    
                csv_writer.writerow([row["t"], row["X0"], row["Y0"], row["Z0"], row["X1"], row["Y1"], row["Z1"],
                                    row["X2"], row["Y2"], row["Z2"], row["X3"], row["Y3"], row["Z3"]])
                
                json_data = json.dumps(row)
                udp_socket.sendto(json_data.encode(), udp_server_address)                

        udp_socket.close()
