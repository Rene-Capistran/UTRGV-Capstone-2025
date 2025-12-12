// Receiver
#include <SoftwareSerial.h>

void blink();

SoftwareSerial uartReceiver(10, 11);

int count = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  uartReceiver.begin(9600);
  Serial.print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nReceiving...\n");
}


void loop() {
  if(uartReceiver.available() > 0){
    count++;
    char buffer[20];
    String message = uartReceiver.readStringUntil('\n');

    // Output formatting
    String msg = static_cast<String>(count) + ": " + message;
    Serial.println(msg);
  }
}

