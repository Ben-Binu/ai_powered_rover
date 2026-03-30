#include <SoftwareSerial.h>
#include <TinyGPS++.h>

// GPS on Pins 2 (RX) and 3 (TX)
SoftwareSerial ss(2, 3); 
TinyGPSPlus gps;

// L298N Motor Pins
const int IN1=9, IN2=8, IN3=7, IN4=6, ENA=10, ENB=5;

// Navigation Variables
double pLat = 0, pLon = 0;
bool holeMarked = false;

void setup() {
  Serial.begin(9600);
  ss.begin(9600);
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
}

void loop() {
  // 1. Process GPS Data
  while (ss.available() > 0) {
    if (gps.encode(ss.read())) {
      sendDataToPi();
    }
  }

  // 2. Process Pi Commands
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 'F') moveForward();
    else if (cmd == 'S') stopMotors();
    else if (cmd == 'L') turnLeft();
    else if (cmd == 'R') turnRight();
    else if (cmd == 'M') { // Mark Pothole Location
      pLat = gps.location.lat();
      pLon = gps.location.lng();
      holeMarked = true;
    }
  }
}

void sendDataToPi() {
  if (gps.location.isValid()) {
    double dist = 0;
    if (holeMarked) {
      dist = TinyGPSPlus::distanceBetween(gps.location.lat(), gps.location.lng(), pLat, pLon);
    }
    // Output format for Pi: GPS:LAT,LON,DIST
    Serial.print("GPS:");
    Serial.print(gps.location.lat(), 6); Serial.print(",");
    Serial.print(gps.location.lng(), 6); Serial.print(",");
    Serial.println(dist);
  }
}

void moveForward() { digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW); digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW); analogWrite(ENA, 150); analogWrite(ENB, 150); }
void stopMotors() { digitalWrite(IN1, LOW); digitalWrite(IN2, LOW); digitalWrite(IN3, LOW); digitalWrite(IN4, LOW); }
void turnLeft() { digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH); digitalWrite(R_IN3, HIGH); digitalWrite(R_IN4, LOW); }
void turnRight() { digitalWrite(IN1, HIGH); digitalWrite(L_IN2, LOW); digitalWrite(R_IN3, LOW); digitalWrite(R_IN4, HIGH); }
