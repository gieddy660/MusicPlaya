#include <Arduino.h>
#include <LiquidCrystal.h>

#define PTS 2  //Pulse to Senconds ratio
#define START 1
#define END_TITLE 3
#define PULSE 6

LiquidCrystal lcd(2, 3, 8, 9, 10, 11);

String title = String("waiting");
unsigned long long tot_pulses = 0;
unsigned long long current_pulses = 0;

unsigned char tot_seconds = 0, tot_minutes = 0, tot_hours = 0;
unsigned char current_seconds = 0, current_minutes = 0, current_hours = 0;

void setup() {
	lcd.begin(16, 2);
	lcd.clear();
	Serial.begin(115200);
}

void loop() {
	if(Serial.available()){
		unsigned char i = Serial.read();

		if(i == START){
			title.remove(0, title.length());
			tot_pulses = 0;
			current_pulses = 0;
			current_hours = 0;
			current_minutes = 0;
			current_seconds = 0;
			while((i = Serial.read()) != END_TITLE){
				title += (char) i;
			}
			do {
				i = Serial.read();
				tot_pulses <<= 7;
				tot_pulses |= i & 0b01111111;
			} while((i & 0b10000000) == 0);

			tot_hours = (tot_pulses / PTS) / 3600;
			tot_minutes = ((tot_pulses / PTS) / 60) % 60;
			tot_seconds = (tot_pulses / PTS) % 60;
			lcd.clear();
		}
		else if(i == PULSE){
			++current_pulses;
			if(current_pulses == PTS){
				current_pulses = 0;
				++current_seconds;
				if(current_seconds == 60){
					current_seconds = 0;
					++current_minutes;
					if(current_minutes == 60){
						current_minutes = 0;
						++current_hours;
					}
				}
			}
		}
	}
	lcd.setCursor(0, 0);
	lcd.print(title);
	lcd.setCursor(0, 1);
	char buffer[35];
	if(tot_hours > 0){
		sprintf(buffer, "%d:%02d:%02d|%d:%02d:%02d", current_hours, current_minutes, current_seconds, tot_hours, tot_minutes, tot_seconds);
	}else if(tot_minutes > 9){
		sprintf(buffer, "%02d:%02d|%02d:%02d", current_minutes, current_seconds, tot_minutes, tot_seconds);
	}else{
		sprintf(buffer, "%d:%02d|%d:%02d", current_minutes, current_seconds, tot_minutes, tot_seconds);
	}
	lcd.print(buffer);
}
