#include <dht.h>

const int echoPin = A5;
const int trigPin = A4;
const int dhtPin = A3;
const int photoPin = 8;

long duration, photo, distance;
dht DHT;
 
void setup() {
  Serial.begin (9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(photoPin,INPUT);
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(5);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  pinMode(echoPin, INPUT);
  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2; // cm

  DHT.read11(dhtPin);

  photo =digitalRead(photoPin);
  if (photo==HIGH) {
    photo = LOW;
  }
  else {
    photo = HIGH;
  }
  
  Serial.print(distance); // cm
  Serial.print(" ");
  Serial.print(DHT.humidity); // %
  Serial.print(" ");
  Serial.print(DHT.temperature); // °C
  Serial.print(" ");
  Serial.print(photo); // 1/0
  Serial.println();
  
  delay(1000);
}
