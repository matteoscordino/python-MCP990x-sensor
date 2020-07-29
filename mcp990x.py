# mcp990x.py - driver class for the I2C based Microchip MCP990x temperature sensors family

"""This module allows driving the I2C temp sensor"""
import smbus


class Sensor(object):
    """Sensor([bus]) -> Sensor
    Return a new Sensor object that is connected to the
    specified I2C device interface.
    """
    REG_ADDR_TEMP_HIGH = 0x00
    REG_ADDR_TEMP_LOW = 0x29
    REG_ADDR_LAST = 0xFF
    _bus = None
    _debug = False
    _i2c_addr = 0b1001100

    def __init__(self, bus=0,  preinited_bus=None, debug=False, i2c_addr=0b1001100):
        # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1), etc
        if preinited_bus is not None:
            if debug:
                print("using preinited-bus, address {0}".format(address))
            self._bus = preinited_bus
        else:
            if debug:
                print("init-ing bus {0}, address {1}".format(bus, address))
            self._bus = smbus.SMBus(bus)
        self._debug = debug
        self._i2c_addr = i2c_addr

    def close(self):
        """close()
        Disconnects the object from the bus.
        """
        self._bus.close()
        self._bus = None

    def __write_register(self, reg_addr, values):
        """ this writes a 8 bit register pointed to by reg_addr.
        """
        if self._bus is None:
            raise IOError("Bus not open")
        if reg_addr > self.REG_ADDR_LAST:
            raise IOError("Invalid register address {0}".format(reg_addr))
        if len(values) > 1:
            raise IOError("Invalid data length {0}".format(len(values)))

        self._bus.write_i2c_block_data(self._i2c_addr, reg_addr, values)

    def __read_register(self, reg_addr):
        """ this reads a 8 bit register pointed to by reg_addr
        """
        if self._bus is None:
            raise IOError("Bus not open")
        if reg_addr > self.REG_ADDR_LAST:
            raise IOError("Invalid register address {0}".format(reg_addr))

        return self._bus.read_byte_data(self._i2c_addr, reg_addr)

    def read(self):
        """read()
        read the current temperature
        """
        raw_temp_reg_low = self.__read_register(self.REG_ADDR_TEMP_LOW)
        raw_temp_reg_high = self.__read_register(self.REG_ADDR_TEMP_HIGH)

        # stitch together the temp reading bytes: the total data is 11 bits,
        # with the most significant 8 in the high reg and the least significant 3
        # in the top 3 bits of the low reg. So, OR them together as a 17 bits integer,
        # then shift everything right by 5
        raw_temp_reg = ((raw_temp_reg_high << 8) | raw_temp_reg_low) >> 5
        if self._debug:
            print("reg: " + hex(raw_temp_reg))

        temp = raw_temp_reg * 0.125
        if self._debug:
            print(str(temp))

        return temp
