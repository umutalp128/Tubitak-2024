
#include "LoRa_E32.h"
#include <SoftwareSerial.h>
String oda = " ";

bool durum = false;
char cdurum ;
SoftwareSerial piSerial(12,13); 
SoftwareSerial mySerial(3, 4); //PCB versiyon 4.3 den sonra bu şekilde olmalı
String recivedData ;
LoRa_E32 e32ttl(&mySerial);
 struct Signal  {
      char type[30] = "test Odası";
      bool state[1] ;
     
    } data;
 
void setup() {
 
  Serial.begin(115200);
  e32ttl.begin();
  delay(500);
piSerial.begin(9600);

}
 
void loop() {
  while (e32ttl.available()  > 1) {
 
    // Gelen mesaj okunuyor
   ResponseStructContainer rsc = e32ttl.receiveMessage(sizeof(Signal));
    
    //Gönderilecek paket veri hazırlanıyor
    struct Signal  {
      char type[30] = "test Odası";
      bool state[1];
 
    } data2;
 
   // Serial.println(rs.getResponseDescription());
   if(piSerial.available() > 1){
    recivedData = piSerial.readString();
    //Serial.println(recivedData);
    oda = recivedData ;
    oda.remove(oda.indexOf('§')  - 1);
    
    cdurum  = recivedData.charAt((recivedData.length() - 1));
    Serial.println(cdurum);

    
    Serial.println(oda);
  
  
    // ayırıcı § ,
    if(cdurum == 'y'){
      durum = 1 ;
    }
    else if(cdurum == 'n'){
      durum = 0 ;
    }
     
   }
    
   
   *(bool*)(data2.state) = durum ;
    ResponseStatus rs = e32ttl.sendFixedMessage(0, 63, 23, &data2, sizeof(Signal));
  }
 
}