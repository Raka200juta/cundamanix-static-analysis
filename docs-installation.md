# Documentation Installation Cundamanix Static Analysis

# Cundamanix Static Analysis

Dokumentasi Instalasi & Konfigurasi Service

Repository ini berisi aplikasi *Cundamanix Static Analysis* beserta panduan untuk melakukan instalasi, konfigurasi virtual environment, dan menjalankannya sebagai service menggunakan **systemd**.

---

## 📌 1. Clone Repository

```bash
git clone -b master https://github.com/Raka200juta/cundamanix-static-analysis.git
cd cundamanix-static-analysis/src
```

---

## 📌 2. Membuat Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 📌 3. Install Dependencies

```bash
pip3 install -r requirements.txt
```

---

## 📌 4. Berikan Izin Eksekusi pada Entrypoint Script

```bash
chmod +x scripts/entrypoint.sh
```

---

## 📌 5. Membuat Service systemd

Edit atau buat service baru:

```bash
sudo nano /etc/systemd/system/cundamanix.service
```

Isi dengan konfigurasi berikut:

```
[Unit]
Description=Cundamanix Static Analysis Web Server
After=network.target

[Service]
User=me
Group=me
WorkingDirectory=/home/me/Documents/digital-forensics-v2/cundamanix-static-analysis/src
Environment="PATH=/home/me/Documents/digital-forensics-v2/cundamanix-static-analysis/src/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/me/Documents/digital-forensics-v2/cundamanix-static-analysis/src/scripts/entrypoint.sh

Restart=always
RestartSec=5

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

> Pastikan nilai User, Group, WorkingDirectory, PATH, dan ExecStart sudah sesuai dengan lokasi instalasi Anda.
> 

---

## 📌 6. Reload systemd & Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl daemon-reexec
sudo systemctl enable cundamanix.service
```

---

## 📌 7. Menjalankan Service

```bash
sudo systemctl start cundamanix.service
```

---

## 📌 8. Mengecek Status Service

```bash
sudo systemctl status cundamanix.service
```

---

## 📌 9. Log Service (Opsional)

Melihat log aplikasi via journalctl:

```bash
sudo journalctl -u cundamanix.service -f
```

---
