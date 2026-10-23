# 🚀 PANDUAN DEMO SUPER LENGKAP (TINGGAL COPY-PASTE)

Panduan ini disiapkan agar saat demo dengan asisten/dosen, kamu tidak perlu mikir lagi. Tinggal *copy-paste* perintah-perintah di bawah ini ke terminalmu sesuai skenario yang ingin didemokan. Semua skenario ini sah dan memenuhi syarat "dua device / dua IP berbeda".

**Persiapan Awal (Wajib untuk semua skenario):**
Buka terminal di Laptop, lalu masuk ke folder project:
```bash
cd "Tugas/1"
```

---

## 🟢 SKENARIO 1: DOCKER 🐳 ke DOCKER 🐳 (Paling Gampang & Rapi)
Skenario ini menggunakan dua buah virtual container (`jane_doe` dan `john_doe`) yang memiliki IP berbeda (`172.20.0.10` dan `172.20.0.11`).

**Langkah 1: Nyalakan semua container**
*Copy-paste ini di Terminal 1:*
```bash
docker compose up -d
```

**Langkah 2: Buka Terminal Host (Jane Doe - 172.20.0.10)**
*Copy-paste ini di Terminal 1:*
```bash
docker exec -it ki_jane_doe python chat_node.py
```
* Input Peran: `host`
* Input Port: `5000` (Tekan Enter saja)
* Input Secret Key: `password` (Tekan Enter)

**Langkah 3: Buka Terminal Client (John Doe - 172.20.0.11)**
Buka Terminal baru (Terminal 2), masuk ke folder `1`, lalu paste ini:
```bash
docker exec -it ki_john_doe python chat_node.py
```
* Input Peran: `client`
* Input IP Host: `172.20.0.10`
* Input Port: `5000` (Tekan Enter saja)
* Input Secret Key: `password` (Harus persis sama dengan Host)

---

## 🟡 SKENARIO 2: LAPTOP 💻 ke DOCKER 🐳
Skenario ini membuktikan laptop kamu (OS asli) bisa berkomunikasi dengan Docker (virtual OS) seolah mereka dua perangkat berbeda. Laptop bertindak sebagai Client, Docker bertindak sebagai Host.

**Langkah 1: Buka Terminal Host (Docker - Jane Doe - 172.20.0.10)**
*Copy-paste ini di Terminal 1:*
```bash
docker compose up -d
docker exec -it ki_jane_doe python chat_node.py
```
* Input Peran: `host`
* Input Port: `5000`
* Input Secret Key: `rahasia1`

**Langkah 2: Buka Terminal Client (Laptop Asli)**
Buka Terminal baru (Terminal 2), pastikan kamu sudah di dalam folder `1`. Paste ini:
```bash
python chat_node.py
```
* Input Peran: `client`
* Input IP Host: `172.20.0.10`
* Input Port: `5000`
* Input Secret Key: `rahasia1`

---

## 🔴 SKENARIO 3: TERMUX ANDROID 📱 ke LAPTOP 💻 (Paling Realistis!)
Ini adalah demo tingkat dewa karena menggunakan dua perangkat fisik murni yang dihubungkan lewat jaringan WiFi.

**Persiapan Tambahan:**
Pastikan HP dan Laptop terhubung ke WiFi yang sama (atau nyalakan hotspot dari HP ke Laptop). 

**Langkah 1: Cek IP Laptop Kamu**
Di terminal laptop, ketik:
```bash
ip a
```
*(Cari alamat IP yang berawalan `192.168.x.x` atau `10.x.x.x` di bagian koneksi wireless/WiFi. Catat IP ini, misal: `192.168.1.15`)*

**Langkah 2: Buka Terminal Host (Laptop Asli)**
Di terminal laptop, jalankan:
```bash
python chat_node.py
```
* Input Peran: `host`
* Input Port: `5000`
* Input Secret Key: `keamanan`

**Langkah 3: Buka Terminal Client (Termux HP)**
Buka Termux di HP, masuk ke folder tempat *source code* disimpan, lalu paste ini:
```bash
chmod +x termux_setup.sh
./termux_setup.sh
```
* Input Peran: `client`
* Input IP Host: **[Masukkan IP Laptop yang kamu catat di Langkah 1]** (Contoh: `192.168.1.15`)
* Input Port: `5000`
* Input Secret Key: `keamanan`

---

## 🕵️‍♂️ TIPS TAMBAHAN: PEMBUKTIAN WIRESHARK (EKSTRA POIN!)
Asisten meminta pembuktian Wireshark? Gampang! Tunjukkan ini ke mereka:

1. Buka aplikasi **Wireshark** di Laptop.
2. Saat disuruh memilih *Network Interface*:
   - Jika pakai **Skenario 1 atau 2** (Docker): Pilih interface bernama `br-xxx` atau `docker0`.
   - Jika pakai **Skenario 3** (Termux): Pilih interface Wi-Fi (biasanya `wlan0` atau nama WiFi kamu).
3. Di kolom pencarian / *filter* di bagian atas, **copy-paste** salah satu kode di bawah ini lalu tekan Enter:

   **Filter untuk Docker (Skenario 1 & 2):**
   ```text
   ip.addr == 172.20.0.10 and tcp.port == 5000
   ```
   **Filter untuk Termux (Skenario 3):**
   ```text
   ip.addr == [Masukkan_IP_HP_Kamu] and tcp.port == 5000
   ```

4. Ketik pesan chat dan tekan enter.
5. Tunjukkan ke asisten baris data TCP yang muncul di Wireshark. Klik kanan baris tersebut -> Pilih **Follow** -> **TCP Stream**.
6. **BAM!** Di layar akan muncul rentetan karakter aneh (Hexadecimal). Bilang ke asisten: 
   *"Bisa dilihat Kak, data yang lewat di jaringan murni berbentuk ciphertext hasil enkripsi algoritma DES manual kami, tidak ada *plain text* sama sekali yang bocor."*
