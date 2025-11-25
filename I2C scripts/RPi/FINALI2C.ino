
#include <Wire.h>

#define I2C_DEV_ADDR 0x08
#define SDA_PIN 21
#define SCL_PIN 22

static void preloadReply() {
  static uint32_t counter = 0;
  char msg[32];
  int n = snprintf(msg, sizeof(msg), "Packet #%lu", (unsigned long)counter++);
  if (n < 0) n = 0;
  Wire.slaveWrite((const uint8_t*)msg, (size_t)n);
}

static void onRequest() {
  Serial.println("[I2C] onRequest (reply preloaded)");
}

static void onReceive(int len) {
  Serial.printf("[I2C] onReceive (%d bytes): ", len);
  while (Wire.available()) {
    uint8_t b = Wire.read();
    Serial.printf("%02X ", b);
  }
  Serial.println();
  preloadReply();
}

void setup() {
  delay(300);
  Serial.begin(9600);
  Serial.println("[BOOT] ESP32 I2C Slave starting...");
  Serial.printf("[BOOT] Using pins SDA=%d SCL=%d, address=0x%02X\n", SDA_PIN, SCL_PIN, I2C_DEV_ADDR);

  Wire.setPins(SDA_PIN, SCL_PIN);
  Wire.onReceive(onReceive);
  Wire.onRequest(onRequest);
  bool ok = Wire.begin((uint8_t)I2C_DEV_ADDR);
  Serial.printf("[BOOT] Wire.begin() %s\n", ok ? "OK" : "FAILED");

  preloadReply();
  Serial.println("[BOOT] Ready. Waiting for Pi to write/read...");
}

void loop() {
  static uint32_t last = 0;
  if (millis() - last >= 1000) {
    last += 1000;
    Serial.println("[HB] idle");
  }
}
