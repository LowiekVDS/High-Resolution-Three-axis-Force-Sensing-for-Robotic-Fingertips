# Master thesis

# How to use

## Calibrating a 2x2 sensor

### Preqrequisites

- Upload firmware `sensor-readout` to sensor
- Configure robot
- Mount sensor on robot

### Capture raw data per taxel

Do this procedure per taxel, giving each file a different name:

- Run the python read file `scripts/together/read.py`
- Make random movements on the taxel 
- Stop. The data will be stored in `data/raw`.

### Model creation

The `notebooks/model_creation.ipynb` notebook allows someone to convert the data to an actual model that converts readings to forces per taxel. Be sure to replace `NAME_PREFIX` with a lambda (or an actual function) that returns the name of the data file for the given taxel `i`. 

- Run the notebook (only the section of the model type you want of course). The result will be stored based on the name you gave it in the parameter section under the respective folder in `models/..`.

Done!

## Running the sensor in realtime

First be sure to select the correct model in `scripts/2x2_sensor/process.py`.

Then you have two choices:

- If you only want the sensor converted results: run `scripts/2x2_sensor/process.py`
- If you want both the sensor converted values and the ground truth (based on the force torque sensor used for calibration): run `scripts/together/process.py`.

Both scripts will write out data to a csv file under `data/..` again and/or send data to a websocket. 



