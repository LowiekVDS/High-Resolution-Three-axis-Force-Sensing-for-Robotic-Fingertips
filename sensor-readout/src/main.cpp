#include "SensorArray.h"
#include <math.h>
#include <avr/wdt.h>

// EDITABLE

// #define DEBUG 1

#define BAUD_RATE 115200
#define MLX_OSR MLX90393_OSR_2
#define MLX_DIG_FILT MLX90393_FILTER_1
#define START_BYTE 0xAA
#define MUX_ADDR 0x77
#define USE_MUX 1

#define HEADER_SIZE 1
#define TAIL_SIZE 0
#define SUBFRAME_SIZE 6
#define I2C_SPEED 400000 // in kHz
#define EXTRA_DELAY 5000

// Readout is done in this order.
// Done so that a mapping can be made between different physical and logical layouts
// Can also be used to have different readout strategies

#define NR_OF_SENSORS 8*4

// Left to right
uint8_t addressing_left_to_right[NR_OF_SENSORS] =
    {
        0x3C, 0x3D, 0x3E, 0x3F,
        0x4C, 0x4D, 0x4E, 0x4F,
        0x2C, 0x2D, 0x2E, 0x2F,
        0x1C, 0x1D, 0x1E, 0x1F,
        0x0C, 0x0D, 0x0E, 0x0F,
        0x5C, 0x5D, 0x5E, 0x5F,
        0x6C, 0x6D, 0x6E, 0x6F,
        0x7C, 0x7D, 0x7E, 0x7F,
};
// Striped
uint8_t addressing_striped[NR_OF_SENSORS] =
    {
      0x3C, 0x3D, 0x3E, 0x3F,
      0x2C, 0x2D, 0x2E, 0x2F,
      0x0C, 0x0D, 0x0E, 0x0F,
      0x6C, 0x6D, 0x6E, 0x6F,
      0x4C, 0x4D, 0x4E, 0x4F,
      0x1C, 0x1D, 0x1E, 0x1F,
      0x5C, 0x5D, 0x5E, 0x5F,
      0x7C, 0x7D, 0x7E, 0x7F,
};

//! Choose mapping here
uint8_t *sensor_addresses = addressing_left_to_right;

// END EDITABLE

Adafruit_MLX90393 sensors[NR_OF_SENSORS];
SensorArray sensorArray(I2C_SPEED, sensors, MUX_ADDR);

uint16_t x[NR_OF_SENSORS], y[NR_OF_SENSORS], z[NR_OF_SENSORS];

long conversion_time_us, comm_time_us, idle_time_us = 0;

uint8_t id = 0;
bool started = false;

void reboot()
{
  Serial.println("[FATAL]> Rebooting");
  Serial.flush();
  wdt_disable();
  wdt_enable(WDTO_15MS);
  while (1)
  {
  }
}

void setup()
{
  // Set up serial communication
  Serial.begin(BAUD_RATE);
  Wire.begin();
  Wire.setClock(I2C_SPEED);

  /* Wait for serial on USB platforms. */
  while (!Serial)
  {
    delay(10);
  }

  delay(2000);

  // Setup sensor array
  bool success = sensorArray.addSensors(sensor_addresses, NR_OF_SENSORS);

  if (!success)
  {
    // Note: why doesn't Serial have a printf :(
    Serial.print("[FATAL]> Something went wrong while adding sensors");

    delay(5000);

    // Reset
    reboot();
  }

  for (int i = 0; i < sensorArray.getNumberOfSensors(); i++)
  {

    auto sensor = sensorArray.getSensor(i);

    // Set gain and resolution

    sensor->setGain(MLX90393_GAIN_1X);
    sensor->setResolution(MLX90393_X, MLX90393_RES_16);
    sensor->setResolution(MLX90393_Y, MLX90393_RES_16);
    sensor->setResolution(MLX90393_Z, MLX90393_RES_16);

    // Set oversampling
    sensor->setOversampling(MLX_OSR);

    // Enable temperature compensation
    sensor->setTemperatureCompensation(false);

    // Set digital filtering
    sensor->setFilter(MLX_DIG_FILT);
  }

  // Calculate the different timings
  conversion_time_us = ceil(1000 * (0.5 + 3 * 0.063 * pow(2.0, MLX_OSR) * (2 + pow(2.0, MLX_DIG_FILT)) + 1)); // + 1 for good measure
  comm_time_us = 8 * 1000000 * (HEADER_SIZE + TAIL_SIZE + NR_OF_SENSORS * SUBFRAME_SIZE) / BAUD_RATE;
  idle_time_us = conversion_time_us - (NR_OF_SENSORS - 1) * 40000000 / I2C_SPEED - comm_time_us;

  if (idle_time_us < 0)
  {
    Serial.println("[WARNING]> Idle wait time is negative, which means the system is underutilized or constrained by Serial speed. Please reconfigure");
    idle_time_us = 0.0;
  }

  idle_time_us += EXTRA_DELAY;
}

void loop()
{
  // Read loop. First step is to start measurements
  for (uint8_t i = 0; i < sensorArray.getNumberOfSensors(); i++)
  {
    if (!sensorArray.getSensor(i)->startSingleMeasurement())
    {
      Serial.println("[WARNING]> Sensor measurement failed");
    }
  }

  // Now send previous data
  if (started)
  {

#ifndef DEBUG
    Serial.write(START_BYTE);

    for (uint8_t i = 0; i < NR_OF_SENSORS; i++)
    {
      Serial.write((x[i] >> 8) & 0xFF);
      Serial.write(x[i] & 0xFF);

      Serial.write((y[i] >> 8) & 0xFF);
      Serial.write(y[i] & 0xFF);

      Serial.write((z[i] >> 8) & 0xFF);
      Serial.write(z[i] & 0xFF);
    }
#endif
  }
  else
  {
    delayMicroseconds(comm_time_us);
  }

  delayMicroseconds(idle_time_us);

  // Read measurements data
  for (uint8_t i = 0; i < sensorArray.getNumberOfSensors(); i++)
  {

#ifndef DEBUG
    if (!sensorArray.getSensor(i)->readRawMeasurement(x + i, y + i, z + i))
    {
      Serial.print("Something went wrong in sensor ");
      Serial.println(i);
    }
#else
    float x, y, z;
    if (!sensorArray.getSensor(i)->readMeasurement(&x, &y, &z))
    {
      Serial.println("ERROR");
      continue;
    }
    Serial.print("S");
    Serial.print(i);
    Serial.print(" ( ");
    Serial.print(x);
    Serial.print(" ; ");
    Serial.print(y);
    Serial.print(" ; ");
    Serial.print(z);
    Serial.print(" ) \n");

#endif
  }

  started = true;
  id++;
}