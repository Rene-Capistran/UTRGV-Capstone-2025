// Transmitter
#include <SoftwareSerial.h>

SoftwareSerial uartTransmitter(10, 11);


void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  uartTransmitter.begin(9600);
  Serial.print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nTransmitting...\n");

}

void loop() {
  // Small
  // uartTransmitter.println("Hello, world!");

  // Medium
  uartTransmitter.println("The quick brown fox jumps over the lazy dog.");

  // Large
  // uartTransmitter.println("In telecommunication and data transmission, serial communication is the process of sending data one bit at a time, sequentially, over a communication channel or computer bus.");
  delay(200);
}


