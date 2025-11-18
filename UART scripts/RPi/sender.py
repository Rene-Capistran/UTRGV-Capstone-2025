import serial
import time

# Define constants for the serial communication
SERIAL_PORT = '/dev/ttyAMA0'
BAUD_RATE = 9600  # Specify the baud rate. Common rates include 9600, 19200, 57600, or 115200.
SMALL_MESSAGE = "Hello, world!\n"
MEDIUM_MESSAGE = "The quick brown fox jumps over the lazy dog."
LARGE_MESSAGE = "In telecommunication and data transmission, serial communication is the process of sending data one bit at a time, sequentially, over a communication channel or computer bus."
# The 'with' statement ensures the port is closed automatically when finished
with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
    # This message is printed once, confirming the port is open
    print("Port opened successfully.")
    
    while True:
        # Wait for 10 seconds before sending the first message.
        # This is useful for giving a receiver device time to start up.
        
        
        # Print the message that is about to be sent
        print(f"Sending: {MEDIUM_MESSAGE.strip()}")
        
        # Encode the message string to bytes and write it to the serial port
        ser.write(MEDIUM_MESSAGE.encode("utf-8"))
        
        # Print a confirmation that the message was sent
        print("Message sent.")
        
        # Pause for a short period before the loop repeats
        time.sleep(0.200)
