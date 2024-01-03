import subprocess
import argparse
import os 
import subprocess
import os 
import argparse

""" 
This script runs the read scripts from the FT300-S force torque sensor and the process script from the 2x2.
"""

parser = argparse.ArgumentParser(description='Read FT300 force torque sensor data and save it to a CSV file.')
parser.add_argument('name', type=str, help='name of the capture file')
args = parser.parse_args()

name = args.name

# Run first Python process
p1 = subprocess.Popen(["python", os.path.join(os.path.dirname(os.path.realpath(__file__)), "../2x2_sensor/process.py"), name])

# Run second Python process
p2 = subprocess.Popen(["python", os.path.join(os.path.dirname(os.path.realpath(__file__)), "../FT300-S_force_torque/read.py"), name])

# Wait for both processes to finish
p1.wait()
p2.wait()
