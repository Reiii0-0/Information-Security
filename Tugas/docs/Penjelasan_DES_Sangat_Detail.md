# 📘 BUKU PANDUAN ULTIMATE: BEDAH KODE DES (LINE-BY-LINE)

Dokumen ini adalah penjelasan paling komprehensif, sangat detail, dan tidak ada yang dilewati. Kita akan membahas dari konsep dasar DES, membedah satu per satu setiap tabel yang digunakan, hingga mengupas tuntas setiap baris kode yang Anda tulis.

---

## 🏗️ BAGIAN 1: KONSEP DASAR ALGORITMA DES
**DES (Data Encryption Standard)** adalah algoritma kriptografi yang diciptakan pada tahun 1970-an. Ada tiga kata kunci utama untuk memahami DES:
1. **Symmetric-Key (Kunci Simetris):** Kunci rahasia yang digunakan untuk mengunci (enkripsi) dan membuka (dekripsi) adalah kunci yang sama persis.
2. **Block Cipher (Sandi Blok):** DES tidak mengenkripsi teks huruf-demi-huruf. DES mengenkripsi data secara berkelompok (blok). Ukuran satu blok DES mutlak **64-bit (8 karakter/byte)**. Jika pesan kurang dari 64-bit, wajib ditambahkan ganjalan (*padding*).
3. **Feistel Network:** Ini adalah arsitektur matematis di mana data dibelah menjadi dua (Kiri dan Kanan), lalu disilangkan berulang-ulang sebanyak **16 putaran (Rounds)**. Keajaiban Feistel adalah: algoritma enkripsi dan dekripsi menggunakan mesin/struktur yang **sama persis 100%**, hanya urutan kuncinya saja yang dibalik.

---

## 🗄️ BAGIAN 2: BEDAH SEMUA TABEL KONSTANTA (Baris 3 - 109)
Semua tabel di bawah ini bukan angka acak yang Anda buat sendiri. Ini adalah standar baku matematis internasional dari algoritma DES.

### 1. Tabel `IP` (Initial Permutation) - Baris 4
Fungsi tabel ini adalah mengacak posisi bit data (64-bit) saat **pertama kali masuk** ke dalam mesin pencacah DES.
* **Cara membacanya:** Angka pertama di tabel ini adalah `58`. Ini berarti: "Ambil bit urutan ke-58 dari pesan asli, lalu letakkan ia di urutan pertama (ke-1) pada pesan yang baru". Angka kedua `50` berarti: "Ambil bit urutan ke-50, taruh di urutan kedua", dan seterusnya sampai 64 bit.
* **Secara Konsep:** Ini disebut *Transposisi*. Tidak ada data yang diubah nilainya (0 tetap 0, 1 tetap 1), hanya digeser letaknya.

### 2. Tabel `IP_INV` (Inverse Initial Permutation) - Baris 15
Ini adalah kebalikan mutlak dari tabel `IP`. Digunakan pada **tahap paling akhir** (setelah 16 putaran Feistel selesai).
* Tujuannya adalah mengembalikan pengacakan yang dilakukan oleh `IP`. Jika Anda memasukkan teks ke `IP` lalu memasukkannya ke `IP_INV` tanpa diapa-apakan, teksnya akan kembali seperti semula. Angka pertamanya `40`, mengembalikan apa yang digeser oleh `IP`.

### 3. Tabel `E` (Expansion Box) - Baris 26
Di dalam fungsi Feistel, data separuh kanan itu besarnya **32-bit**, sedangkan *Subkey* (Kunci Putaran) besarnya **48-bit**. Karena ukurannya beda, mereka tidak bisa dioperasikan (di-XOR).
* **Fungsi:** Tabel `E` bertugas melebarkan (expand) data 32-bit menjadi 48-bit.
* **Cara Kerjanya:** Jika Anda menghitung jumlah angka di tabel `E`, jumlahnya ada 48. Beberapa angka (seperti `4`, `5`, `8`, `9`) muncul dua kali (*di-copy-paste*). Ini menyebarkan 1 bit menjadi 2 bit, menciptakan efek **Diffusion** (satu perubahan kecil akan menyebar ke mana-mana).

### 4. Tabel `P` (Permutation) - Baris 37
Setelah data melewati S-Box (ukurannya kembali jadi 32-bit), posisinya diacak lagi menggunakan tabel `P` ini.
* **Fungsi:** Memastikan bahwa output dari satu S-Box akan menyebar dan memengaruhi S-Box yang berbeda di putaran Feistel berikutnya (efek bola salju / *Avalanche Effect*).

### 5. Tabel `PC1` (Permuted Choice 1) - Baris 44
Tabel ini digunakan HANYA pada *Key* (Kunci Rahasia), bukan pada pesan.
* Kunci yang kita masukkan adalah 64-bit (8 karakter). Tabel `PC1` **hanya memiliki 56 angka**. 
* **Fungsi:** Tabel ini mengacak kunci sekaligus **membuang 8-bit** (bit kelipatan 8 yaitu ke-8, 16, 24, dst dibuang). Bit yang dibuang ini aslinya adalah *Parity Bit* (untuk ngecek error). Jadi, kunci DES yang sesungguhnya hanyalah **56-bit**.

### 6. Tabel `PC2` (Permuted Choice 2) - Baris 55
Setelah kunci 56-bit diputar dan digeser (Shift), ia harus dimasukkan ke tabel `PC2`.
* **Fungsi:** Tabel `PC2` hanya memiliki **48 angka**. Artinya, ia memilih 48-bit dari 56-bit yang tersedia, dan mengacaknya. Output dari PC2 inilah yang disebut **Subkey** (Kunci Putaran) yang siap di-XOR dengan pesan.

### 7. Tabel `SHIFTS` - Baris 66
Ada 16 angka di tabel ini: `[1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]`.
* **Fungsi:** Menentukan berapa banyak langkah kunci harus "digeser ke kiri" (Circular Left Shift) pada putaran tertentu. Contoh: Pada putaran ke-1, geser 1 bit. Pada putaran ke-3, geser 2 bit.

### 8. Tabel `S_BOX` (Substitution Box) - Baris 68
Ini adalah **Jantung Keamanan Tertinggi** dari DES. Tanpa ini, DES sangat gampang di-_hack_. Ada 8 buah S-Box (`S1` sampai `S8`).
* **Sifat:** Ini adalah satu-satunya proses yang **Non-Linear**. (Tabel lain cuma mindah-mindahin posisi, S-Box ini murni mengubah nilai bit menjadi nilai baru yang tidak bisa ditebak rumusnya).
* **Cara Kerjanya:** Menerima input 48-bit. Dibagi jadi 8 kelompok (tiap kelompok 6-bit). Tiap 6-bit masuk ke S-Box yang sesuai.
* **Cara Membaca 6-bit (Contoh input `101010` masuk ke S1):**
  1. Ambil bit pertama (`1`) dan terakhir (`0`) => Gabung jadi `10` biner (Angka 2 desimal). Ini adalah letak **Baris (Row)**.
  2. Ambil 4 bit di tengah (`0101`) => Dalam biner ini adalah Angka 5 desimal. Ini adalah letak **Kolom (Column)**.
  3. Cek di tabel S1, baris ke-2 (ingat index mulai dari 0, 1, 2), kolom ke-5. Nilai yang ada di sana akan diubah menjadi biner 4-bit.
  4. Efeknya: 6-bit masuk, 4-bit keluar. (8 Sbox x 4-bit = 32-bit output total).

---

## 🛠️ BAGIAN 3: BEDAH KODE FUNGSI PER FUNGSI (Line by Line)

### Fungsi `permute` (Baris 112 - 113)
```python
def permute(data, table):
    return ''.join(data[i-1] for i in table)
```
* **Penjelasan:** Ini adalah fungsi sakti untuk menjalankan semua tabel `IP`, `PC1`, `P`, dll. 
* **Logika:** Fungsi ini membaca `table` angka demi angka. Jika angkanya `i`, dia akan mengambil karakter pada posisi ke `i-1` dari `data` (dikurangi 1 karena index array Python dimulai dari 0). Semua karakter yang diambil digabungkan (`join`) menjadi string biner yang baru.

### Fungsi `generate_keys` (Baris 115 - 127)
```python
def generate_keys(key_bin):
    keys = []
    # PC1
    key_pc1 = permute(key_bin, PC1)
```
* Baris 118: Kunci 64-bit (`key_bin`) dilewatkan ke tabel `PC1` menggunakan fungsi `permute`. Hasilnya `key_pc1` (56-bit).

```python
    c0 = key_pc1[:28]
    d0 = key_pc1[28:]
```
* Baris 120-121: Membelah kunci 56-bit menjadi dua: `c0` (separuh kiri, 28-bit) dan `d0` (separuh kanan, 28-bit).

```python
    for shift in SHIFTS:
        c0 = c0[shift:] + c0[:shift]
        d0 = d0[shift:] + d0[:shift]
        keys.append(permute(c0 + d0, PC2))
    return keys
```
* Baris 123: Looping 16 kali, mengambil nilai pergeseran dari array `SHIFTS`.
* Baris 124-125: Memotong string dari index `shift` ke belakang, lalu menyambungkannya dengan potongan dari awal sampai index `shift`. Ini adalah trik Python untuk melakukan **Circular Left Shift** (menggeser bit ke kiri, dan bit yang jatuh dari tebing kiri muncul lagi di kanan).
* Baris 126: `c0` dan `d0` digabung kembali, lalu dipadatkan menggunakan tabel `PC2`. Hasilnya (48-bit) dimasukkan ke dalam daftar `keys`. Setelah loop selesai, kembalikan 16 kunci tersebut.

### Fungsi `feistel` (Baris 129 - 143)
```python
def feistel(r_half, subkey):
    expanded = permute(r_half, E)
    xored = des_utils.xor(expanded, subkey)
```
* Baris 131: Melebarkan data `r_half` (Kanan, 32-bit) menjadi 48-bit menggunakan tabel `E`.
* Baris 133: Melakukan operasi XOR antara data yang dilebarkan dengan `subkey` (48-bit). Hasilnya disimpan di `xored`.

```python
    s_output = ""
    for i in range(8):
        block = xored[i*6 : (i+1)*6]
```
* Baris 135-137: Looping 8 kali (karena ada 8 S-Box). `xored` yang panjangnya 48-bit dipecah-pecah menjadi potongan kecil sepanjang 6-bit. Iterasi ke-0 mengambil karakter 0-6. Iterasi ke-1 mengambil 6-12, dst.

```python
        row = int(block[0] + block[5], 2)
        col = int(block[1:5], 2)
        val = S_BOX[i][row][col]
        s_output += format(val, '04b')
```
* Baris 138: Mengambil bit ujung (index 0 dan 5), menggabungkannya jadi string, lalu fungsi `int(..., 2)` mengubah string biner tersebut menjadi angka desimal (sebagai index **Baris/Row**).
* Baris 139: Mengambil 4 bit tengah (index 1 sampai 4), mengubahnya jadi desimal (sebagai index **Kolom/Col**).
* Baris 140: Melacak angka pengganti di dalam tabel `S_BOX` ke-`i`.
* Baris 141: Mengubah angka pengganti (misal angka 9) menjadi format biner 4-bit (`04b`), hasilnya `1001`. Ditambahkan ke `s_output`.

```python
    return permute(s_output, P)
```
* Baris 143: Mengacak `s_output` (32-bit hasil S-Box) menggunakan tabel `P` dan mengembalikannya.

### Fungsi `process_block` (Baris 145 - 161)
```python
def process_block(block_bin, keys):
    block = permute(block_bin, IP)
    L = block[:32]
    R = block[32:]
```
* Mengacak blok masuk 64-bit dengan tabel `IP`.
* Membelahnya menjadi `L` (Kiri, 32-bit) dan `R` (Kanan, 32-bit).

```python
    for key in keys:
        L_new = R
        R_new = des_utils.xor(L, feistel(R, key))
        L = L_new
        R = R_new
```
* Baris 153-157: Inti Jaringan Feistel selama 16 putaran. 
* Kiri baru (`L_new`) mengambil nilai Kanan lama (`R`).
* Kanan baru (`R_new`) adalah hasil XOR Kiri lama (`L`) dengan hasil eksekusi fungsi `feistel`.
* Variabel L dan R di-update untuk putaran berikutnya.

```python
    return permute(R + L, IP_INV)
```
* Baris 160: Ingat aturan Feistel: di akhir 16 putaran, posisinya harus **ditukar** (Swap). Makanya ditulis `R + L` bukan `L + R`!
* Setelah digabung, diacak untuk terakhir kali dengan tabel `IP_INV`. Selesai! Keluarlah 1-blok Ciphertext utuh.

### Fungsi `encrypt_message` (Baris 163 - 180)
```python
def encrypt_message(text, key_text):
    text_bytes = text.encode('utf-8')
    key_bytes = key_text.encode('utf-8').ljust(8, b'0')[:8]
    
    key_bin = des_utils.bytes2bin(key_bytes)
    keys = generate_keys(key_bin)
```
* Baris 165: Mengubah pesan teks menjadi format *bytes* (ASCII/UTF-8).
* Baris 166: Kunci juga diubah ke *bytes*. Fungsi `.ljust(8, b'0')` artinya: "Jika kunci kurang dari 8 karakter, tambahkan biner '0' di kanannya sampai pas 8. Lalu `[:8]` memastikan kunci tidak boleh lebih dari 8 karakter. (Pemotongan otomatis).
* Baris 168-169: Mengubah kunci jadi biner `0` dan `1`, lalu memanggil `generate_keys()` untuk membuat 16 Subkey.

```python
    padded_bytes = des_utils.pad(text_bytes)
    cipher_hex = ""
    
    for i in range(0, len(padded_bytes), 8):
        block_bytes = padded_bytes[i:i+8]
        block_bin = des_utils.bytes2bin(block_bytes)
        cipher_bin = process_block(block_bin, keys)
        cipher_hex += des_utils.bin2hex(cipher_bin)
        
    return cipher_hex
```
* Baris 171: Melakukan **Padding PKCS7** (menambahkan ganjalan agar panjang pesan pas kelipatan 8 bytes).
* Baris 174-178: Looping untuk memecah pesan menjadi blok-blok sepanjang 8 bytes. Tiap 8 byte (`block_bytes`) diubah ke biner, lalu dimasukkan ke dalam `process_block()` (mesin pencacah DES utama). Hasil cacahannya (biner) diubah menjadi teks *Hexadecimal* (seperti `1A3F...`) dan digabung terus ke variabel `cipher_hex`.

### Fungsi `decrypt_message` (Baris 182 - 200)
```python
def decrypt_message(cipher_hex, key_text):
    key_bytes = key_text.encode('utf-8').ljust(8, b'0')[:8]
    key_bin = des_utils.bytes2bin(key_bytes)
    keys = generate_keys(key_bin)
    keys.reverse() # Decryption uses reversed keys
```
* Baris 183-186: Sama persis seperti enkripsi, menyiapkan kunci. Namun poin terpenting ada di baris 186: `keys.reverse()`. Inilah pesona jaringan Feistel. Algoritma dekripsi DES itu 100% sama dengan enkripsi, HANYA urutan kuncinya yang dibalik (dari kunci ke-16 turun ke kunci ke-1).

```python
    cipher_bin = des_utils.hex2bin(cipher_hex)
    plain_bytes = bytearray()
    
    for i in range(0, len(cipher_bin), 64):
        block_bin = cipher_bin[i:i+64]
        if len(block_bin) < 64:
            break
        plain_bin = process_block(block_bin, keys)
        plain_bytes.extend(des_utils.bin2bytes(plain_bin))
```
* Baris 188: Mengubah teks *Hexadecimal* dari jaringan kembali menjadi biner murni.
* Baris 191-196: Sama seperti sebelumnya, pesan dipecah per-64-bit (karena ini sudah biner, 8 bytes = 64 bit). Dimasukkan kembali ke mesin pencacah `process_block()`. Karena kuncinya terbalik, mesin ini otomatis merajut kembali teks acak tadi menjadi teks asli (ajaib, bukan?).
* Hasilnya dikembalikan menjadi *bytes* dan disambung ke `plain_bytes`.

```python
    unpadded_bytes = des_utils.unpad(plain_bytes)
    return unpadded_bytes.decode('utf-8', errors='ignore')
```
* Baris 198: Setelah utuh, kita tidak butuh *padding* pengganjalnya lagi. Fungsi `unpad()` akan mengecek byte terakhir, melihat angkanya (misal 3), dan memotong 3 byte terakhir.
* Baris 199: Mengubah kembali (Decode) *bytes* menjadi string teks yang bisa dibaca manusia. `errors='ignore'` ditambahkan agar jika ada 1 bit yang rusak saat transmisi (menyebabkan teks jadi error), program tidak langsung mati terbakar (crash), melainkan mengabaikan huruf yang rusak tersebut.

---
**SELESAI.**
Anda baru saja menuntaskan bedah anatomi dari algoritma enkripsi paling legendaris sepanjang sejarah dunia keamanan komputer! 🏆
