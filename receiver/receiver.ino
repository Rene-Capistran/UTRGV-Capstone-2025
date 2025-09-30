// Receiver
#include <SoftwareSerial.h>

void blink();

SoftwareSerial uartReceiver(2, 3);

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  uartReceiver.begin(9600);
  Serial.print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nReceiving...\n");
}


void loop() {
  if(uartReceiver.available() > 0){
    String message = uartReceiver.readStringUntil('\n');
    Serial.println(message);
  }
}

