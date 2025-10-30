# sender.py
import time, serial

# Adjust if needed: '/dev/ttyAMA0' or '/dev/ttyS0'
PORT = "/dev/serial0"
BAUD = 115200

with serial.Serial(PORT, BAUD, timeout=1) as ser:
    n = 0
    while True:
        msg = f"MSG {n} - hello from Pi A\r\n"
        ser.write(msg.encode("utf-8"))
        print("Sent:", msg.strip())
        n += 1
        time.sleep(1)