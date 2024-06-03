#include "SensorArray.h"
#include <math.h>
#include <Wire.h>
#include "taxels.h"

// EDITABLE

// #define DEBUG 1

#define SEND_FORCE_PREDICTIONS true
#define ENABLE_STAGE_II true

#define BAUD_RATE 400000
#define MLX_OSR MLX90393_OSR_2
#define MLX_DIG_FILT MLX90393_FILTER_1
#define START_BYTE 0xAA
#define MUX_ADDR 0x77
#define USE_MUX 1

#define HEADER_SIZE 1
#define TAIL_SIZE 0
#define SUBFRAME_SIZE 6
#define I2C_SPEED 400000 // in kHz
#define EXTRA_DELAY 0
#define ANGLE 1.6025613
#define DEBIAS_WINDOW 100

// Readout is done in this order.
// Done so that a mapping can be made between different physical and logical layouts
// Can also be used to have different readout strategies

#define NR_OF_SENSORS 8 * 4

// Left to right
uint8_t addressing_left_to_right[NR_OF_SENSORS] =
    {

        0x3C,
        0x3D,
        0x3E,
        0x3F,
        0x4C,
        0x4D,
        0x4E,
        0x4F,
        0x2C,
        0x2D,
        0x2E,
        0x2F,
        0x1C,
        0x1D,
        0x1E,
        0x1F,
        0x0C,
        0x0D,
        0x0E,
        0x0F,
        0x5C,
        0x5D,
        0x5E,
        0x5F,
        0x6C,
        0x6D,
        0x6E,
        0x6F,
        0x7C,
        0x7D,
        0x7E,
        0x7F,
};

//! Choose mapping here
uint8_t *sensor_addresses = addressing_left_to_right;

// END EDITABLE

Adafruit_MLX90393 sensors[NR_OF_SENSORS];
SensorArray sensorArray(I2C_SPEED, sensors, MUX_ADDR);

uint16_t x[NR_OF_SENSORS], y[NR_OF_SENSORS], z[NR_OF_SENSORS];
float prev_x[NR_OF_SENSORS], prev_y[NR_OF_SENSORS], prev_z[NR_OF_SENSORS];
int x_cycle[NR_OF_SENSORS], y_cycle[NR_OF_SENSORS], z_cycle[NR_OF_SENSORS];
float x_bias[NR_OF_SENSORS], y_bias[NR_OF_SENSORS], z_bias[NR_OF_SENSORS];

long conversion_time_us, comm_time_us, idle_time_us = 0;

uint8_t id = 0;
bool started = false;

bool is_first = true;

uint8_t debiasing_counter = 0;

void setup()
{
    Wire.begin();

    // Set up serial communication
    Serial.begin(BAUD_RATE);

    /* Wait for serial on USB platforms. */
    while (!Serial)
    {
        delay(10);
    }

    // Setup sensor array
    bool success = sensorArray.addSensors(sensor_addresses, NR_OF_SENSORS);

    if (!success)
    {
        // Note: why doesn't Serial have a printf :(
        Serial.print("[FATAL]> Something went wrong while adding sensors");

        while (1)
            ;
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
        sensor->setTemperatureCompensation(true);

        // Set digital filtering
        sensor->setFilter(MLX_DIG_FILT);
    }

    // Calculate the different timings
    conversion_time_us = ceil(1000 * (0.5 + 3 * 0.063 * pow(2.0, MLX_OSR) * (2 + pow(2.0, MLX_DIG_FILT)) + 1)); // + 1 for good measure
    comm_time_us = 8 * 1000000 * (HEADER_SIZE + TAIL_SIZE + NR_OF_SENSORS * SUBFRAME_SIZE) / BAUD_RATE;
    idle_time_us = conversion_time_us - NR_OF_SENSORS * 40000000 / I2C_SPEED - comm_time_us;

    Serial.println("Conversion time: " + String(conversion_time_us) + " us");
    Serial.println("Communication time: " + String(comm_time_us) + " us");
    Serial.println("Idle time: " + String(idle_time_us) + " us");

    if (idle_time_us < 0)
    {
        Serial.println("[WARNING]> Idle wait time is negative, which means the system is underutilized or constrained by Serial speed. Please reconfigure");
        idle_time_us = 0.0;
    }

    idle_time_us += EXTRA_DELAY;
}

uint16_t convert(float fval, float min, float max)
{
    if (fval < min)
        return (0);
    if (fval > max)
        return (UINT16_MAX);
    return (lrintf((fval - min) / (max - min) * UINT16_MAX));
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

        if (!SEND_FORCE_PREDICTIONS)
        {
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
        }
        else
        {

            float feature_input_stage_II[3 * NR_OF_SENSORS];

            for (uint8_t i = 0; i < NR_OF_SENSORS; i++)
            {

                // Conversion based on sensor settings (to uT)
                float x_f = ~x[i];
                float y_f = ~y[i];
                float z_f = ~z[i];

                // Unwrapping
                if (!is_first)
                {
                    if (abs(x_f - prev_x[i]) > pow(2, 15))
                    {
                        x_cycle[i] += x_f < prev_x[i] ? 1 : -1;
                    }
                    if (abs(y_f - prev_y[i]) > pow(2, 15))
                    {
                        y_cycle[i] += y_f < prev_y[i] ? 1 : -1;
                    }
                    if (abs(z_f - prev_z[i]) > pow(2, 15))
                    {
                        z_cycle[i] += z_f < prev_z[i] ? 1 : -1;
                    }
                }

                prev_x[i] = x_f;
                prev_y[i] = y_f;
                prev_z[i] = z_f;

                x_f = x_f + 65536 + x_cycle[i] * 65536;
                y_f = y_f + 65536 + y_cycle[i] * 65536;
                z_f = z_f + 65536 + z_cycle[i] * 65536;

                x_f = x_f * 0.150;
                y_f = y_f * 0.150;
                z_f = z_f * 0.242;

                // Global feature transformation
                float x_temp = x_f;
                float y_temp = y_f;

                x_f = x_temp * cos(ANGLE) - y_temp * sin(ANGLE);
                y_f = x_temp * sin(ANGLE) + y_temp * cos(ANGLE);

                // Local feature transformation
                z_f = (float)1.0 / z_f;

                // Debiasing
                if (debiasing_counter < DEBIAS_WINDOW)
                {
                    x_bias[i] += x_f;
                    y_bias[i] += y_f;
                    z_bias[i] += z_f;

                    x_f = 0;
                    y_f = 0;
                    z_f = 0;
                }
                else
                {

                    x_f -= x_bias[i] / DEBIAS_WINDOW;
                    y_f -= y_bias[i] / DEBIAS_WINDOW;
                    z_f -= z_bias[i] / DEBIAS_WINDOW;
                }

                // Make polynomial features
                float polynomials[20];
                generate_polynomial_features(x_f, y_f, z_f, polynomials);

                // Apply stage I
                apply_model(coef_pointers[i], polynomials, feature_input_stage_II + 3 * i);
            }

            if (debiasing_counter <= DEBIAS_WINDOW)
                debiasing_counter++;

            is_first = false;

            float feature_output_stage_II[3 * NR_OF_SENSORS];

            if (ENABLE_STAGE_II)
            {
                apply_stage_II(feature_input_stage_II, feature_output_stage_II);
            }

            if (debiasing_counter <= DEBIAS_WINDOW)
            {
                delayMicroseconds(comm_time_us);
                return;
            }

            // Output stage. Convert to

            float *to_send = ENABLE_STAGE_II ? feature_output_stage_II : feature_input_stage_II;

            // Convert to 2 bytes and send
            Serial.write(START_BYTE);
            for (uint8_t i = 0; i < 3 * NR_OF_SENSORS; i++)
            {

                uint16_t val;

                if (i % 3 == 2)
                {
                    //  Serial.println(to_send[i]);
                    val = convert(to_send[i], -30.0, 10.0);
                    // Serial.println(val);
                }
                else
                    val = convert(to_send[i], -10.0, 10.0);

                // if (i == 2) {
                //     Serial.println(val);
                // }

                Serial.write((val >> 8) & 0xFF);
                Serial.write(val & 0xFF);
            }
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

// --------------------------------------
// i2c_scanner
//
// Version 1
//    This program (or code that looks like it)
//    can be found in many places.
//    For example on the Arduino.cc forum.
//    The original author is not know.
// Version 2, Juni 2012, Using Arduino 1.0.1
//     Adapted to be as simple as possible by Arduino.cc user Krodal
// Version 3, Feb 26  2013
//    V3 by louarnold
// Version 4, March 3, 2013, Using Arduino 1.0.3
//    by Arduino.cc user Krodal.
//    Changes by louarnold removed.
//    Scanning addresses changed from 0...127 to 1...119,
//    according to the i2c scanner by Nick Gammon
//    https://www.gammon.com.au/forum/?id=10896
// Version 5, March 28, 2013
//    As version 4, but address scans now to 127.
//    A sensor seems to use address 120.
// Version 6, November 27, 2015.
//    Added waiting for the Leonardo serial communication.
//
//
// This sketch tests the standard 7-bit addresses
// Devices with higher bit address might not be seen properly.
//

// #include <Wire.h>

// void setup()
// {
//   Wire.begin();

//   Serial.begin(9600);
//   while (!Serial);             // Leonardo: wait for serial monitor
//   Serial.println("\nI2C Scanner");

//   Wire.beginTransmission(0x77);
//   Wire.write(0x01 << 3);
//   if (Wire.endTransmission() == false)
//   {
//     Serial.println("Success");
//   }
// }

// void loop()
// {
//   byte error, address;
//   int nDevices;

//   Serial.println("Scanning...");

//   nDevices = 0;
//   for(address = 1; address < 127; address++ )
//   {
//     // The i2c_scanner uses the return value of
//     // the Write.endTransmisstion to see if
//     // a device did acknowledge to the address.
//     Wire.beginTransmission(address);
//     error = Wire.endTransmission();

//     if (error == 0)
//     {
//       Serial.print("I2C device found at address 0x");
//       if (address<16)
//         Serial.print("0");
//       Serial.print(address,HEX);
//       Serial.println("  !");

//       nDevices++;
//     }
//     else if (error==4)
//     {
//       Serial.print("Unknown error at address 0x");
//       if (address<16)
//         Serial.print("0");
//       Serial.println(address,HEX);
//     }
//   }
//   if (nDevices == 0)
//     Serial.println("No I2C devices found\n");
//   else
//     Serial.println("done\n");

//   delay(5000);           // wait 5 seconds for next scan
// }
