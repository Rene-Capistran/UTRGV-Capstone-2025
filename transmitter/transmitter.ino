// Transmitter
#include <SoftwareSerial.h>

SoftwareSerial uartTransmitter(2, 3);


void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  uartTransmitter.begin(9600);
  Serial.print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nTransmitting...\n");

}

void loop() {
  // uartTransmitter.println("Hello, world!");
  uartTransmitter.println("The quick brown fox jumps over the lazy dog.");
  delay(200);
}


