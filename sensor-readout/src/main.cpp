#include "SensorArray.h"
#include <math.h>

// #define DEBUG

#define NR_OF_SENSORS 4
#define BAUD_RATE 115200
#define MLX_OSR MLX90393_OSR_2
#define MLX_DIG_FILT MLX90393_FILTER_1
#define START_BYTE 0xAA

#define HEADER_SIZE 1
#define TAIL_SIZE 0
#define SUBFRAME_SIZE 6
#define I2C_SPEED 400000 // in kHz
#define EXTRA_DELAY 0


SensorArray sensorArray(I2C_SPEED);

uint16_t x[NR_OF_SENSORS], y[NR_OF_SENSORS], z[NR_OF_SENSORS];

long conversion_time_us, comm_time_us, idle_time_us = 0;

uint8_t id = 0;
bool started = false;

void setup(void)
{

  // Set up serial communication
  Serial.begin(BAUD_RATE);

  /* Wait for serial on USB platforms. */
  while (!Serial)
  {
    delay(10);
  }

  // Setup sensor array
  bool success = true;
  success &= sensorArray.addSensor(0x0C);
  success &= sensorArray.addSensor(0x0D);
  success &= sensorArray.addSensor(0x0E);
  success &= sensorArray.addSensor(0x0F);

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
    // For 1.5 and 2 mm
    sensor->setGain(MLX90393_GAIN_1X);

    // For 1mm
    // sensor->setGain(MLX90393_GAIN_1_33X);

    // Set resolution, per axis

    // For 1mm and 1.5mm
    sensor->setResolution(MLX90393_X, MLX90393_RES_16);
    sensor->setResolution(MLX90393_Y, MLX90393_RES_16);
    sensor->setResolution(MLX90393_Z, MLX90393_RES_16);


    // // For 2mm
    // sensor->setResolution(MLX90393_X, MLX90393_RES_19);
    // sensor->setResolution(MLX90393_Y, MLX90393_RES_19);
    // sensor->setResolution(MLX90393_Z, MLX90393_RES_19);

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

  if (idle_time_us < 0) {
    Serial.println("[WARNING]> Idle wait time is negative, which means the system is underutilized or constrained by Serial speed. Please reconfigure");
    idle_time_us = 0.0;
  }  

  idle_time_us += EXTRA_DELAY;

  // Read sensors once, then print value

  for (int i = 0; i < sensorArray.getNumberOfSensors(); i++)
  {
    if (!sensorArray.getSensor(i)->startSingleMeasurement())
    {
      Serial.println("[WARNING]> Sensor measurement failed");
    }
  }

  delay(100);

  // for (uint i = 0; i < sensorArray.getNumberOfSensors(); i++)
  // {
  //   uint16_t x, y, z;
  //   if (!sensorArray.getSensor(i)->readRawMeasurement(&x, &y, &z)) {
  //     Serial.println("ERROR");
  //   }
    
  //   if (!sensorArray.getSensor(i)->setConstantOffset(MLX90393_X, x - 32768)) {
  //     Serial.println("ERROR");
  //     while (1) {}
  //   }
  //   if (!sensorArray.getSensor(i)->setConstantOffset(MLX90393_Y, y - 32768)) {
  //     Serial.println("ERROR");
  //     while (1) {}
  //   }
  //   if (!sensorArray.getSensor(i)->setConstantOffset(MLX90393_Z, z - 32768)) {
  //     Serial.println("ERROR");
  //     while (1) {}
  //   }
  //   // sensorArray.getSensor(i)->setConstantOffset(MLX90393_Y, 32768 - y);
  //   // sensorArray.getSensor(i)->setConstantOffset(MLX90393_Z, 32768 - z);
  // }

  // while (1){}
}

void loop(void)
{

  // Read loop. First step is to start measurements
  for (uint i = 0; i < sensorArray.getNumberOfSensors(); i++) {
    if (!sensorArray.getSensor(i)->startSingleMeasurement()) {
      Serial.println("[WARNING]> Sensor measurement failed");
    }
  }

  // Now send previous data
  if (started) {

#ifndef DEBUG    
    Serial.write(START_BYTE);

    for (uint i = 0; i < NR_OF_SENSORS; i++) {
      Serial.write((x[i] >> 8) & 0xFF);
      Serial.write(x[i] & 0xFF);

      Serial.write((y[i] >> 8) & 0xFF);
      Serial.write(y[i] & 0xFF);

      Serial.write((z[i] >> 8) & 0xFF);
      Serial.write(z[i] & 0xFF);
    }
#endif

  } else {
    delayMicroseconds(comm_time_us);
  }

  delayMicroseconds(idle_time_us);

  // Read measurements data
  for (uint i = 0; i < sensorArray.getNumberOfSensors(); i++) {

#ifndef DEBUG
    if (!sensorArray.getSensor(i)->readRawMeasurement( x + i, y + i, z + i)) {
      Serial.print("Something went wrong in sensor ");
      Serial.println(i);
    }
#else
    float x, y, z;
    if (!sensorArray.getSensor(i)->readMeasurement(&x, &y, &z)) {
      Serial.println("ERROR");
    }
    Serial.print("Sensor ");
    Serial.print(i);
    Serial.print(" x: ");
    Serial.print(x);
    Serial.print(" y: ");
    Serial.print(y);
    Serial.print(" z: ");
    Serial.println(z);
#endif
  }

  started = true;
  id++;
}