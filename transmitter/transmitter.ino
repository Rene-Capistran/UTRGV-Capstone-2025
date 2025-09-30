// Transmitter
#include <SoftwareSerial.h>

void repeat(String text);

SoftwareSerial uartTransmitter(2, 3);

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  uartTransmitter.begin(9600);
  Serial.print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nTransmitting...\n");
}

void loop() {
  // manualComm();

  uartTransmitter.println("Hello, world!");
  delay(500);
  

}

void manualComm(){
  if(Serial.available() > 0){
      String message = Serial.readStringUntil('\n');
      uartTransmitter.println(message);
    }
}