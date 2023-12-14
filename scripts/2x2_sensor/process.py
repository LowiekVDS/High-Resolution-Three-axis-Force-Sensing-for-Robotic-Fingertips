import pickle
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


ARRAY_SIZE = 4
MODEL_PREFIX = "H1_5"

models = []

# Load the models

for i in range(ARRAY_SIZE):
  
  model_F_x = pickle.load(open(f'models/{MODEL_PREFIX}_sensor{i}/F_x', 'rb'))
  model_F_y = pickle.load(open(f'models/{MODEL_PREFIX}_sensor{i}/F_y', 'rb'))
  model_F_z = pickle.load(open(f'models/{MODEL_PREFIX}_sensor{i}/F_z', 'rb'))
  
  models.append([model_F_x, model_F_y, model_F_z])


GAIN = 3
RESOLUTION = 3
BAUD = 115200
COM = '/dev/ttyACM0'
ENABLE_WS = True

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
                x = (data_bytes[i * 3 * 2] << 8) + data_bytes[i * 3 * 2 + 1] - 16384
                y = (data_bytes[i * 3 * 2 + 2] << 8) + data_bytes[i * 3 * 2 + 3] - 16384
                z = (data_bytes[i * 3 * 2 + 4] << 8) + data_bytes[i * 3 * 2 + 5] - 16384

                x *= mlx90393_lsb_lookup[0][GAIN][RESOLUTION][0]
                y *= mlx90393_lsb_lookup[0][GAIN][RESOLUTION][0]
                z *= mlx90393_lsb_lookup[0][GAIN][RESOLUTION][1]

                row[f"X{i}"] = x
                row[f"Y{i}"] = y
                row[f"Z{i}"] = z
                
                row[f"sens{i}_magnitude"] = np.sqrt(x**2 + y**2 + z**2)
                row[f"sens{i}_magnitude_XY"] = np.sqrt(x**2 + y**2)
              
            # Predict the force
            for i in range(ARRAY_SIZE):
              for j, letter in enumerate(['x', 'y', 'z']):
                row[f'F_{letter}{i}'] = models[i][j].predict(np.array([row[f'X{i}'], row[f'Y{i}'], row[f'Z{i}'], row[f'sens{i}_magnitude'], row[f'sens{i}_magnitude_XY']]).reshape(1, -1))[0]



                # print(f"Sensor {i}, x: {x} uT, y: {y} uT, z: {z} uT")

            csv_writer.writerow([row["t"], row["X0"], row["Y0"], row["Z0"], row["X1"], row["Y1"], row["Z1"],
                                    row["X2"], row["Y2"], row["Z2"], row["X3"], row["Y3"], row["Z3"]]) #,  row[f'F_x0'], row[f'F_y0'], row[f'F_z0'], row[f'F_x1'], row[f'F_y1'], row[f'F_z1'], row[f'F_x2'], row[f'F_y2'], row[f'F_z2'], row[f'F_x3'], row[f'F_y3'], row[f'F_z3']])

            # Send data to WebSocket as JSON
            if ENABLE_WS:
                asyncio.get_event_loop().run_until_complete(send_data_to_websocket(row))