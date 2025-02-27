int servoPin = 9;

void setup() {
    pinMode(servoPin, OUTPUT);
}

void loop() {
    digitalWrite(servoPin, HIGH);
    delayMicroseconds(1500); // 90도 위치 (1.5ms 펄스)
    digitalWrite(servoPin, LOW);
    delay(20);  // 20ms 주기 유지
}
