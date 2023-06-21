#line 1 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
/*********************************************************************************
  *Copyright(C),Jilin University China
  *FileName:  SensorArraySystem
  *Author:  Torey Gu(Gu Tianyi)
  *Version:  v0.1.0
  *Date:  2023 July 20
  *Description:  Measure the resistance signal of six semiconductor gas sensors and 
                communicate with the host computer through BLE Bluetooth and serial 
                ports 
  *Others:      The development board used in this system is Arduino nano 33 BLE Sense
                Nrf52840 can also be used instead of Arduino
  *Function List:  
     1. readSensorValue() 
     2. OledPrint_xxxx()
     3. EventSW1()/EventSW2()
     4. SendSerialBuffer()

  *History: 
     1.Date:        2023 July 20
       Author:      Torey Gu(Gu Tianyi) 
       Modification:Createde the main body of the project
                    include : 1.BLE communication 
                              2.Analog signal input
                              3.Oled GUI system(12864)
                              4.HTS221 signal input
                              5.SW1/SW2 interrupt
**********************************************************************************/

/*HeadFiles*/
//board Headfile
#include <Arduino.h>
//GUI HeadFile
#include <U8g2lib.h>
#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif
//BLE Headfile
#include <ArduinoBLE.h>
#include "ble/BLE.h"
//humi Sensor Headfile
#include <Arduino_HTS221.h>
//c++ HeadFile
#include <sstream>
using namespace std;

/*macros*/
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);
#define NameLeft  0
#define NameRight 64
#define ResLeft   20
#define ResRight  84

/*Global variables*/
//pin in
extern const int PinU3 = A2;
extern const int PinU4 = A1;
extern const int PinU5 = A0;
extern const int PinU6 = A6;
extern const int PinU7 = A3;
extern const int PinU8 = A7;
//keyboard in
const int buttonSW1 = D10;
const int buttonSW2 = D9;
extern bool oledMode = 0;
extern bool bufferFlag = 0;
//sensor value
float ValueU3 = 0;
float ValueU4 = 0;
float ValueU5 = 0;
float ValueU6 = 0;
float ValueU7 = 0;
float ValueU8 = 0;
//humi value
float humi = 0;


/* BLE configs */
BLEService SensorArray("1809");
BLEFloatCharacteristic SensorSignalHumi("19B10011-E8F2-537E-4F6C-D104768A1212" , BLERead | BLENotify);
BLEFloatCharacteristic SensorSignalU3("19B10011-E8F2-537E-4F6C-D104768A1213" , BLERead | BLENotify);
BLEFloatCharacteristic SensorSignalU4("19B10011-E8F2-537E-4F6C-D104768A1214" , BLERead | BLENotify);
BLEFloatCharacteristic SensorSignalU5("19B10011-E8F2-537E-4F6C-D104768A1215" , BLERead | BLENotify);
BLEFloatCharacteristic SensorSignalU6("19B10011-E8F2-537E-4F6C-D104768A1216" , BLERead | BLENotify);
BLEFloatCharacteristic SensorSignalU7("19B10011-E8F2-537E-4F6C-D104768A1217" , BLERead | BLENotify);
BLEFloatCharacteristic SensorSignalU8("19B10011-E8F2-537E-4F6C-D104768A1218" , BLERead | BLENotify);

/* Functions */
#line 91 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
std::string Convert(float Num);
#line 98 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void readSensorValue();
#line 107 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void OledStandby();
#line 119 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void OledPrintSeneor();
#line 144 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void OledPrintStream();
#line 150 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void OledPrintBLE();
#line 160 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void OledPrintUsb();
#line 165 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void OledPrintHeater();
#line 168 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void OledPrintData();
#line 178 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void SendData();
#line 200 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void SendSerialBuffer();
#line 207 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void EventSW1();
#line 211 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void EventSW2();
#line 217 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void InitBle();
#line 232 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void setup();
#line 245 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
void loop();
#line 91 "C:\\Users\\qwer1\\Desktop\\array\\sketch_jun19a\\sketch_jun19a.ino"
std::string Convert(float Num){//convert float to string
    std::ostringstream oss;
    oss<<Num;
    std::string str(oss.str());
    return str;
}

void readSensorValue(){//read Analog Signal
    ValueU3 = float(analogRead(PinU3)*3.3/1024);
    ValueU4 = float(analogRead(PinU4)*3.3/1024);
    ValueU5 = float(analogRead(PinU5)*3.3/1024);
    ValueU6 = float(analogRead(PinU6)*3.3/1024);
    ValueU7 = float(analogRead(PinU7)*3.3/1024);
    ValueU8 = float(analogRead(PinU8)*3.3/1024);
}

void OledStandby(){//System Standby GUI
    u8g2.clearBuffer();
    u8g2.setFont(u8g2_font_ncenB08_tr);
    u8g2.drawStr(ResLeft-10,25,"System is Working");

    humi = HTS.readHumidity();
    u8g2.drawStr(ResLeft+5,60,"Humi:");
    u8g2.drawStr(ResLeft+50,60,Convert(humi).substr(0,2).c_str());
    u8g2.drawStr(ResLeft+70,60,"%");

}

void OledPrintSeneor(){//Show array sigal
  
  u8g2.clearBuffer();					// clear the internal memory
  u8g2.setFont(u8g2_font_ncenB08_tr);	// choose a suitable font

  u8g2.drawStr(NameLeft,25,"U3:");
  u8g2.drawStr(ResLeft,25,Convert(ValueU3).substr(0,6).c_str());

  u8g2.drawStr(NameRight,25,"U4:");
  u8g2.drawStr(ResRight,25,Convert(ValueU4).substr(0,6).c_str());

  u8g2.drawStr(NameLeft,40,"U5:");
  u8g2.drawStr(ResLeft,40,Convert(ValueU5).substr(0,6).c_str());

  u8g2.drawStr(NameRight,40,"U6:");
  u8g2.drawStr(ResRight,40,Convert(ValueU6).substr(0,6).c_str());

  u8g2.drawStr(NameLeft,55,"U7:");
  u8g2.drawStr(ResLeft,55,Convert(ValueU7).substr(0,6).c_str());

  u8g2.drawStr(NameRight,55,"U8:");
  u8g2.drawStr(ResRight,55,Convert(ValueU8).substr(0,6).c_str());

}

void OledPrintStream(){//show if BLE Connected
  u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
  u8g2.drawGlyph(15, 15, 64);	
  u8g2.drawGlyph(20, 15, 67);	
}

void OledPrintBLE(){//Show BLE LOGO
  BLEDevice central = BLE.central();
  if (central){
    OledPrintStream();
    digitalWrite(LED_BUILTIN, HIGH);
  }
  u8g2.setFont(u8g2_font_open_iconic_embedded_2x_t);
  u8g2.drawGlyph(0, 15 ,74);	
}

void OledPrintUsb(){//Show if serial Connected
  u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
  u8g2.drawGlyph(40, 15, 89);	
}

void OledPrintHeater(){ 
}

void OledPrintData(){

  if(oledMode){
      OledPrintSeneor();
  }else{
        OledStandby();
        }
}


void SendData(){//send data to serial & BLE
    Serial.print(" U3 Value = ");Serial.println(ValueU3);
    Serial.print(" U4 Value = ");Serial.println(ValueU4);
    Serial.print(" U5 Value = ");Serial.println(ValueU5);
    Serial.print(" U6 Value = ");Serial.println(ValueU6);
    Serial.print(" U7 Value = ");Serial.println(ValueU7);
    Serial.print(" U8 Value = ");Serial.println(ValueU8);
    Serial.print(" Humi = ");Serial.print(humi) ;Serial.println(" % ") ;

    SensorSignalHumi.writeValue(humi);
    SensorSignalU3.writeValue(ValueU3);
    SensorSignalU4.writeValue(ValueU4);
    SensorSignalU5.writeValue(ValueU5);
    SensorSignalU6.writeValue(ValueU6);
    SensorSignalU7.writeValue(ValueU7);
    SensorSignalU8.writeValue(ValueU8);


    u8g2.setFont(u8g2_font_open_iconic_arrow_1x_t);
    u8g2.drawGlyph(60, 15, 85);	
}

void SendSerialBuffer(){//Serial Communication Protocol with host
  if(bufferFlag){
    SendData();
    bufferFlag = !bufferFlag;
  }
}

void EventSW1(){//SW1 interrupt
   oledMode = !oledMode;
}

void EventSW2(){//SW2 interrupt
  //interrupt Enter cannot use 'Serial.println()'
  //interrupt must be simple , or Nrf52840 will crash 
   bufferFlag = 1;
}

void InitBle(){//INIT BLE SERVICES
  BLE.setDeviceName("SensorArraySystem");
  BLE.setLocalName("SensorArray");
  BLE.setAdvertisedService(SensorArray); 
  SensorArray.addCharacteristic(SensorSignalHumi);
  SensorArray.addCharacteristic(SensorSignalU3);
  SensorArray.addCharacteristic(SensorSignalU4);
  SensorArray.addCharacteristic(SensorSignalU5);
  SensorArray.addCharacteristic(SensorSignalU6);
  SensorArray.addCharacteristic(SensorSignalU7);
  SensorArray.addCharacteristic(SensorSignalU8);
  BLE.addService(SensorArray);
  BLE.advertise();
}

void setup() {
  u8g2.begin();
  Serial.begin(9600);
  HTS.begin();
  while (!BLE.begin()) {
  Serial.println("starting BLE failed!");
  }
  BLE.setDeviceName("SensorArraySystem");
  InitBle();
  attachInterrupt(buttonSW1, EventSW1, LOW);
  attachInterrupt(buttonSW2, EventSW2, LOW);
}

void loop() {
  BLEDevice central = BLE.central();
  readSensorValue();
  OledPrintData();
  OledPrintBLE();
  OledPrintUsb();
  SendSerialBuffer();
  //SendData();
  u8g2.sendBuffer();
  delay(500);
}

