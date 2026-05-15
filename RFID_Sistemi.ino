/*
 * CyberLock v1.0 - RFID Okuyucu Ünitesi
 * Geliştirici Ekip: Şeyda Nur Demirkol , Umut Dirlik, Kayra Miraç Daşdan
 */

#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN 5          
#define SS_PIN 4         

MFRC522 mfrc522(SS_PIN, RST_PIN);  

void setup() {
  Serial.begin(9600); 
  SPI.begin(); 
  mfrc522.PCD_Init();
  mfrc522.PCD_SetAntennaGain(mfrc522.RxGain_max); 
  Serial.println("RFID_READY");
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) return;

  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    uid += (mfrc522.uid.uidByte[i] < 0x10 ? "0" : "") + String(mfrc522.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  Serial.println(uid); 

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
  delay(1000); // Okuma sonrası stabilizasyon beklemesi
  mfrc522.PCD_Init(); // Sensörü yeniden başlat (Donma koruması)
}
