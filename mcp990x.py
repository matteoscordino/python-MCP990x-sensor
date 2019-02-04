# sensor.py - driver class for the I2C based Atmel at30ts00 temperature sensor

"""This module allows driving the I2C temp sensor"""
import smbus


class Sensor(object):
    """Sensor([bus]) -> Sensor
    Return a new Sensor object that is connected to the
    specified I2C device interface.
    """
    REG_ADDR_CAPABILITY = 0x00
    REG_ADDR_CONFIGURATION = 0x01
    REG_ADDR_UPPERALARM = 0x02
    REG_ADDR_LOWERALARM = 0x03
    REG_ADDR_CRITICALALRAM = 0x04
    REG_ADDR_TEMP = 0x05
    REG_ADDR_MANUF_ID = 0x06
    REG_ADDR_DEV_ID = 0x07
    REG_ADDR_RESERVED1 = tuple(range(0x08, 0x22))
    REG_ADDR_SMBUS = 0x22
    REG_ADDR_RESERVED2 = tuple(range(0x23, 0xFF))
    REG_ADDR_LAST = REG_ADDR_DEV_ID
    _bus = -1
    _debug = False
    _i2c_addr = 0b0011011

    def __init__(self, bus=0, debug=False, i2c_addr=0b0011011):
        # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1), etc
        self._bus = smbus.SMBus(bus)
        self._debug = debug
        self._i2c_addr = i2c_addr

    def close(self):
        """close()
        Disconnects the object from the bus.
        """
        self._bus.close()
        self._bus = -1

    def __write_register(self, reg_addr, values):
        """ this writes a 16 bit register pointed to by reg_addr.
        """
        if reg_addr > self.REG_ADDR_LAST:
            raise IOError("Invalid register address {0}".format(reg_addr))
        if len(values) > 2:
            raise IOError("Invalid data length {0}".format(len(values)))

        self._bus.write_i2c_block_data(self._i2c_addr, reg_addr, values)

    def __read_register(self, reg_addr):
        """ this reads a 16 bit register pointed to by reg_addr
        """
        if reg_addr > self.REG_ADDR_LAST:
            raise IOError("Invalid register address {0}".format(reg_addr))

        return self._bus.read_word_data(self._i2c_addr, reg_addr)

    def read(self):
        """read()
        read the current temperature
        """
        raw_temp_reg = self.__read_register(self.REG_ADDR_TEMP)

        # invert the endianness
        raw_temp_reg = ((raw_temp_reg >> 8)&0xff) | ((raw_temp_reg << 8)&0xff00)
        if self._debug:
            print("reg: " + hex(raw_temp_reg))

        temp = raw_temp_reg & 0xFFF
        if self._debug:
            print(str(temp))
        temp /= 16.0
        if self._debug:
            print(str(temp))

        if raw_temp_reg & (1 << 12):
            temp *= -1.0
            if self._debug:
                print(str(temp))

        return temp
