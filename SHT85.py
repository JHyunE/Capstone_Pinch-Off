import argparse
import time
from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection, CrcCalculator
from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_sht3x.device import Sht3xDevice
from sensirion_i2c_sht3x.commands import (Repeatability)


parser = argparse.ArgumentParser()
parser.add_argument('--i2c-port', '-p', default='/dev/i2c-0')
args = parser.parse_args()

def getTempHumid():
    with LinuxI2cTransceiver(args.i2c_port) as i2c_transceiver:
        channel = I2cChannel(I2cConnection(i2c_transceiver),
                             slave_address=0x44,
                             crc=CrcCalculator(8, 0x31, 0xff, 0x0))
        sensor = Sht3xDevice(channel)
        try:
            sensor.stop_measurement()
            time.sleep(0.001)
        except BaseException:
            ...
        try:
            sensor.soft_reset()
            time.sleep(0.1)
        except BaseException:
            ...
        a_status_register = sensor.read_status_register()
        try:
            (a_temperature, a_humidity
             ) = sensor.measure_single_shot(Repeatability.MEDIUM, False)
            return (a_temperature.value, a_humidity.value)
        except BaseException:
            return False
            
