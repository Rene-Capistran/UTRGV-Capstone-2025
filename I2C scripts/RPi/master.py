import smbus2 as smbus  
import time
from smbus2 import i2c_msg


I2C_BUS = 1
SLAVE_ADDRESS = 0x08

# Messages (defined as strings)
SMALL_MESSAGE = "Hello, world!"
MEDIUM_MESSAGE = "The quick brown fox jumps over the lazy dog."
LARGE_MESSAGE = "In telecommunication and data transmission, serial communication is the process of sending data one bit at a time, sequentially, over a communication channel or computer bus."

def string_to_bytes(s):
    """Converts a string to a list of byte integers (ASCII values)."""
    return [ord(c) for c in s]

def send_i2c_message(bus, address, message_bytes, message_string):
    """Sends a list of bytes over I2C using smbus2 block writes and prints the message string."""
    try:
        write_msg = i2c_msg.write(address, message_bytes)
        bus.i2c_rdwr(write_msg)
        print(f"Sent message: {message_string}") 
    except IOError as e:
        print(f"I2C error: {e}")

with smbus.SMBus(I2C_BUS) as bus:
    current_message = SMALL_MESSAGE
    print(f"Starting to send: {current_message}")

    while True:
        message_bytes = string_to_bytes(current_message)
        send_i2c_message(bus, SLAVE_ADDRESS, message_bytes, current_message)
        time.sleep(0.200)
