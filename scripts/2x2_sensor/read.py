import serial
from mlx import mlx90393_lsb_lookup
import csv
import time
import json
import asyncio
import websockets

GAIN = 3
RESOLUTION = 3
BAUD = 115200
COM = '/dev/ttyACM0'
ENABLE_WS = True

ser = serial.Serial(COM, BAUD) 
t0 = time.time()

# Define the WebSocket server URL
websocket_server_url = "ws://localhost:9871"

async def send_data_to_websocket(data):
    async with websockets.connect(websocket_server_url) as websocket:
        await websocket.send(json.dumps(data))

with open('data.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["t", "X0", "Y0", "Z0", "X1", "Y1", "Z1", "X2", "Y2", "Z2", "X3", "Y3", "Z3"])  # Header row

    while True:
        data = ser.read(1)
        if data == b'\xAA':
            data_bytes = ser.read(6 * 4)
            row = {"t": time.time()}

            print(f"Rate: {1 / (time.time() - t0)}Hz")

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

                print(f"Sensor {i}, x: {x} uT, y: {y} uT, z: {z} uT")

            csv_writer.writerow([row["t"], row["X0"], row["Y0"], row["Z0"], row["X1"], row["Y1"], row["Z1"],
                                    row["X2"], row["Y2"], row["Z2"], row["X3"], row["Y3"], row["Z3"]])

            # Send data to WebSocket as JSON
            if ENABLE_WS:
                asyncio.get_event_loop().run_until_complete(send_data_to_websocket(row))