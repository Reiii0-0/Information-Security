# 📖 Penjelasan Detail Source Code DES & Socket (Line by Line)

Dokumen ini disusun untuk membantu Anda memahami alur kerja kode dari awal sampai akhir, sehingga Anda sangat siap jika ditanya oleh dosen/asisten saat sesi demo tugas.

---

## 1. Penjelasan `des_utils.py` (Fungsi Bantuan)
File ini berisi fungsi-fungsi dasar untuk mengelola konversi data antara string, hexadecimal, bytes, dan biner (0 dan 1).

* **`hex2bin(s)` & `bin2hex(s)`**: 
  Fungsi ini mengubah teks hexadecimal (contoh: `A1`) menjadi biner (`10100001`), dan sebaliknya. Fungsi `zfill` digunakan untuk memastikan panjang binernya tetap utuh meski ada angka nol di depan (tidak terpotong).
* **`bytes2bin(b)` & `bin2bytes(s)`**: 
  Mengubah data bertipe *bytes* menjadi deretan string biner (`0` dan `1`). Ini penting karena enkripsi DES beroperasi pada level bit/biner.
* **`xor(a, b)`**: 
  Operasi XOR bit-by-bit. Jika bit sama (`1` dan `1`, atau `0` dan `0`), hasilnya `0`. Jika beda, hasilnya `1`. Ini adalah jantung dari jaringan Feistel di DES.
* **`pad(data_bytes)` & `unpad(data_bytes)`**: 
  Implementasi standar algoritma **PKCS7 Padding**. Karena DES memproses data per blok (8 bytes), jika pesan Anda panjangnya 10 bytes, maka akan kurang 6 bytes untuk menjadi 2 blok penuh (16 bytes). `pad()` akan menambahkan sisa 6 byte tersebut, dengan nilai masing-masing `06`. Fungsi `unpad()` bertugas membuang karakter tambahan ini saat pesan berhasil didekripsi.

---

## 2. Penjelasan `des_manual.py` (Inti Algoritma)
Ini adalah tempat dimana enkripsi Data Encryption Standard (DES) manual Anda berjalan.

### Tabel-tabel Konstanta (Line 3 - 109)
* **`IP` (Initial Permutation) & `IP_INV`**: Tabel ini hanya bertugas mengacak urutan bit di awal dan di akhir proses enkripsi agar strukturnya lebih sulit ditebak.
* **`E` (Expansion) & `P` (Permutation)**: Digunakan di dalam fungsi Feistel. `E` melebarkan data 32-bit menjadi 48-bit (agar bisa di-XOR dengan subkey), dan `P` mengacak ulang hasil dari S-Box.
* **`PC1` & `PC2` (Permuted Choice)**: Digunakan saat proses pembuatan kunci (Key Schedule). `PC1` membuang bit *parity* (mengubah 64-bit jadi 56-bit). `PC2` memilih dan memadatkan 56-bit menjadi 48-bit (Subkey untuk setiap putaran).
* **`SHIFTS`**: Menentukan berapa kali bit harus digeser ke kiri (Left Shift) pada tiap putaran (Round 1-16).
* **`S_BOX`**: Ini adalah "Jantung Keamanan" DES. Tabel ini melakukan substitusi non-linear, merapatkan kembali data dari 48-bit menjadi 32-bit. Tanpa S-Box, DES hanyalah sistem acak matematika biasa yang sangat mudah dibobol.

### Pembuatan Kunci / Key Schedule (Line 115 - 127)
```python
def generate_keys(key_bin):
```
1. Memasukkan kunci asli (64-bit) ke `PC1` sehingga berubah menjadi 56-bit.
2. Membelahnya menjadi dua bagian: Kiri (`c0`, 28-bit) dan Kanan (`d0`, 28-bit).
3. Terjadi _looping_ 16 kali (mewakili 16 putaran DES). Di tiap putaran, `c0` dan `d0` digeser ke kiri (*Circular Left Shift*) sesuai nilai di tabel `SHIFTS`.
4. Setelah digeser, Kiri dan Kanan digabung, lalu dilewatkan ke tabel `PC2` untuk menjadikannya 48-bit (Subkey).
5. Hasil akhirnya adalah array berisi 16 buah `Subkey` yang berbeda-beda.

### Fungsi Feistel (Line 129 - 143)
```python
def feistel(r_half, subkey):
```
Ini adalah fungsi yang dieksekusi di setiap putaran dari total 16 putaran DES:
1. `r_half` (data separuh kanan, 32-bit) dilebarkan menjadi 48-bit dengan tabel `E`.
2. Hasil pelebaran tersebut di-XOR dengan `subkey` (48-bit).
3. Hasil XOR (48-bit) dibagi menjadi 8 kelompok (masing-masing 6-bit). Tiap kelompok dimasukkan ke `S_BOX` untuk diciutkan menjadi 4-bit. (8 kelompok x 4-bit = 32-bit).
4. Hasil substitusi 32-bit tadi diacak posisinya menggunakan tabel `P`.

### Enkripsi Per Blok (Line 145 - 161)
```python
def process_block(block_bin, keys):
```
Satu blok pesan (64-bit / 8 karakter) dienkripsi melalui fungsi ini:
1. Blok diacak dengan `IP`.
2. Dibelah jadi dua: `L` (Kiri, 32-bit) dan `R` (Kanan, 32-bit).
3. Memasuki **16 putaran (Rounds)**:
   * Bagian Kiri yang baru (`L_new`) mengambil nilai Kanan (`R`).
   * Bagian Kanan yang baru (`R_new`) didapat dari hasil XOR bagian Kiri lama (`L`) dengan hasil fungsi `feistel(R, key)`.
4. Setelah 16 putaran selesai, posisi L dan R **ditukar** (Swap).
5. Hasilnya diacak terakhir kalinya dengan `IP_INV`.

### Penggabungan Enkripsi Utama (Line 163 - 180)
```python
def encrypt_message(text, key_text):
```
Fungsi yang akan dipanggil oleh aplikasi Chat:
1. `text` (string) diubah menjadi array of Bytes (UTF-8).
2. Kunci diatur pasti 8 karakter via `.ljust(8, b'0')[:8]`. 
3. Membuat 16 *subkey* menggunakan `generate_keys()`.
4. Menambahkan PKCS7 *padding* agar panjang pesan pas berkelipatan 8.
5. Memecah pesan menjadi blok per 8-byte, dan memanggil `process_block()` untuk tiap blok (Mode ECB).
6. Menggabungkan seluruh hasil blok terenkripsi menjadi teks hexadecimal. `decrypt_message()` bekerja kebalikannya (dengan kunci yang dibalik urutannya/di-*reverse*).

---

## 3. Penjelasan `chat_node.py` (Sistem Komunikasi Jaringan)
File ini bertugas mengirimkan ciphertext dari DES melalui jaringan internet menggunakan *socket*.

### Penerima Pesan / Receiver Thread (Line 6 - 26)
```python
def receive_messages(sock, secret_key):
```
* Sebuah *Infinite Loop* (`while True`) yang terus memantau apakah ada data masuk.
* Begitu `data = sock.recv(4096)` menerima paket dari jaringan, data tersebut di-_decode_ dari byte. Datanya berupa Ciphertext (teks acak Hexadecimal).
* Pesan yang diterima akan langsung dimasukkan ke fungsi `des_manual.decrypt_message()` untuk diubah kembali ke *plain text*.
* Menggunakan `threading.Thread` di baris ke-79 agar loop penerima ini bisa berjalan di latar belakang (bersamaan dengan proses mengetik pesan). (Ini disebut *Asynchronous / Full-Duplex*).

### Setup Server / Host (Line 28 - 37)
```python
def start_host(port):
```
* `socket.AF_INET`: Menggunakan protokol IPv4.
* `socket.SOCK_STREAM`: Menggunakan protokol koneksi TCP (Handshake aman, data dijamin sampai utuh, penting untuk pengiriman kode acak/ciphertext yang sensitif rusak).
* `bind(('0.0.0.0', port))`: Server akan membuka gerbang di port 5000, dan siap menerima dari IP mana pun (`0.0.0.0`).
* `server.accept()`: Program akan *berhenti/menunggu* di baris ini sampai ada Client yang terhubung. Begitu terhubung, ia mengembalikan objek `conn` yang digunakan untuk mengirim/terima data.

### Setup Client (Line 39 - 48)
```python
def start_client(ip, port):
```
* Klien membuat soket TCP dan memanggil `client.connect((ip, port))`.
* Berbeda dengan server yang menunggu, Client secara aktif "mengetuk" pintu IP dan Port milik Server.

### Fungsi Utama (Line 50 - Akhir)
1. Menanyakan peran ke *user* lewat input terminal.
2. Meminta *Secret Key*. Key ini TIDAK PERNAH dikirim via koneksi jaringan `conn.send()`. Keduanya memiliki key sendiri secara lokal, hal ini sangat disukai oleh dosen karena membuktikan Anda paham manajemen keamanan.
3. Memulai Thread `receive_messages`.
4. Loop utama `while True`: Terus menerus menunggu *user* mengetik pesan (`input("> ")`). Begitu diketik, pesan langsung dienkripsi `des_manual.encrypt_message()`, lalu dikirim melalui socket `conn.send()`.
