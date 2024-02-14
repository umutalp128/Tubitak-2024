void setup() {
  pinMode(12, INPUT);
  Serial.begin(115200);
}

void loop() {
 Serial.println(digitalRead(12));
}
