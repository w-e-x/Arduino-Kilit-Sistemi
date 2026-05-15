from flask import Flask, render_template_string, redirect, request, jsonify
import serial, time, threading, json, os, socket
from datetime import datetime

app = Flask(__name__)

# --- AYARLAR ---
COM_KILIT = 'COM5'  
COM_RFID = 'COM6'   
LOG_DOSYASI = "loglar.json"
KART_DOSYASI = "kartlar.json"

# --- RENKLİ TERMİNAL ÇIKTILARI ---
class Renk:
    YESIL = '\033[92m'
    KIRMIZI = '\033[91m'
    SARI = '\033[93m'
    MAVI = '\033[94m'
    PEMBE = '\033[95m'
    CYAN = '\033[96m'
    SIFIRLA = '\033[0m'

# --- VERİ YÖNETİMİ ---
def veri_yukle(dosya, varsayilan):
    if os.path.exists(dosya):
        try:
            with open(dosya, "r", encoding="utf-8") as f: return json.load(f)
        except: return varsayilan
    return varsayilan

def veri_kaydet(dosya, veri):
    with open(dosya, "w", encoding="utf-8") as f: json.dump(veri, f, indent=4)

yetkili_kartlar = veri_yukle(KART_DOSYASI, {})
son_bilinmeyen_kart = ""

def log_kaydet(kaynak, durum="normal"):
    loglar = veri_yukle(LOG_DOSYASI, [])
    simdi = datetime.now()
    yeni = {
        "tarih": simdi.strftime("%d.%m.%Y"), 
        "saat": simdi.strftime("%H:%M:%S"), 
        "kaynak": kaynak,
        "durum": durum 
    }
    loglar.insert(0, yeni)
    veri_kaydet(LOG_DOSYASI, loglar[:50])
    
    saat_str = simdi.strftime("%H:%M:%S")
    if durum == "success": print(f"{Renk.YESIL}[{saat_str}] 🟢 KİLİT AÇILDI -> {kaynak}{Renk.SIFIRLA}")
    elif durum == "error": print(f"{Renk.KIRMIZI}[{saat_str}] 🔴 GÜVENLİK İHLALİ -> {kaynak}{Renk.SIFIRLA}")
    else: print(f"{Renk.SARI}[{saat_str}] ℹ️ BİLGİ -> {kaynak}{Renk.SIFIRLA}")

# --- TERMİNAL İMZASI VE EKİP BİLGİLERİ ---
def print_dev_info():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try: s.connect(('8.8.8.8', 1)); ip = s.getsockname()[0]
    except: ip = "127.0.0.1"
    finally: s.close()
    
    print("\n" + Renk.CYAN + "="*65)
    print("   ███████╗██╗███████╗████████╗███████╗███╗   ███╗")
    print("   ██╔════╝██║██╔════╝╚══██╔══╝██╔════╝████╗ ████║")
    print("   ███████╗██║███████╗   ██║   █████╗  ██╔████╔██║")
    print("   ╚════██║██║╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║")
    print("   ███████║██║███████║   ██║   ███████╗██║ ╚═╝ ██║")
    print("   ╚══════╝╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝")
    print("="*65)
    print(" 🚀 AKILLI KİLİT SİSTEMİ ÇEVRİMİÇİ")
    print(f" 💻 {Renk.PEMBE}Geliştirici Ekip:{Renk.CYAN}")
    print("    - Şeyda Nur Demirkol")
    print("    - Umut Dirlik")
    print("    - Kayra Miraç Daşdan")
    print("-" * 65)
    print(f" 🔗 LOCAL HOST : http://localhost:5000")
    print(f" 📱 NETWORK IP : http://{ip}:5000")
    print("="*65 + Renk.SIFIRLA + "\n")

print_dev_info()

# --- ARDUINO BAĞLANTILARI ---
try: 
    ser_kilit = serial.Serial(COM_KILIT, 9600, timeout=1)
    print(f"{Renk.YESIL}[OK] Kilit Bağlandı ({COM_KILIT}){Renk.SIFIRLA}")
except: 
    ser_kilit = None; print(f"{Renk.KIRMIZI}[!] Kilit Bağlanamadı ({COM_KILIT}){Renk.SIFIRLA}")

try: 
    ser_rfid = serial.Serial(COM_RFID, 9600, timeout=1)
    print(f"{Renk.YESIL}[OK] RFID Bağlandı ({COM_RFID}){Renk.SIFIRLA}")
except: 
    ser_rfid = None; print(f"{Renk.KIRMIZI}[!] RFID Bağlanamadı ({COM_RFID}){Renk.SIFIRLA}")

def dinle():
    global son_bilinmeyen_kart
    while True:
        if ser_rfid and ser_rfid.in_waiting > 0:
            uid = ser_rfid.readline().decode('utf-8', errors='ignore').strip().upper()
            if uid and "READY" not in uid:
                if uid in yetkili_kartlar:
                    if ser_kilit: ser_kilit.write(b'A')
                    log_kaydet(f"RFID Onay: {yetkili_kartlar[uid]}", "success")
                    son_bilinmeyen_kart = ""
                else:
                    son_bilinmeyen_kart = uid
                    log_kaydet(f"Yetkisiz Kart! ID: {uid}", "error")
        
        if ser_kilit and ser_kilit.in_waiting > 0:
            msg = ser_kilit.readline().decode('utf-8', errors='ignore').strip()
            if msg == "KEYPAD_OK": log_kaydet("Şifre Paneli (Doğru)", "success")
            if msg == "KEYPAD_FAIL": log_kaydet("Şifre Paneli (Hatalı!)", "error")
        time.sleep(0.05)

threading.Thread(target=dinle, daemon=True).start()

# --- MODERN WEB ARAYÜZÜ ---
HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>w3x Dashboard</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@500;600;700&family=Permanent+Marker&display=swap');
        :root { --bg-color: #0b0f19; --panel-bg: #151b2b; --primary: #00ffcc; --danger: #ff3366; --text-main: #e2e8f0; --text-muted: #94a3b8; }
        body { margin: 0; padding: 20px; background-color: var(--bg-color); color: var(--text-main); font-family: 'Rajdhani', sans-serif; }
        .container { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 25px; }
        .header-title { text-align: center; font-family: 'Orbitron', sans-serif; font-size: 2.5em; letter-spacing: 2px; margin-bottom: 40px; }
        .header-title span { color: var(--primary); }
        .card { background: var(--panel-bg); padding: 30px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); position: relative; overflow: hidden; }
        .card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: linear-gradient(90deg, var(--primary), #ff00ff); }
        h2 { font-family: 'Orbitron', sans-serif; color: var(--primary); font-size: 1.2em; margin-top: 0; margin-bottom: 25px; }
        .btn-unlock { background: rgba(0, 255, 204, 0.1); border: 2px solid var(--primary); color: var(--primary); width: 100%; padding: 20px; font-family: 'Orbitron', sans-serif; font-weight: bold; font-size: 1.5em; cursor: pointer; border-radius: 12px; transition: all 0.3s; }
        .btn-unlock:hover { background: var(--primary); color: #000; box-shadow: 0 0 20px rgba(0,255,204,0.4); }
        .form-group { display: flex; gap: 10px; margin-bottom: 20px; }
        .inp { flex: 1; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); color: white; padding: 12px 15px; border-radius: 8px; font-family: 'Orbitron', sans-serif; }
        .btn-add { background: var(--primary); color: #000; border: none; padding: 0 25px; border-radius: 8px; font-weight: bold; font-family: 'Orbitron', sans-serif; cursor: pointer; }
        table { width: 100%; border-collapse: separate; border-spacing: 0 8px; }
        th { color: var(--text-muted); font-size: 0.85em; text-transform: uppercase; text-align: left; padding: 0 10px 5px 10px; }
        td { background: rgba(0,0,0,0.2); padding: 12px 10px; font-size: 0.95em; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
        .badge-success { background: rgba(0,255,204,0.1); color: var(--primary); border: 1px solid var(--primary); }
        .badge-error { background: rgba(255,51,102,0.1); color: var(--danger); border: 1px solid var(--danger); }
        .badge-info { background: rgba(255,255,255,0.05); color: var(--text-muted); }
        .btn-del { color: var(--danger); text-decoration: none; font-weight: bold; padding: 5px 10px; background: rgba(255,51,102,0.1); border-radius: 5px; }
        .signature-container { text-align: center; margin-top: 50px; padding-bottom: 30px; }
        .signature { font-family: 'Permanent Marker', cursive; font-size: 2.5em; color: #ff00ff; text-shadow: 0 0 10px #ff00ff; transform: rotate(-2deg); margin-bottom: 10px; }
        .dev-team { color: var(--text-muted); font-size: 1em; letter-spacing: 1px; display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; }
        .dev-team span { background: rgba(255,255,255,0.05); padding: 8px 15px; border-radius: 8px; }
    </style>
</head>
<body>
    <h1 class="header-title">SYSTEM <span>CORE</span></h1>
    <div class="container">
        <div class="card">
            <h2>KİLİT KONTROLÜ</h2>
            <button class="btn-unlock" onclick="fetch('/ac', {method:'POST'})">KİLİDİ AÇ</button>
        </div>
        <div class="card">
            <h2>KART YÖNETİMİ</h2>
            <form action="/kart_ekle" method="post" class="form-group">
                <input type="text" name="uid" id="uid-input" class="inp" placeholder="Kart ID" required>
                <input type="text" name="isim" class="inp" placeholder="Kullanıcı" required>
                <button type="submit" class="btn-add">+</button>
            </form>
            <table id="kart-tablosu"></table>
        </div>
        <div class="card" style="grid-column: 1 / -1;">
            <h2>CANLI SİSTEM LOGLARI</h2>
            <table id="log-tablosu"></table>
        </div>
    </div>

    <div class="signature-container">
        <div class="signature">w3x was here</div>
        <div class="dev-team">
            <span>💻 Şeyda Nur Demirkol</span>
            <span>🚀 Umut Dirlik</span>
            <span>🛠️ Kayra Miraç Daşdan</span>
        </div>
    </div>

    <script>
        function verileriGuncelle() {
            fetch('/api/veri').then(res => res.json()).then(data => {
                let logHtml = '<tr><th>Zaman</th><th>Olay Kaynağı</th><th>Durum</th></tr>';
                data.loglar.slice(0, 8).forEach(log => {
                    let bc = log.durum === 'success' ? 'badge-success' : (log.durum === 'error' ? 'badge-error' : 'badge-info');
                    let dt = log.durum === 'success' ? 'ONAY' : (log.durum === 'error' ? 'İHLAL' : 'BİLGİ');
                    logHtml += `<tr><td>${log.saat}</td><td>${log.kaynak}</td><td><span class="badge ${bc}">${dt}</span></td></tr>`;
                });
                document.getElementById('log-tablosu').innerHTML = logHtml;

                let kartHtml = '<tr><th>Kullanıcı</th><th>ID</th><th style="text-align:right;">İşlem</th></tr>';
                for (const [uid, isim] of Object.entries(data.kartlar)) {
                    kartHtml += `<tr><td>${isim}</td><td>${uid}</td><td style="text-align: right;"><a href="/sil/${uid}" class="btn-del">SİL</a></td></tr>`;
                }
                document.getElementById('kart-tablosu').innerHTML = kartHtml;

                let uidInput = document.getElementById('uid-input');
                if (data.son_okunan && data.son_okunan !== uidInput.value) {
                    uidInput.value = data.son_okunan;
                }
            });
        }
        setInterval(verileriGuncelle, 1000); verileriGuncelle();
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/api/veri')
def veri_api(): return jsonify({"kartlar": yetkili_kartlar, "loglar": veri_yukle(LOG_DOSYASI, []), "son_okunan": son_bilinmeyen_kart})

@app.route('/ac', methods=['POST'])
def ac():
    if ser_kilit: ser_kilit.write(b'A'); log_kaydet("Web Panel", "success"); return "OK"
    return "HATA"

@app.route('/kart_ekle', methods=['POST'])
def ekle():
    uid, isim = request.form.get('uid').strip().upper(), request.form.get('isim').strip()
    if uid and isim: yetkili_kartlar[uid] = isim; veri_kaydet(KART_DOSYASI, yetkili_kartlar); log_kaydet(f"Kart Eklendi: {isim}")
    return redirect('/')

@app.route('/sil/<uid>')
def sil(uid):
    if uid in yetkili_kartlar: del yetkili_kartlar[uid]; veri_kaydet(KART_DOSYASI, yetkili_kartlar); log_kaydet(f"Kart Silindi")
    return redirect('/')

if __name__ == '__main__':
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=5000)
