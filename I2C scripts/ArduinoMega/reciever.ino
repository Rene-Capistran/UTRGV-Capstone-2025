#include <Wire.h>

String recvBuffer = "";
unsigned long lastChunkTime = 0;
bool receiving = false;

void receiveEvent(int howMany) {
  receiving = true;
  lastChunkTime = millis();  

  while (Wire.available()) {
    recvBuffer += (char)Wire.read();
  }
}

void setup() {
  Serial.begin(9600);
  Wire.begin(8);
  Wire.onReceive(receiveEvent);
}

void loop() {

  // If we've received something BUT no new chunks for 20 ms → print full message
  if (receiving && millis() - lastChunkTime > 20) {

    Serial.println(recvBuffer);   // print the FULL message at once

    recvBuffer = "";              // clear for next message
    receiving = false;
  }
}
