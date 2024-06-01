#include "SensorArray.h"

bool SensorArray::readData(uint16_t *x, uint16_t *y, uint16_t *z)
{

  // First start all measurements
  for (int i = 0; i < this->numSensors; i++)
  {
    if (!this->sensors[i].startSingleMeasurement())
      return false;
  }

  // Delay (assume same conversion time for all sensors)
  this->sensors[0].waitForConversion();

  // Now get data
  for (uint8_t i = 0; i < this->numSensors; i++)
  {
    if (!this->sensors[i].readRawMeasurement(x + i, y + i, z + i))
      return false;
  }

  return true;
}

bool SensorArray::setMuxChannel(uint8_t chan)
{

  // Compatibility layer with non-mux systems
  if (this->mux_addr < 0x70 || this->mux_addr > 0x77)
  {
    return true;
  }

  if (chan == this->current_chan)
  {
    return true;
  }

  Wire.beginTransmission(this->mux_addr);
  Wire.write(0x01 << chan);
  if (Wire.endTransmission() == false)
  {
    this->current_chan = chan;
    return true;
  }

  return false;
}

Adafruit_MLX90393 *SensorArray::getSensor(uint8_t id)
{
  this->setMuxChannel((this->addresses[id] & 0xf0) >> 4);

  if (id >= this->numSensors)
    return nullptr;

  return this->sensors + id;
}

bool SensorArray::addSensors(uint8_t *addresses, uint8_t numSensors)
{

  for (uint8_t i = 0; i < numSensors; i++)
  {
    // Set channel (if not set yet)
    bool channel_set = this->setMuxChannel((addresses[i] & 0xf0) >> 4);

    if (!channel_set) {
      Serial.print("Failed to set channel ");
      Serial.println((addresses[i] & 0xf0) >> 4);
      return false;
    }

    // Init the new sensor
    if (!channel_set || !this->sensors[i].begin_I2C(addresses[i] & 0x0f, this->speed))
    {
      Serial.print("Failed to initialize sensor ");
      Serial.println(addresses[i], 16);
      return false;
    }
  }

  this->addresses = addresses;
  this->numSensors = numSensors;

  return true;
}