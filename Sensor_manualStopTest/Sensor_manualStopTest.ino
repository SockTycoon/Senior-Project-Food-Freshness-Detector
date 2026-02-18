#include "ADS1X15.h"
#include "DHT.h"


ADS1115 ADS(0x48);

#define motor1Pin 2
#define motor2Pin 3
#define DHT11_PIN 4

#define senseDelay 15 * 1000

const unsigned int MAX_MESSAGE_LENGTH = 2;
const char MotorFridge = '1';
const char MotorRoom = '2';
const char MotorStop = '3';
const char SenseData = '4';
const char SenseStop = '5';

DHT dht11(DHT11_PIN, DHT11);

void setup() {
  // put your setup code here, to run once:
  pinMode(motor1Pin, OUTPUT);
  pinMode(motor2Pin, OUTPUT);

  Serial.begin(9600);
  ADS.begin();
  dht11.begin();


  while(!Serial){
    ;//wait for serial connection
  }
  stopMotors();
}

String dataLabel1 = "Ethanol";
String dataLabel2 = "Ammonia";
String dataLabel3 = "Hydrogen Sulfide";
String dataLabel4 = "Temperature";
bool label = true;
bool sense = true;

void loop() {
  ADS.setGain(0);

  while(label){ //runs once
    Serial.println(dataLabel1 + "," + dataLabel2 + "," + dataLabel3 + "," + dataLabel4);
    label=false;
  }

  while(Serial.available() > 0){

  static char message[MAX_MESSAGE_LENGTH];
  static unsigned int message_pos = 0;
  //Read the next available byte in the serial receive buffer
  char inByte = Serial.read();

  if ( inByte != '\n' && (message_pos < MAX_MESSAGE_LENGTH - 1) )
   {
     //Add the incoming byte to our message
     message[message_pos] = inByte;
     message_pos++;
   }
   //Full message received...
   else
   {
     //Add null character to string
     message[message_pos] = '\0';
     //Print the message (or do other things)
     switch(message[0]) {
      case MotorFridge:
      //Serial.println("pumping air from fridge");
      pumpAirFridge();
      break;
      case MotorRoom:
      //Serial.println("pumping air from room");
      pumpAirRoom();
      break;
      case MotorStop:
      //Serial.println("stopping all motors");
      stopMotors();
      break;
      case SenseData:
      //Serial.println("collecting sensor data");
      sense = true;
      getSensorData();
      break;
      default:
      Serial.println("ERROR!");
      break;
     }
     //Reset for the next message
     message_pos = 0;
   }

  }
}

void pumpAirFridge() {
  //activate fridge pump motor
  digitalWrite(motor1Pin, LOW);
  //deactivate room pump motor
  digitalWrite(motor2Pin, HIGH);
}

void pumpAirRoom() {
  //deactivate fridge pump motor
  digitalWrite(motor1Pin, HIGH);
  //activate room pump motor
  digitalWrite(motor2Pin, LOW);
}

void stopMotors() {
  //deactivate all pump motors
  digitalWrite(motor1Pin, HIGH);
  digitalWrite(motor2Pin, HIGH);
}

void getSensorData() {
  while(sense){
    delay(senseDelay);
    int16_t val_ethanol = ADS.readADC(0);  
    int16_t val_ammonia = ADS.readADC(1);  
    int16_t val_hsulfid = ADS.readADC(2);  
    float val_tempF = dht11.readTemperature(true);
    
    String data = String(val_ethanol) + "," + String(val_ammonia) + "," + String(val_hsulfid) + "," + String(val_tempF);
    Serial.println(data);

    while(Serial.available() > 0){

    static char message[MAX_MESSAGE_LENGTH];
    static unsigned int message_pos = 0;
    //Read the next available byte in the serial receive buffer
    char inByte = Serial.read();

    if ( inByte != '\n' && (message_pos < MAX_MESSAGE_LENGTH - 1) )
    {
       //Add the incoming byte to our message
      message[message_pos] = inByte;
      message_pos++;
    }
    //Full message received...
   else
   { if(message[0] == SenseStop) sense = false; }
  }
  }
  //Serial.println("sensing complete");
}
