// Riley Dawson
// Have fun!

#include <LiquidCrystal.h>
#include <avr/interrupt.h>
char currentCharTask[140];
String currentTask = String();
char inChar = -1;
byte index = 0;
LiquidCrystal lcd(12, 11, 5, 4, 3, 6);
const int switchPin = 2;
volatile boolean complete = false;
boolean hasTask = false;

// Setup arduino
void setup()
{
	pinMode(switchPin, INPUT);
	pinMode(13, HIGH);
	attachInterrupt(0, switchInterrupt, RISING);
	//conect to comp and wait for incomming message over
	Serial.begin(9600);
	lcd.begin(16, 2);
	lcd.setCursor(0, 1);
	lcd.clear();
	Serial.println("Arduino Ready");
}

void loop()
{
	//If current task has been completed, congratulate and update flags.
	if (complete){
		complete = false;
		lcd.clear();
		lcd.setCursor(0, 0);
		lcd.print("Task Complete!");
		
		hasTask = false;
		Serial.println("Task Complete");
		delay(3000);
	}
	//if no current message, wait for one
	if (!hasTask){
		lcd.clear();
		lcd.print("No current tasks!");
		// Get next task
		if (Serial.available()){
			lcd.clear();

			currentTask = Serial.readStringUntil('\n');
			delay(10);
			hasTask = true;
		}



	} else{
		int first = 0;
		int last = 0;
		int scrollC = 16;
		

		//String currentTask = String(currentCharTask);

		for (int i = 0; i < currentTask.length() + 15; i++){
			if (complete) break;
			lcd.setCursor(scrollC, 1);
			lcd.print(currentTask.substring(first, last));
			lcd.setCursor(0, 0);
			lcd.print("Current Task:");

			delay(300);
			lcd.clear();
			if (first == 0 && scrollC > 0){
				scrollC--;
				last++;
			}
			else if (last == currentTask.length() && scrollC == 0){
				first++;

			}
			else {
				first++;
				last++;
			}
		}
	}
	

	delay(30);

}

void switchInterrupt(){
	lcd.clear();
	complete = true;
}
