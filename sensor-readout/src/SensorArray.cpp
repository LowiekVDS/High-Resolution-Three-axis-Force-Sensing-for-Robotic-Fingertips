#include "SensorArray.h"

bool SensorArray::readData(int16_t *x, int16_t *y, int16_t *z) {

  // First start all measurements
  for (int i = 0; i < this->numSensors; i++) {
    if (!this->sensors[i].startSingleMeasurement())
      return false;
  }

  // Delay (assume same conversion time for all sensors)
  this->sensors[0].waitForConversion();

  // Now get data
  for (int i = 0; i < this->numSensors; i++) {
    if (!this->sensors[i].readRawMeasurement(x + i, y + i, z + i))
      return false;
  }

  return true;
}

bool SensorArray::addSensor(uint8_t address) {
    Adafruit_MLX90393* newSensors = new Adafruit_MLX90393[numSensors + 1];
    float* newSensorData = new float[numSensors + 1];

    // Copy existing sensors and data
    for (int i = 0; i < numSensors; i++) {
        newSensors[i] = sensors[i];
        newSensorData[i] = sensorData[i];
    }

    // Add the new sensor
    newSensors[numSensors] = Adafruit_MLX90393();
    if (newSensors[numSensors].begin_I2C(address, this->speed)) {
        sensors = newSensors;
        sensorData = newSensorData;
        numSensors++;
        return true;
    } else {
        // Failed to initialize the new sensor
        delete[] newSensors;
        delete[] newSensorData;
        return false;
    }
}
