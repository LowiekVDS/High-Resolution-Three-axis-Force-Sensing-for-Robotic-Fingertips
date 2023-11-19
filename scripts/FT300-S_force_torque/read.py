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

ROBOT_HOST = "10.42.0.162"
ENABLE_WS = True
ZERO_SENSOR_ON_START = True
SAMPLE_FREQUENCY = 500

parser = argparse.ArgumentParser(description='Read FT300 force torque sensor data and save it to a CSV file.')
parser.add_argument('name', type=str, help='name of the capture file')
args = parser.parse_args()

# Connect to the RTDE robot
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_HOST)
rtde_c = rtde_control.RTDEControlInterface(ROBOT_HOST)

t0 = time.time()

# Define the WebSocket server URL
websocket_server_url = "ws://localhost:9871"

# Send data to the WebSocket server for visualization in PlotJuggler
async def send_data_to_websocket(data):
    async with websockets.connect(websocket_server_url) as websocket:
        await websocket.send(json.dumps(data))


now = datetime.datetime.now()
timestamp_str = now.strftime("%Y%m%d_%H%M%S")

started = False

with open( os.path.join(os.path.dirname(os.path.realpath(__file__)), f'data/{args.name}_{timestamp_str}.csv'), 'w', newline='') as csvfile:        
        
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["t_wall [s]", "t_robot [s]", "F_x [N]", "F_y [N]", "F_z [N]", "T_x [Nm]", "T_y [Nm]", "T_z [Nm]"])  # Header row
    
    if ZERO_SENSOR_ON_START:
        rtde_c.zeroFtSensor()

    while True:
        data = rtde_r.getActualTCPPose()
            
        fx, fy, fz, tx, ty, tz = rtde_r.getActualTCPForce()
        t = rtde_r.getTimestamp()
    
        t0 = time.time()        
        
        csv_writer.writerow([t0, t, fx, fy, fz, tx, ty, tz]) 
        
        if ENABLE_WS:
            asyncio.get_event_loop().run_until_complete(send_data_to_websocket({
                "t_wall": t0,
                "t_robot": t,
                "F_x": fx,
                "F_y": fy,
                "F_z": fz,
                "T_x": tx,
                "T_y": ty,
                "T_z": tz
            }))
            
        time.sleep(1 / SAMPLE_FREQUENCY)