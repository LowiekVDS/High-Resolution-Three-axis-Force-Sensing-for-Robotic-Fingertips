import subprocess
import os 
import subprocess
import os 

name = input("Enter a name: ")

# Run first Python process
p1 = subprocess.Popen(["python", os.path.join(os.path.dirname(os.path.realpath(__file__)), "../2x2_sensor/read.py"), name])

# Run second Python process
p2 = subprocess.Popen(["python", os.path.join(os.path.dirname(os.path.realpath(__file__)), "../FT300-S_force_torque/read.py"), name])

# Wait for both processes to finish
p1.wait()
p2.wait()
