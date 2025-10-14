// Transmitter
#include <SoftwareSerial.h>

void longSend(String msg);

SoftwareSerial uartTransmitter(2, 3);

char large_msg_chars[1000] = "In telecommunication and data transmission, serial communication is the process of sending data one bit at a time, sequentially, over a communication channel or computer bus. This is in contrast to parallel communication, where several bits are sent as a whole, on a link with several parallel channels. Serial communication is used for all long-haul communication and most computer networks, where the cost of cable and difficulty of synchronization make parallel communication impractical. Serial computer buses have become more common even at shorter distances, as improved signal integrity and transmission speeds in newer serial technologies have begun to outweigh the parallel bus's advantage of simplicity (no need for serializer and deserializer, or SerDes) and to outstrip its disadvantages (clock skew, interconnect density). The migration from PCI to PCI Express (PCIe) is an example.";
String partial_msg;
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  uartTransmitter.begin(9600);
  Serial.print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nTransmitting...\n");

}

void loop() {
  // uartTransmitter.println("Hello, world!");
  uartTransmitter.println("The quick brown fox jumps over the lazy dog.");

  // for(int i = 0; i < 1000; i++){
  //   if(isAscii(large_msg_chars[i]))
  //     partial_msg += String(large_msg_chars[i]);
  //   if(partial_msg.length() > 20){
  //     Serial.print(partial_msg);
  //     uartTransmitter.print(partial_msg);
  //     String partial_msg;
  //   }
  // }
  Serial.print('\n');
  
  delay(50);
  

}


// void longSend(char msg[]){
//   int msgLen = msg.length();
//   Serial.println(msg);
//   for(int pos = 0; pos < msgLen; pos += 50){
//     String part = msg.substring(pos - 50, pos);
//     uartTransmitter.println(part);
//     Serial.println(part);
//   }

// }