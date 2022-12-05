//Author: Logan Foreman
//RedID: 825056655

#include <LiquidCrystal.h>
LiquidCrystal lcd(7,8,9,10,11,12);


int x;
String msg;
int lineNumber = 1;
int cursor = 0;

void setup() {
  Serial.begin(115200); // Connects to python with baud rate of 115200
  lcd.begin(16,2); // This sets up the LCD screen format of 16*2
}


// Loop function will receive communication from python script
// data is brought in one long string so that its easy
// for the arduino for it to read.

// The C++ code can also parse some of it for purposes of 
// formatting onto the LCD screen

void loop() {

  if (Serial.available() > 0){
    msg = Serial.readString(); //data encoded in utf-8 (must have)
    String SpotName;
    String SpotSummary;
    int str_size = msg.length();
    int saveInd = 0;
// This loop will get the spot's name from the given string 
    for(int i = 0; i < str_size; i++){
     SpotName.concat(msg[i]);
      if(msg[i] == ' ') {
        saveInd = i;
        break;
      }
    }

// Prints spot name at top of LCD screen
    lcd.setCursor(3,0);
    lcd.print(SpotName);

// Gets spot's summary from given string 
    for(int i = saveInd; i < str_size; i++){
      SpotSummary.concat(msg[i]);
    }

// All of the following loops are for 
// managing the scrolling text effect
// for the given string:
    if(SpotSummary.length() >6){
      for(int i=16; i>=0; i--){ //16 positions on screen to fill
        lcd.clear();
        lcd.setCursor(3,0);
        lcd.print(SpotName);
        lcd.setCursor(i,1);
        lcd.print(SpotSummary);
        delay(250);
    }
    }else{
      lcd.clear();
        lcd.setCursor(3,0);
        lcd.print(SpotName);
        lcd.setCursor(0,1);
        lcd.print(SpotSummary);
    }
    delay(1500);
    int sizeMark = 0;
    sizeMark = SpotSummary.substring(1,2).toInt();
   delay(4000);
    if(sizeMark >=1 && sizeMark<=2){
      lcd.clear();
        lcd.setCursor(3,0);
        lcd.print(SpotName);
        lcd.setCursor(0,1);
        lcd.print("Too small!!");
        delay(1250);
        lcd.clear();
        lcd.setCursor(3,0);
        lcd.print(SpotName);
        lcd.setCursor(0,1);
        lcd.print("Not worth it.");
    }
    else if(sizeMark>2 && sizeMark <5){
      lcd.clear();
        lcd.setCursor(3,0);
        lcd.print(SpotName);
        lcd.setCursor(0,1);
        lcd.print("Not Bad.");
        delay(1250);
        lcd.clear();
        lcd.setCursor(3,0);
        lcd.print(SpotName);
        lcd.setCursor(0,1);
        lcd.print("Go Surf!");
    }
    else if(sizeMark>=6 && sizeMark<=8){
        for(int i=15; i>=-10; i--){ //16 positions on screen to fill, i
        lcd.clear();
        lcd.setCursor(3,0);
        lcd.print(SpotName);
        lcd.setCursor(i,1);
        lcd.print("OMG Its big out, go surf!!!!!!");
        delay(250);
    }
    }
    else if(sizeMark>=9){
        for(int i=16; i>=-18; i--){ //16 positions on screen to fill, i
        lcd.clear();
        lcd.setCursor(3,0);
        lcd.print(SpotName);
        lcd.setCursor(i,1);
        lcd.print("Woah! Better bring a friend, its huge out!");
        delay(250);
    }
    }
  }
}
