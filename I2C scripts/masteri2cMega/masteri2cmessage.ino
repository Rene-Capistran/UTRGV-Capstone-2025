#include <Wire.h>

String message = "Hello world!";
// String message = "The quick brown fox jumps over the lazy dog.";
// String message = "In telecommunication and data transmission, serial communication is the process of sending data one bit at a time, sequentially, over a communication channel or computer bus.";

void setup() {
  Wire.begin();  // I2C master
  Serial.begin(9600);
}

void loop() {
  Serial.print("Sending: ");
  Serial.println(message);

  Wire.beginTransmission(8);
  Wire.write(message.c_str());
  Wire.endTransmission();

  delay(200);
}
