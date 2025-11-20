from smbus2 import SMBus
import time

I2C_BUS = 1
SLAVE_ADDRESS = 0x08

messages = ["Hello, World!\n", "The quick brown fox jumps over the lazy dog."]

def string_to_bytes(s):
    return [ord(c) for c in s]

with SMBus(I2C_BUS) as bus:
    for msg in messages:
        bus.write_i2c_block_data(SLAVE_ADDRESS, 0, string_to_bytes(msg))
        time.sleep(1)
