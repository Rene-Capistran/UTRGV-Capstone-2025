# receiver.py
import serial

PORT = "/dev/serial0"
BAUD = 115200

with serial.Serial(PORT, BAUD, timeout=1) as ser:
    print("Listening on", PORT, "at", BAUD, "baud...")
    while True:
        line = ser.readline()
        if line:
            print("Received:", line.decode(errors="replace").strip())