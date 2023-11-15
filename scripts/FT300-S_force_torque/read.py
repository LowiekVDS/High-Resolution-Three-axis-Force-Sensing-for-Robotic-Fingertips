import rtde_receive
import time
import websockets
import json
import csv
import asyncio

ROBOT_HOST = "10.42.0.162"
ENABLE_WS = True
ZERO_SENSOR_ON_START = False

# Connect to the RTDE robot
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_HOST)

t0 = time.time()

# Define the WebSocket server URL
websocket_server_url = "ws://localhost:9871"

# Send data to the WebSocket server for visualization in PlotJuggler
async def send_data_to_websocket(data):
    async with websockets.connect(websocket_server_url) as websocket:
        await websocket.send(json.dumps(data))


with open('data.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["t", "F_x", "F_y", "F_z", "T_x", "T_y", "T_z"])  # Header row
    
    if ZERO_SENSOR_ON_START:
        rtde_r.zeroFtSensor()

    while True:
        data = rtde_r.getActualTCPPose()
        
        fx, fy, fz, tx, ty, tz = rtde_r.getActualTCPForce()
        t = time.time()
        
        csv_writer.writerow([t, fx, fy, fz, tx, ty, tz]) 
        
        if ENABLE_WS:
            asyncio.get_event_loop().run_until_complete(send_data_to_websocket([t, fx, fy, fz, tx, ty, tz]))