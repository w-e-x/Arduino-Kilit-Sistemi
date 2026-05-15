# 🛡️  Akıllı Kilit ve Yönetim Sistemi

**CyberLock**, Arduino tabanlı donanım kontrolünü, Flask tabanlı modern bir web arayüzü ile birleştiren çift katmanlı bir IoT güvenlik projesidir. Sistem; RFID kart, şifre paneli (Keypad) ve lokal ağ (Web Dashboard) üzerinden kapı/kilit yönetimi sağlar.

## 🚀 Öne Çıkan Özellikler
* **Çoklu Giriş Yöntemi:** RFID Kart, 4 haneli şifre veya Web Arayüzü ile tetikleme.
* **Canlı Log ve Güvenlik Uyarıları:** Tüm onaylı ve yetkisiz giriş denemeleri anlık olarak panele ve terminale düşer.
* **Dinamik Kart Yönetimi:** Yeni kartları web arayüzünden veritabanına ekleme ve silme.
* **Yerel Ağ Bağlantısı:** Ev/Ofis Wi-Fi ağı üzerinden telefon, tablet veya PC ile kontrol imkanı.
* **Anti-Donma Koruması:** RFID modüllerinde sık yaşanan okuma tıkanmalarına karşı yazılımsal *Hard-Reset* algoritması.

---

## 👨‍💻 Geliştirici Ekip & Katkıda Bulunanlar

Bu proje, donanım mimarisi ve yazılım entegrasyonu alanında aşağıdaki geliştiriciler tarafından hazırlanmıştır:


* **Umut Dirlik** - *Hardware Integration & UI/UX* | [LinkedIn Profiline Git](https://www.linkedin.com/in/umut-dirlik-9053aa321/)
* **Kayra Miraç Daşdan** - *Core Algorithms & Testing* | [LinkedIn Profiline Git](https://www.linkedin.com/in/kayra-mira%C3%A7-da%C5%9Fdan-25a57338b/)

---

## 🛠️ Donanım Mimarisi ve Devre Şeması

Sistem iki ayrı Arduino Uno modülünün Python ana sunucusu ile asenkron haberleşmesi mantığına dayanır.

### Kilit & Keypad Ünitesi (COM5)
* **Servo Motor (Kilit):** D9
* **Buzzer:** D12
* **I2C LCD:** A4 (SDA), A5 (SCL)
* **4x3 Keypad:** D2, D3, D4, D5 (Satırlar) | D6, D7, D8 (Sütunlar)

### RFID Okuyucu Ünitesi (COM6)
* **MFRC522 (SDA/SS):** D4 
* **MFRC522 (RST):** D5 
* **SPI Pinleri:** D11 (MOSI), D12 (MISO), D13 (SCK)

---

## 💻 Kurulum ve Çalıştırma

**1.** Proje dosyalarını bilgisayarınıza indirin.
**2.** Arduino kodlarını (`KilitSistemi.ino` ve `RFID_Sistemi.ino`) ilgili Arduino kartlarına yükleyin.
**3.** Terminali açarak gerekli Python kütüphanelerini kurun:

    pip install flask pyserial

**4.** Sistemi başlatın:

    python anasistem.py

**5.** Terminalde beliren **Local Host** veya **Network IP** adresini tarayıcınıza yapıştırarak kontrol paneline ulaşın.
