#include "SensorArray.h"

SensorArray sensorArray;

int16_t x[4], y[4], z[4];

void setup(void)
{

  // Set up serial communication
  Serial.begin(115200);

  /* Wait for serial on USB platforms. */
  while (!Serial)
  {
    delay(10);
  }

  // Setup sensor array
  bool success = true;
  success |= sensorArray.addSensor(0x0C);
  success |= sensorArray.addSensor(0x0D);
  success |= sensorArray.addSensor(0x0E);
  success |= sensorArray.addSensor(0x0F);

  if (!success)
  {
    Serial.println("[FATAL]> Something went wrong while configuring the sensors...");
    while (1)
    {
      delay(10);
    }
  }

  // Configure sensor array
  for (int i = 0; i < sensorArray.getNumberOfSensors(); i++)
  {

    auto sensor = sensorArray.getSensor(i);

    // Set gain
    sensor->setGain(MLX90393_GAIN_2_5X);

    // Set resolution, per axis
    sensor->setResolution(MLX90393_X, MLX90393_RES_19);
    sensor->setResolution(MLX90393_Y, MLX90393_RES_19);
    sensor->setResolution(MLX90393_Z, MLX90393_RES_19);

    // Set oversampling
    sensor->setOversampling(MLX90393_OSR_2);

    // Enable temperature compensation
    sensor->setTemperatureCompensation(true);

    // Set digital filtering
    sensor->setFilter(MLX90393_FILTER_6);
  }
}

void loop(void)
{
  
}