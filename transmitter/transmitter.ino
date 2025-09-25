// Transmitter
#include <SoftwareSerial.h>

void repeat(String text);

SoftwareSerial uartTransmitter(2, 3);

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  uartTransmitter.begin(9600);
}

void loop() {
  uartTransmitter.println("Hello, world!");
  delay(200);
  // if(Serial.available() > 0){
  //   String message = Serial.readStringUntil('\n');
  //   uartTransmitter.println(message);
  //   digitalWrite(LED_BUILTIN, HIGH);
  //   delay(1000);
  //   digitalWrite(LED_BUILTIN, LOW);
  //   delay(1000);
  // }

}