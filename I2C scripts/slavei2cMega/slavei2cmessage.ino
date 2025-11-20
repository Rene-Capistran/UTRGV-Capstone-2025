#include <Wire.h>

volatile bool hasData = false;
String recvBuffer = "";

void receiveEvent(int howMany) {
  recvBuffer = "";

  while (Wire.available()) {
    char c = Wire.read();
    recvBuffer += c;
  }

  hasData = true;   // signal main loop
}

void setup() {
  Serial.begin(9600);
  Wire.begin(8);  // slave address
  Wire.onReceive(receiveEvent);
}

void loop() {
  if (hasData) {
    //Serial.print("Received: ");
    Serial.println(recvBuffer);
    hasData = false;
  }
}
