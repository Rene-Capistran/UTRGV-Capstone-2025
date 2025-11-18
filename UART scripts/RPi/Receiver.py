import serial
import time 
SERIAL_PORT = '/dev/ttyAMA0'
BAUD_RATE = 9600

print("Listening for UART data...")

with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
    while True:
        data = ser.readline()
        if data:
            print("Received:". data.decode('utf-8', errors='replace'))
