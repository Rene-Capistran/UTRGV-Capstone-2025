#include <Wire.h>

// String message = "Hello world!";
String message = "The quick brown fox jumps over the lazy dog.";
// String message = "In telecommunication and data transmission, serial communication is the process of sending data one bit at a time, sequentially, over a communication channel or computer bus.";

void setup() {
  Wire.begin();
  Serial.begin(9600);
}

void loop() {
  const char* msg = message.c_str();
  int len = message.length();

  // Send in ~28 byte chunks
  for (int i = 0; i < len; i += 28) {
    Wire.beginTransmission(8);

    int chunkLen = min(28, len - i);
    Wire.write((uint8_t*)(msg + i), chunkLen);

    Wire.endTransmission();
    delay(3);   // allow slave time to process
  }

  delay(200);
}
