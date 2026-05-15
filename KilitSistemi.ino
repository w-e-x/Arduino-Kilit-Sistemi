/*
 * CyberLock v1.0 - Kilit Kontrol Ünitesi
 * Geliştirici Ekip: Şeyda Nur Demirkol, Umut Dirlik, Kayra Miraç Daşdan
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Keypad.h>
#include <Servo.h> 

LiquidCrystal_I2C lcd(0x27, 16, 2);

// Keypad Ayarları
const byte ROWS = 4;
const byte COLS = 3;
char keys[ROWS][COLS] = {
  {'1','2','3'}, {'4','5','6'}, {'7','8','9'}, {'*','0','#'}
};
byte rowPins[ROWS] = {2,3,4,5};
byte colPins[COLS] = {6,7,8}; 

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);
Servo kilitServosu;

// Donanım Pinleri
const int servoPin = 9; 
const int buzzerPin = 12; 

// Ayarlar
String anaSifre = "3636"; 
String girilenSifre = "";

void setup() {
  Serial.begin(9600);
  pinMode(buzzerPin, OUTPUT);
  kilitServosu.attach(servoPin);
  
  kilitKapat(); 
  
  lcd.init();
  lcd.backlight();
  lcd.print("Sistem Aktif");
  delay(1000);
  lcd.clear();
  lcd.print("Sifre Girin:");
}

void kilitAc() {
  kilitServosu.writeMicroseconds(2000); // Açık pozisyon
  tone(buzzerPin, 2000, 500); 
}

void kilitKapat() {
  kilitServosu.writeMicroseconds(1000); // Kapalı pozisyon
}

void loop() {
  // Python'dan gelen komutu dinle (RFID veya Web için)
  if (Serial.available() > 0) {
    char komut = Serial.read();
    if (komut == 'A' || komut == 'a') {
      lcd.clear(); lcd.print("Erisim Onaylandi");
      kilitAc(); delay(3000); kilitKapat();
      lcd.clear(); lcd.print("Sifre Girin:");
    }
  }

  char key = keypad.getKey();
  if (key) {
    tone(buzzerPin, 1000, 50);
    if (key == '*') { 
      girilenSifre = ""; 
      lcd.clear(); lcd.print("Sifre Girin:"); 
      return; 
    }
    if (key == '#') {
      if (girilenSifre == anaSifre) {
        lcd.clear(); lcd.print("Dogru Sifre");
        Serial.println("KEYPAD_OK");
        kilitAc(); delay(3000); kilitKapat();
      } else {
        Serial.println("KEYPAD_FAIL");
        lcd.clear(); lcd.print("HATALI SIFRE!"); delay(1500);
      }
      girilenSifre = ""; lcd.clear(); lcd.print("Sifre Girin:");
      return;
    }
    if (girilenSifre.length() < 4) {
      girilenSifre += key;
      lcd.setCursor(girilenSifre.length()-1, 1); lcd.print("*");
    }
  }
}
