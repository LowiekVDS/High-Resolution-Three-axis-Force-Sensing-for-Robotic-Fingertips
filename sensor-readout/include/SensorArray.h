#ifndef SENSORARRAY_H
#define SENSORARRAY_H

#include <Adafruit_MLX90393.h>
#include <Wire.h>

class SensorArray
{
public:
    SensorArray(uint32_t speed) : speed(speed)
    {
        sensors = nullptr;
        sensorData = nullptr;
        numSensors = 0;
    };

    /**
     * @brief adds a sensor, given the address
     * @param address The I2C address of the sensor to add.
     * @return true if the sensor was successfully added, false if not.
     */
    bool addSensor(uint8_t address);

    Adafruit_MLX90393 *getSensors() { return this->sensors; };

    uint8_t getNumberOfSensors() { return this->numSensors; };

    bool readData(uint16_t *x, uint16_t *y, uint16_t *z);

    Adafruit_MLX90393 *getSensor(uint8_t id)
    {
        if (id >= this->numSensors)
            return nullptr;

        return this->sensors + id;
    };

private:
    Adafruit_MLX90393 *sensors;
    float *sensorData;
    uint8_t numSensors;
    uint32_t speed;
};

#endif
