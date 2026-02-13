#include "ADS1X15.h"

ADS1115 ADS(0x48);

#define motorPin 2
#define valveFridge 5
#define valveRoom 6
//delays are in ms
#define senseDelay 1 * 5 * 1000
#define cleanDelay 1 * 10 * 1000
#define longDelay  1 * 10 * 1000

void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);

ADS.begin();
pinMode(motorPin, OUTPUT);
pinMode(valveFridge, OUTPUT);
pinMode(valveRoom, OUTPUT);
}

String dataLabel1 = "Ethanol";
String dataLabel2 = "Ammonia";
String dataLabel3 = "Hydrogen Sulfide";
bool label = true;

void loop() {
  // put your main code here, to run repeatedly:
  ADS.setGain(0);
//print out column headers
  while(label){ //runs once
    Serial.println(dataLabel1 + "," + dataLabel2 + "," + dataLabel3);
    label=false;
  }
  //activate air pump from fridge
  pumpAirFromFridge();
  //let run for X minutes
  delay(senseDelay);
  // use senseFunction() to gather data
  senseFunction();
  //deactivate pump
  pumpDeactivate();
}

void senseFunction() {
  int16_t val_ethanol = ADS.readADC(0);  
  int16_t val_ammonia = ADS.readADC(1);  
  int16_t val_hsulfid = ADS.readADC(2);  
  
  String data = String(val_ethanol) + "," + String(val_ammonia) + "," + String(val_hsulfid);
  Serial.println(data);
}

void pumpAirFromFridge() {
  //activate solenoids so tube to fridge is open
  digitalWrite(valveFridge, LOW);
  digitalWrite(valveRoom, HIGH);
  //activate pump motor
  digitalWrite(motorPin, LOW);
}

void pumpAirFromRoom() {
  //activate solenoids so tube to room is open
  digitalWrite(valveFridge, HIGH);
  digitalWrite(valveRoom, LOW); 
  //activate pump motor
  digitalWrite(motorPin, LOW);
}

void pumpDeactivate() {
  //activate solemnoids so tube to room is open
  digitalWrite(valveFridge, LOW);
  digitalWrite(valveRoom, HIGH);
  //deactivate pump motor
  digitalWrite(motorPin, HIGH);
}