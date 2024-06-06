#ifndef SENSORARRAY_H
#define SENSORARRAY_H

#include <Adafruit_MLX90393.h>
#include <Wire.h>

class SensorArray
{
public:
    SensorArray(uint32_t speed, Adafruit_MLX90393* sensors, uint8_t mux_addr = 0x00) : speed(speed), sensors(sensors), mux_addr(mux_addr)
    {
        sensorData = nullptr;
        numSensors = 0;
        current_chan = 255;
    };

    bool addSensors(uint8_t *addresses, uint8_t numSensors);

    Adafruit_MLX90393 *getSensors() { return this->sensors; };

    uint8_t getNumberOfSensors() { return this->numSensors; };

    bool readData(uint16_t *x, uint16_t *y, uint16_t *z);

    Adafruit_MLX90393 *getSensor(uint8_t id);

    bool setMuxChannel(uint8_t chan);

private:
    Adafruit_MLX90393 *sensors;
    uint8_t *addresses;
    float *sensorData;
    uint8_t numSensors;
    uint32_t speed;
    uint8_t mux_addr;
    uint8_t current_chan;
};

#endif
