import pickle
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn
from sklearn import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import serial
from mlx import mlx90393_lsb_lookup
import csv
import time
import json
import asyncio
import websockets
import datetime
import os
import argparse
import dill

#
#
# START EDIT PARAMETERS
#
#

ARRAY_SIZE = 4 # Number of sensors in the array
MODEL_NAME = "H1_5-2x2-005" # Name of the model to load for processing
WINDOW_SIZE = 100 # Number of samples to collect before starting to predict
SCALE_FACTOR = 1000 # Scale factor for the input data

GAIN = 4 # Gain setting (same as firmware)
RESOLUTION = 0 # Resolution setting (same as firmware)
BAUD = 115200 # Baud rate
COM = '/dev/ttyACM0' # Serial port
ENABLE_WS = True # Enable WebSocket server. Disable if not using websocket. Script will crash otherwise.

#
#
# END EDIT PARAMETERS
#
#

# Load the models
taxel_models = dill.load(open(os.path.join(os.getcwd(), f'../../models/PolyLinear-Deg4/{MODEL_NAME}'), 'rb'))
means_tmp = np.zeros((WINDOW_SIZE, ARRAY_SIZE, 3))
means = np.zeros((ARRAY_SIZE, 3))

ser = serial.Serial(COM, BAUD) 
t0 = time.time()

# Define the WebSocket server URL
websocket_server_url = "ws://localhost:9871"

parser = argparse.ArgumentParser(description='Read FT300 force torque sensor data and save it to a CSV file.')
parser.add_argument('name', type=str, help='name of the capture file')
args = parser.parse_args()

async def send_data_to_websocket(data):
    async with websockets.connect(websocket_server_url) as websocket:
        await websocket.send(json.dumps(data))

now = datetime.datetime.now()
timestamp_str = now.strftime("%Y%m%d_%H%M%S")

print("Starting calibration... PLEASE DO NOT TOUCH SENSOR ARRAY!")

path = os.path.join(os.path.dirname(os.path.realpath(__file__)), f'data/{args.name}.csv').split('/')[:-1]

if not os.path.exists('/'.join(path)):
    os.makedirs('/'.join(path))

k = 0
with open( os.path.join(os.path.dirname(os.path.realpath(__file__)), f'data/{args.name}.csv'), 'w', newline='') as csvfile:    
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["t_wall [s]", "X0 [uT]", "Y0 [uT]", "Z0 [uT]", "X1 [uT]", "Y1 [uT]", "Z1 [uT]", "X2 [uT]", "Y2 [uT]", "Z2 [uT]", "X3 [uT]", "Y3 [uT]", "Z3 [uT]"])  # Header row

    while True:
        data = ser.read(1)
        if data == b'\xAA':
            data_bytes = ser.read(6 * 4)
            row = {"t": time.time()}

            # print(f"Rate: {1 / (time.time() - t0)}Hz")

            t0 = time.time()

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
                
                # First collect {WINDOW_SIZE} samples while idle                    
                if k < WINDOW_SIZE:
                    means_tmp[k, i] = [x, y, z]
                    
                    row[f'F_x{i}'] = 0
                    row[f'F_y{i}'] = 0
                    row[f'F_z{i}'] = 0    
                    
                else:
                    # Predict the force
                    X = (np.array([row[f'X{i}'], row[f'Y{i}'], row[f'Z{i}']]) - means[i]) / SCALE_FACTOR
                    Y = taxel_models[i].predict(X.reshape(1, -1))
                    
                    row[f'F_x{i}'] = Y[0, 0]
                    row[f'F_y{i}'] = Y[0, 1]
                    row[f'F_z{i}'] = Y[0, 2]                      

            k += 1
            
            if k == WINDOW_SIZE:
                for i in range(4):
                    means[i, 0] = np.mean(means_tmp[:, i, 0])
                    means[i, 1] = np.mean(means_tmp[:, i, 1])
                    means[i, 2] = np.mean(means_tmp[:, i, 2])

                    row[f'F_x{i}'] = 0
                    row[f'F_y{i}'] = 0
                    row[f'F_z{i}'] = 0   
                    
                print("Calibration done! You can now touch the sensor array.")
                print("Mean values are: ", means)

            csv_writer.writerow([row["t"], row["X0"], row["Y0"], row["Z0"], row["X1"], row["Y1"], row["Z1"],
                                    row["X2"], row["Y2"], row["Z2"], row["X3"], row["Y3"], row["Z3"],  row[f'F_x0'], row[f'F_y0'], row[f'F_z0'], row[f'F_x1'], row[f'F_y1'], row[f'F_z1'], row[f'F_x2'], row[f'F_y2'], row[f'F_z2'], row[f'F_x3'], row[f'F_y3'], row[f'F_z3']])

            # Send data to WebSocket as JSON
            if ENABLE_WS:
                asyncio.get_event_loop().run_until_complete(send_data_to_websocket(row))