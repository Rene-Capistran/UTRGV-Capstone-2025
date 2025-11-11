# sender.py
import time, serial

# Adjust if needed: '/dev/ttyAMA0' or '/dev/ttyS0'
PORT = "/dev/serial0"
BAUD = 9600

with serial.Serial(PORT, BAUD, timeout=1) as ser:
    n = 0
    while True:
        small = "Hello, world!"
        medium = "The quick brown fox jumps over the lazy dog."
        large = "In telecommunication and data transmission, serial communication is the process of sending data one bit at a time, sequentially, over a communication channel or computer bus."

        msg = small
        
        ser.write(msg.encode("utf-8"))
        print("Sent:", msg.strip())
        n += 1
        time.sleep(1)