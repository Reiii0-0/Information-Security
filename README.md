# Simulasi Komunikasi Aman DES (Peer-to-Peer)

Proyek ini adalah simulasi transmisi ciphertext P2P menggunakan algoritma Data Encryption Standard (DES) Murni tanpa library eksternal. Dibuat untuk memenuhi tugas Keamanan Informasi.

## 🚀 Fitur Utama
- **Algoritma DES Manual:** Semua proses *Key Schedule*, *S-Box*, *Feistel Network*, dan *PKCS7 Padding* diimplementasikan secara manual.
- **Transmisi Jaringan Nyata:** Menggunakan protokol TCP/IP murni.
- **Asinkron & Full-Duplex:** Mampu mengirim dan menerima pesan secara bersamaan dengan bantuan `threading`.
- **Dukungan Unicode & Emoji:** Pesan dienkripsi di level byte sehingga mendukung karakter UTF-8.
- **Arsitektur Multi-Role:** Bisa bertindak sebagai Host maupun Client hanya dengan satu file eksekusi.

## 📂 Struktur File
- `des_manual.py` - Core Engine DES (S-Box, IP, PC-1, PC-2, Feistel)
- `des_utils.py` - Fungsi pembantu untuk konversi bit dan *padding*
- `chat_node.py` - Aplikasi antarmuka chatting P2P via Terminal
- `docker-compose.yml` - Konfigurasi virtualisasi untuk simulasi antar VM
- `Dockerfile` - Basis *image* sistem

## 🛠️ Cara Menggunakan (Mode Multi-Role Docker)
1. **Jalankan Tuan Rumah (Host):**
   ```bash
   docker compose up -d
   docker exec -it ki_jane_doe python chat_node.py
   # Pilih Host, tekan Enter pada Port
   ```
2. **Jalankan Tamu (Client):**
   ```bash
   docker exec -it ki_john_doe python chat_node.py
   # Pilih Client, masukkan IP 172.20.0.10, tekan Enter pada Port
   ```

3. Masukkan 8-karakter Kunci Rahasia dan mulailah bertukar pesan terenkripsi yang aman dari penyadap!

## 📱 Cara Menggunakan (Mode Termux Android)
Untuk mensimulasikan koneksi dua perangkat fisik murni, Anda bisa menjalankan *client* atau *host* dari aplikasi Termux di HP Android Anda.
Repositori ini sudah dilengkapi dengan _script_ instalasi mandiri untuk Termux.

1. **Jalankan Instalasi dan Aplikasi:**
   Pindahkan *source code* ini ke memori internal HP Anda. Buka Termux, masuk ke folder kode ini berada, lalu eksekusi *script* berikut:
   ```bash
   chmod +x termux_setup.sh
   ./termux_setup.sh
   ```
   *(Script ini akan mengecek instalasi Python secara otomatis, menginstalnya jika belum ada, dan langsung menjalankan aplikasi).*
2. **Koneksikan dengan Laptop:**
   Pilih peran yang Anda inginkan (misal **client**). Masukkan IP *Wireless/WiFi* dari Laptop Anda. Anda sekarang terhubung secara fisik (dua *device* berbeda) melalui jaringan WiFi!
