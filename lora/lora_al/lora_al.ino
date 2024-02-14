#include "LoRa_E32.h"
#include <SoftwareSerial.h>
 
SoftwareSerial mySerial(3, 4); //PCB versiyon 4.3 den sonra bu şekilde olmalı
 
/*
   Pinler     Arduino Nano    Lora E32 433T20d
                  11                3
                  10                4
*/
 
LoRa_E32 e32ttl(&mySerial);
#define M0 7
#define M1 6
String recvData = "";
struct Signal {
  char type[30] = "test.com";
  bool state[1];

} data;
char cdurum = 'n';
 
void setup() {
  pinMode(M0, OUTPUT);
  pinMode(M1, OUTPUT);
  digitalWrite(M0, LOW);
  digitalWrite(M1, LOW);
  pinMode(9, OUTPUT);
  Serial.begin(115200);
  e32ttl.begin();
  delay(500);
}
 
void loop() {
 
  ResponseStatus rs = e32ttl.sendFixedMessage(0, 44, 23, &data, sizeof(Signal));

 
  delay(2000);
 
  while (e32ttl.available()  > 1) {
    ResponseStructContainer rsc = e32ttl.receiveMessage(sizeof(Signal));
    struct Signal data = *(Signal*) rsc.data;
    String name = data.type;

    name.replace("ö","o");
    name.replace("ü","u");
    name.replace("ı","i");
    name.replace("ğ","g");
    name.replace("Ö","O");
    name.replace("Ü","U");
    name.replace("İ","I");
    name.replace("Ğ","G");
    name.replace("ç","c");
    name.replace("Ç","C");
    /*
    Serial.print("Yer: ");
    Serial.println(name);
    Serial.print("durum: ");
    Serial.println(*(bool*)(data.state));
    */
    digitalWrite(5,*(bool*)(data.state));
    if(*(bool*)(data.state)==true){
      cdurum = 'y';
    }
    else if(*(bool*)(data.state)==false){
      cdurum = 'n';
    }
    recvData = name + "$" + cdurum;
    Serial.println(recvData);
    rsc.close();
  }
}