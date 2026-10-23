# ✉️ PART 2: Perjalanan Pesan — Enkripsi & Dekripsi

## Pendahuluan

Di Part 1, kita sudah berhasil membuat **16 Anak Kunci (Subkey)** dari 1 Kunci Utama. Ke-16 Anak Kunci itu sekarang tersimpan rapi di dalam laci memori bernama `keys`.

Di Part 2 ini, kita akan mengikuti perjalanan pesan chat Anda (misalnya kata `"HALO"`) dari saat diketik di terminal, dihancurkan menjadi teks acak (*Ciphertext*), dikirim lewat jaringan, diterima oleh teman Anda, lalu dirajut kembali menjadi kata `"HALO"` yang bisa dibaca.

Perjalanan ini terbagi menjadi 2 bagian besar:
- **Bagian A:** Enkripsi (Menghancurkan pesan menjadi *Ciphertext*)
- **Bagian B:** Dekripsi (Merajut kembali *Ciphertext* menjadi pesan asli)

---

# BAGIAN A: ENKRIPSI

## Langkah A1: Persiapan Pesan (`encrypt_message`, Baris 163-172)

Saat Anda mengetik `"HALO"` di terminal dan menekan Enter, program memanggil fungsi `encrypt_message(text="HALO", key_text="RAHASIA1")`.

```python
# Baris 163-165: Fungsi menerima teks dan kunci, lalu mengubah teks jadi Byte
def encrypt_message(text, key_text):
    text_bytes = text.encode('utf-8')
```

### Penjelasan Detail:

`text.encode('utf-8')` mengubah string `"HALO"` menjadi deretan angka Byte (ASCII):
```
H = 72,  A = 65,  L = 76,  O = 79
```
Variabel `text_bytes` sekarang berisi 4 angka Byte: `b'\x48\x41\x4c\x4f'` (atau dalam desimal: `[72, 65, 76, 79]`).

Selanjutnya, kunci diproses (sudah dibahas lengkap di Part 1):

```python
# Baris 166-169: Menyiapkan kunci dan membuat 16 Anak Kunci
key_bytes = key_text.encode('utf-8').ljust(8, b'0')[:8]
key_bin = des_utils.bytes2bin(key_bytes)
keys = generate_keys(key_bin)
```

Setelah baris ini selesai, variabel `keys` sudah berisi 16 Anak Kunci 48-bit yang siap digunakan.

---

## Langkah A2: Padding / Penambalan (`encrypt_message`, Baris 171)

```python
# Baris 171: Menambal pesan agar panjangnya habis dibagi 8
padded_bytes = des_utils.pad(text_bytes)
```

### Penjelasan Detail:

Mesin DES (`process_block`) hanya bisa menelan data yang ukurannya **tepat 8 Byte (64-bit)**. Pesan `"HALO"` panjangnya cuma 4 Byte. Kurang 4 Byte lagi agar genap 8.

Fungsi `pad()` dari `des_utils.py` yang dipanggil:

```python
# des_utils.py, Baris 21-23
def pad(data_bytes):
    pad_len = 8 - (len(data_bytes) % 8)
    return data_bytes + bytes([pad_len] * pad_len)
```

Mari kita ikuti hitungannya langkah demi langkah:

1. `len(data_bytes)` — Panjang pesan `"HALO"` adalah **4** Byte.
2. `4 % 8` — Operator `%` (Modulus) menghitung sisa bagi. 4 dibagi 8 = 0 sisa **4**.
3. `8 - 4` — Hasilnya **4**. Artinya kita kurang 4 Byte lagi.
4. `pad_len = 4` — Variabel ini menyimpan angka kekurangan: **4**.
5. `[pad_len] * pad_len` — Python menggandakan angka 4 sebanyak 4 kali: `[4, 4, 4, 4]`.
6. `bytes([4, 4, 4, 4])` — Mengubah list angka tadi menjadi tipe data Byte: `b'\x04\x04\x04\x04'`.
7. `data_bytes + ...` — Pesan asli disambung dengan ganjalan.

Hasilnya:
```
Sebelum padding: [H ] [A ] [L ] [O ]              → 4 Byte
Sesudah padding: [H ] [A ] [L ] [O ] [04] [04] [04] [04]  → 8 Byte ✓
                  72   65   76   79    4    4    4    4
```

Sekarang `padded_bytes` berukuran tepat 8 Byte dan siap dimasukkan ke mesin DES.

**Pertanyaan: Bagaimana kalau pesannya sudah pas 8 huruf?**
Misalnya pesan `"KOMPUTER"` (8 huruf). `8 % 8 = 0`, maka `8 - 0 = 8`. Padding-nya adalah `[8, 8, 8, 8, 8, 8, 8, 8]` — **1 blok penuh baru** berisi angka 8. Kenapa? Karena kalau tidak ditambal, mesin `unpad` nanti bisa salah menebak mana huruf asli dan mana ganjalan (sudah dibahas di sesi chat sebelumnya).

---

## Langkah A3: Mekanisme Ban Berjalan / Pemotongan per Blok (`encrypt_message`, Baris 172-178)

```python
# Baris 172: Menyiapkan keranjang kosong untuk menampung hasil enkripsi
cipher_hex = ""

# Baris 174: Looping — memotong pesan per 8 Byte
for i in range(0, len(padded_bytes), 8):

    # Baris 175: Mengambil potongan 8 Byte
    block_bytes = padded_bytes[i:i+8]

    # Baris 176: Mengubah 8 Byte menjadi string biner 64-bit
    block_bin = des_utils.bytes2bin(block_bytes)

    # Baris 177: MEMASUKKAN KE MESIN PENCACAH UTAMA!
    cipher_bin = process_block(block_bin, keys)

    # Baris 178: Mengubah hasil biner jadi Hexadecimal, ditambahkan ke keranjang
    cipher_hex += des_utils.bin2hex(cipher_bin)
```

### Penjelasan Detail per Baris:

**Baris 172: `cipher_hex = ""`**
Ini adalah keranjang kosong (string kosong) yang nantinya akan diisi teks acak Hexadecimal. Setiap blok yang selesai dienkripsi akan ditempelkan (*disambung*) di sini.

**Baris 174: `for i in range(0, len(padded_bytes), 8):`**
Fungsi `range(start, stop, step)` menghasilkan deretan angka yang melompat-lompat:
- `start = 0` — Mulai dari index ke-0 (awal pesan).
- `stop = len(padded_bytes)` — Berhenti saat sudah melewati seluruh pesan.
- `step = 8` — Melompat setiap 8 langkah.

Untuk pesan `"HALO"` yang sudah di-padding (total 8 Byte), `range(0, 8, 8)` hanya menghasilkan satu angka: `[0]`. Artinya looping hanya berjalan **1 kali** (karena pesannya pas 1 blok).

Jika pesannya panjang (misalnya 24 Byte setelah padding), `range(0, 24, 8)` akan menghasilkan: `[0, 8, 16]`. Looping berjalan **3 kali** (3 blok terpisah dienkripsi bergantian).

**Baris 175: `block_bytes = padded_bytes[i:i+8]`**
Ini menggunakan *slicing* Python untuk mengambil tepat 8 Byte dari pesan:
- Saat `i = 0`: mengambil index 0 sampai 7 (8 Byte pertama).
- Saat `i = 8`: mengambil index 8 sampai 15 (8 Byte kedua).
- Dan seterusnya.

Untuk kasus `"HALO"`, `block_bytes` berisi: `[72, 65, 76, 79, 4, 4, 4, 4]` (huruf HALO + 4 byte padding).

**Baris 176: `block_bin = des_utils.bytes2bin(block_bytes)`**
Memanggil fungsi yang sudah kita bahas di Part sebelumnya. Setiap Byte diubah jadi biner 8-digit, lalu disambung. Hasilnya:
```
72  → 01001000
65  → 01000001
76  → 01001100
79  → 01001111
4   → 00000100
4   → 00000100
4   → 00000100
4   → 00000100
```
`block_bin` sekarang berisi string: `"0100100001000001010011000100111100000100000001000000010000000100"` (64 karakter biner).

**Baris 177: `cipher_bin = process_block(block_bin, keys)`**
Inilah momen dimana blok 64-bit tadi resmi dilemparkan ke dalam **Mesin Pencacah Utama** bersama laci berisi 16 Anak Kunci. Di dalam mesin inilah Feistel Network bekerja. (Akan dibahas sangat detail di Langkah A4 di bawah).

**Baris 178: `cipher_hex += des_utils.bin2hex(cipher_bin)`**
Mesin pencacah mengeluarkan 64-bit biner yang sudah hancur. Fungsi `bin2hex()` mengubahnya jadi bentuk Hexadecimal (lebih pendek dan mudah dikirim lewat jaringan). Operator `+=` menempelkan hasilnya ke keranjang `cipher_hex`.

---

## Langkah A4: Masuk ke Mesin Pencacah Utama (`process_block`, Baris 145-161)

Ini adalah badan mesin DES. Satu blok masuk (64-bit), satu blok keluar (64-bit).

### A4.1: Pengacakan Pintu Masuk — Tabel IP (Baris 147)

```python
# Baris 145-147: Fungsi menerima blok 64-bit dan 16 Anak Kunci
def process_block(block_bin, keys):
    block = permute(block_bin, IP)
```

#### Apa itu Tabel IP? (Baris 4-13)

```python
IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9,  1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]
```

Tabel ini berisi **64 angka** (karena data yang masuk adalah 64-bit, dan data yang keluar juga 64-bit — tidak ada yang dibuang, hanya diacak posisinya).

Cara kerjanya sama persis dengan tabel PC1 yang sudah kita bahas di Part 1. Fungsi `permute()` membaca tabel ini angka demi angka:
- Angka pertama = **58**. Ambil bit urutan ke-58 dari `block_bin`, taruh di posisi pertama output.
- Angka kedua = **50**. Ambil bit urutan ke-50, taruh di posisi kedua.
- ...dan seterusnya sampai 64 angka habis.

**Fakta Historis:** Secara kriptografi, tabel IP ini sebenarnya **tidak menambah keamanan sama sekali**. Tabel ini diciptakan pada era 1970-an hanya untuk mempermudah pemasukan data ke dalam *chip hardware* 8-bit di komputer kuno. Meskipun begitu, ia tetap menjadi bagian wajib dari standar DES.

Hasilnya: `block` sekarang berisi 64-bit yang posisinya sudah teracak.

### A4.2: Pembelahan Mangkuk (Baris 150-151)

```python
# Baris 150: Ambil 32 karakter pertama → Mangkuk Kiri
L = block[:32]

# Baris 151: Ambil 32 karakter sisanya → Mangkuk Kanan
R = block[32:]
```

Blok 64-bit yang sudah diacak tadi dibelah tepat di tengah:
- **`L`** (Left / Kiri) = 32-bit pertama (index 0 sampai 31).
- **`R`** (Right / Kanan) = 32-bit sisanya (index 32 sampai 63).

Kedua mangkuk ini akan saling bertukar dan dihancurkan selama 16 putaran Feistel.

### A4.3: Jantung Feistel — Looping 16 Putaran (Baris 154-158)

```python
# Baris 154: Looping 16 kali, mengambil 1 Anak Kunci per putaran
for key in keys:

    # Baris 155: Mangkuk Kiri yang baru = isi Mangkuk Kanan yang lama
    L_new = R

    # Baris 156: Mangkuk Kanan yang baru = Mangkuk Kiri yang lama di-XOR dengan hasil Feistel
    R_new = des_utils.xor(L, feistel(R, key))

    # Baris 157-158: Update mangkuk untuk putaran selanjutnya
    L = L_new
    R = R_new
```

#### Penjelasan Detail Baris 154:

`for key in keys:` — Python membaca laci `keys` dari awal ke akhir. Pada putaran pertama, `key` berisi Anak Kunci ke-1 (`K1`). Pada putaran kedua, `key` berisi `K2`. Dan seterusnya sampai `K16`.

#### Penjelasan Detail Baris 155:

`L_new = R` — Aturan pertama dari Feistel Network: **Mangkuk Kiri yang baru langsung mengkopi Mangkuk Kanan yang lama**. Tidak ada proses apa pun, tidak ada perhitungan, hanya salin mentah-mentah. Ini sangat penting agar nanti saat proses dekripsi, mesin bisa memutar balikkan prosesnya.

#### Penjelasan Detail Baris 156:

`R_new = des_utils.xor(L, feistel(R, key))` — Ini adalah baris paling krusial di seluruh algoritma DES! Di sini terjadi **dua hal** secara berurutan:

1. **`feistel(R, key)`** dipanggil terlebih dahulu. Mangkuk Kanan (`R`, 32-bit) dan Anak Kunci (`key`, 48-bit) dimasukkan ke dalam **Mesin Bumbu Ajaib** (fungsi `feistel`). Hasil keluarannya adalah bumbu 32-bit yang sudah sangat diacak-acak (akan dibahas sangat detail di Langkah A5 di bawah).

2. **`des_utils.xor(L, ...)`** — Bumbu 32-bit dari langkah 1 tadi dibenturkan (XOR) dengan Mangkuk Kiri yang lama (`L`). Hasilnya menjadi **Mangkuk Kanan yang baru** (`R_new`).

#### Penjelasan Detail Baris 157-158:

```python
L = L_new
R = R_new
```

Variabel `L` dan `R` di-update dengan nilai baru agar putaran berikutnya menggunakan mangkuk yang sudah bermutasi. Putaran ke-2 akan mengolah mangkuk yang sudah diacak oleh putaran ke-1, dan seterusnya sampai 16 kali.

**Ilustrasi Visual 1 Putaran Feistel:**
```
MASUK PUTARAN ke-n:
    L (32-bit)              R (32-bit)
    │                       │
    │                       ├──────────────┐
    │                       │              │
    │                       ▼              │
    │               ┌──────────────┐       │
    │               │  feistel()   │       │
    │               │  + Kunci Kn  │       │
    │               └──────┬───────┘       │
    │                      │               │
    │           Bumbu 32-bit               │
    │                      │               │
    ▼                      ▼               │
  ┌────────────────────────────┐           │
  │          XOR               │           │
  │   L (lama) ⊕ Bumbu        │           │
  └────────────┬───────────────┘           │
               │                           │
               ▼                           ▼
KELUAR PUTARAN ke-n:
           R_new (32-bit)          L_new (32-bit)
           (hasil XOR)            (salinan R lama)
```

Perhatikan bahwa Mangkuk Kanan yang lama (R) **tidak hilang** — ia dicopy menjadi Mangkuk Kiri yang baru (L_new). Sementara Mangkuk Kiri yang lama (L) dihancurkan oleh XOR dengan bumbu dan menjadi Mangkuk Kanan yang baru (R_new). Inilah mengapa disebut *"Jaringan Feistel"* — data saling menyilang berulang-ulang.

### A4.4: Pertukaran (Swap) & Pengacakan Keluar — Tabel IP_INV (Baris 161)

```python
# Baris 161: Menukar posisi R dan L, lalu mengacak dengan tabel IP_INV
return permute(R + L, IP_INV)
```

#### Penjelasan Detail:

Setelah 16 putaran Feistel selesai, ada **satu langkah terakhir yang krusial**: posisi Mangkuk Kanan dan Kiri harus **ditukar (Swap)**.

Perhatikan kode `R + L`, bukan `L + R`! Ini **bukan salah ketik**. Ini adalah aturan baku dari standar DES. Setelah 16 putaran Feistel, mangkuk yang terakhir kali diolah (R) harus diletakkan di depan, dan L di belakang. Tujuannya agar saat proses dekripsi nanti, mesin yang sama bisa memutar balikkan prosesnya dengan benar.

Setelah ditukar dan digabung kembali menjadi 64-bit, data terakhir ini diacak posisinya menggunakan tabel **IP_INV** (Inverse Initial Permutation):

```python
IP_INV = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9,  49, 17, 57, 25
]
```

Tabel ini berisi **64 angka** dan bekerja sama persis seperti tabel IP. Bedanya, tabel ini adalah **kebalikan matematis sempurna** dari tabel IP. Artinya:
- Jika data X masuk ke tabel IP menghasilkan Y, maka data Y masuk ke tabel IP_INV akan menghasilkan X kembali.
- IP dan IP_INV saling membatalkan efek satu sama lain.

Hasilnya: Fungsi `process_block` mengembalikan (*return*) 64-bit biner yang sudah hancur lebur — ini adalah **Ciphertext** untuk 1 blok!

---

## Langkah A5: Mesin Bumbu Ajaib — Fungsi Feistel (`feistel`, Baris 129-143)

Ini adalah fungsi yang dipanggil oleh baris 156 tadi. Di sinilah "keajaiban" kriptografi sesungguhnya terjadi. Fungsi ini menerima Mangkuk Kanan (32-bit) dan 1 Anak Kunci (48-bit), lalu menghasilkan "bumbu" 32-bit yang sangat acak.

### A5.1: Expansion — Tabel E (Baris 131)

```python
# Baris 129-131
def feistel(r_half, subkey):
    expanded = permute(r_half, E)
```

#### Apa itu Tabel E? (Baris 26-35)

```python
E = [
    32, 1,  2,  3,  4,  5,      # Kelompok 1
    4,  5,  6,  7,  8,  9,      # Kelompok 2
    8,  9,  10, 11, 12, 13,     # Kelompok 3
    12, 13, 14, 15, 16, 17,     # Kelompok 4
    16, 17, 18, 19, 20, 21,     # Kelompok 5
    20, 21, 22, 23, 24, 25,     # Kelompok 6
    24, 25, 26, 27, 28, 29,     # Kelompok 7
    28, 29, 30, 31, 32, 1       # Kelompok 8
]
```

**Masalah:** Mangkuk Kanan (`r_half`) berukuran **32-bit**, tapi Anak Kunci (`subkey`) berukuran **48-bit**. Untuk bisa di-XOR, keduanya harus berukuran sama. Maka, Mangkuk Kanan harus **dilebarkan** dari 32-bit menjadi 48-bit.

**Bagaimana caranya?** Tabel E berisi **48 angka**. Padahal data yang masuk cuma 32-bit. Artinya, beberapa bit akan diambil lebih dari 1 kali (**diduplikasi / di-copy-paste**).

**Cara membaca tabel ini secara detail:**

Perhatikan **Kelompok 1** (baris pertama tabel): `32, 1, 2, 3, 4, 5`
- Angka 32 berarti ambil bit urutan ke-32 dari `r_half` (bit paling ujung kanan).
- Angka 1, 2, 3, 4 berarti ambil bit urutan ke-1 sampai ke-4.
- Angka 5 berarti ambil bit urutan ke-5.

Sekarang perhatikan **Kelompok 2**: `4, 5, 6, 7, 8, 9`
- Angka **4** dan **5** muncul lagi! Padahal mereka sudah diambil di Kelompok 1.

Ini artinya bit ke-4 dan ke-5 **di-fotokopi** — salinannya ditaruh di Kelompok 2 juga. Begitu seterusnya: bit-bit di perbatasan antar kelompok selalu diduplikasi.

Bit-bit yang di-copy-paste: **4-5, 8-9, 12-13, 16-17, 20-21, 24-25, 28-29, 32-1**
Total duplikasi: 16 bit tambahan. Maka: 32 bit asli + 16 bit duplikat = **48 bit**. ✓

**Kenapa bit perbatasan yang diduplikasi?** Ini menciptakan efek **Avalanche** (bola salju). Jika 1 bit saja berubah di input, perubahannya akan menyebar ke 2 kelompok S-Box sekaligus (karena bit tersebut muncul di 2 tempat). Ini membuat *hacker* sangat sulit menganalisis pola.

### A5.2: Pencampuran dengan Kunci — XOR (Baris 133)

```python
# Baris 133
xored = des_utils.xor(expanded, subkey)
```

Sekarang kita punya dua bahan yang ukurannya sama-sama **48-bit**:
- `expanded` = Mangkuk Kanan yang sudah dilebarkan (48-bit)
- `subkey` = Anak Kunci putaran ini (48-bit)

Fungsi `xor()` dari `des_utils.py` dijalankan:

```python
# des_utils.py, Baris 18-19
def xor(a, b):
    return ''.join('1' if i != j else '0' for i, j in zip(a, b))
```

**Cara kerja `zip(a, b)`:** Mensejajarkan 2 string bit-per-bit. Contoh:
```
a = "1 0 1 1 0 0"
b = "0 1 1 0 1 0"
zip menghasilkan pasangan: (1,0), (0,1), (1,1), (1,0), (0,1), (0,0)
```

**Aturan XOR (`'1' if i != j else '0'`):**
- Jika pasangan **berbeda** (`1` dan `0`, atau `0` dan `1`) → hasilnya **`1`**
- Jika pasangan **kembar** (`0` dan `0`, atau `1` dan `1`) → hasilnya **`0`**

Contoh:
```
expanded: 1 0 1 1 0 0
subkey:   0 1 1 0 1 0
─────────────────────
xored:    1 1 0 1 1 0
```

Hasilnya: `xored` berisi adonan campuran 48-bit.

### A5.3: Substitusi — S-BOX! (Baris 135-141)

Ini adalah **komponen paling penting** di seluruh algoritma DES!

```python
# Baris 135: Menyiapkan penampung hasil
s_output = ""

# Baris 136: Looping 8 kali (karena 48 ÷ 6 = 8 kelompok)
for i in range(8):

    # Baris 137: Memotong 'xored' per 6-bit
    block = xored[i*6 : (i+1)*6]
```

#### Penjelasan Detail Baris 137:

`xored` panjangnya 48 karakter. Ia dipotong menjadi 8 bongkahan, masing-masing 6 karakter:

| Nilai `i` | Rumus `i*6 : (i+1)*6` | Index yang diambil | Contoh isi `block` |
|:-:|:-:|:-:|:-:|
| 0 | `0 : 6` | karakter ke-0 sampai 5 | `"110100"` |
| 1 | `6 : 12` | karakter ke-6 sampai 11 | `"010110"` |
| 2 | `12 : 18` | karakter ke-12 sampai 17 | `"101010"` |
| 3 | `18 : 24` | karakter ke-18 sampai 23 | `"011001"` |
| 4 | `24 : 30` | karakter ke-24 sampai 29 | `"110011"` |
| 5 | `30 : 36` | karakter ke-30 sampai 35 | `"100101"` |
| 6 | `36 : 42` | karakter ke-36 sampai 41 | `"010010"` |
| 7 | `42 : 48` | karakter ke-42 sampai 47 | `"001110"` |

Setiap bongkahan 6-bit ini akan dimasukkan ke S-Box yang berbeda-beda (S1 untuk `i=0`, S2 untuk `i=1`, dst).

#### Menentukan Baris dan Kolom (Baris 138-139):

```python
    # Baris 138: Menentukan BARIS di tabel S-Box
    row = int(block[0] + block[5], 2)

    # Baris 139: Menentukan KOLOM di tabel S-Box
    col = int(block[1:5], 2)
```

Mari kita ambil contoh `block = "101010"` (saat `i = 2`, masuk ke S-Box ke-3):

**Baris 138 — Mencari Baris (Row):**
- `block[0]` = karakter index ke-0 = `"1"` (bit paling kiri)
- `block[5]` = karakter index ke-5 = `"0"` (bit paling kanan)
- `block[0] + block[5]` = `"1"` + `"0"` = **`"10"`** (penggabungan string, bukan penjumlahan angka!)
- `int("10", 2)` = mengubah biner `"10"` ke desimal = **2**
- Maka: **`row = 2`**

**Baris 139 — Mencari Kolom (Col):**
- `block[1:5]` = karakter index ke-1, 2, 3, 4 = **`"0101"`** (4 bit yang terjepit di tengah)
- `int("0101", 2)` = mengubah biner `"0101"` ke desimal = **5**
- Maka: **`col = 5`**

Secara visual, dari 6 bit `"101010"`, kita memecahnya begini:
```
bit:     1    0  1  0  1    0
posisi: [0]  [1][2][3][4]  [5]
         │    └────┬────┘    │
         │        COL        │
         └────── ROW ────────┘
```

#### Mengambil Nilai dari Tabel S-Box (Baris 140):

```python
    # Baris 140: Buka tabel S-Box ke-i, cari angka di baris 'row' kolom 'col'
    val = S_BOX[i][row][col]
```

Karena `i = 2`, kita membuka tabel **S-Box ke-3** (S3, index dimulai dari 0):

```python
# S3 (index 2 di array S_BOX)
[[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],    # Baris 0
 [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],     # Baris 1
 [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],     # Baris 2
 [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]]     # Baris 3
```

- `S_BOX[2]` = membuka tabel S3 (seluruh 4 baris di atas).
- `[row]` = `[2]` = melihat **Baris ke-2**: `[13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7]`
- `[col]` = `[5]` = melihat **Kolom ke-5**: 
  - Index 0 = 13
  - Index 1 = 6
  - Index 2 = 4
  - Index 3 = 9
  - Index 4 = 8
  - **Index 5 = 15** ← INI DIA!

Maka: **`val = 15`**

#### Mengubah Nilai Menjadi Biner 4-Bit (Baris 141):

```python
    # Baris 141: Ubah angka desimal jadi biner 4-bit, tambahkan ke penampung
    s_output += format(val, '04b')
```

- `format(15, '04b')` — Mengubah angka 15 jadi biner.
- `'04b'` artinya: format sebagai **b**iner, panjang minimum **4** digit, jika kurang ganjal dengan angka **0** di depan.
- Biner dari 15 = `1111` (sudah 4 digit, tidak perlu diganjal).
- Hasilnya: **`"1111"`** ditempelkan ke `s_output`.

**Sihir Penciutan:**
- Yang masuk ke S-Box: **6-bit** (`"101010"`)
- Yang keluar dari S-Box: **4-bit** (`"1111"`)
- 6-bit dipaksa menjadi 4-bit! 2 bit "hilang" (bukan benar-benar hilang, tapi nilainya sudah disubstitusi menjadi bentuk baru yang lebih padat).

Setelah 8 bongkahan selesai diproses oleh 8 S-Box, `s_output` berisi 8 × 4-bit = **32-bit**. Misi penciutan dari 48-bit ke 32-bit berhasil!

### A5.4: Pengacakan Akhir — Tabel P (Baris 143)

```python
# Baris 143: Mengacak posisi 32-bit hasil S-Box
return permute(s_output, P)
```

#### Apa itu Tabel P? (Baris 37-42)

```python
P = [
    16, 7,  20, 21, 29, 12, 28, 17,
    1,  15, 23, 26, 5,  18, 31, 10,
    2,  8,  24, 14, 32, 27, 3,  9,
    19, 13, 30, 6,  22, 11, 4,  25
]
```

Tabel ini berisi **32 angka** (masuk 32-bit, keluar 32-bit — tidak ada yang ditambah atau dibuang). Fungsinya hanya mengacak posisi bit.

**Kenapa perlu diacak lagi setelah S-Box?** Karena tabel P dirancang agar output dari satu S-Box **disebarkan** ke input beberapa S-Box yang berbeda di putaran berikutnya. Ini menciptakan efek **Avalanche** — perubahan kecil di 1 bit akan merambat ke banyak S-Box di putaran selanjutnya, sehingga semakin sulit dianalisis oleh *hacker*.

Hasilnya: bumbu 32-bit yang sudah sangat teracak ini di-**return** ke baris 156 (`process_block`), di mana ia akan di-XOR dengan Mangkuk Kiri.

---

## Langkah A6: Finalisasi dan Pengiriman (`encrypt_message`, Baris 178-180)

```python
    # Baris 178: Mengubah biner hasil enkripsi jadi Hexadecimal
    cipher_hex += des_utils.bin2hex(cipher_bin)

# Baris 180: Mengembalikan seluruh Ciphertext Hexadecimal
return cipher_hex
```

Setelah semua blok selesai diproses oleh ban berjalan, `cipher_hex` berisi teks *Hexadecimal* yang panjang (misal: `"A1B2C3D4E5F6A7B8"`). Inilah yang dikirim lewat jaringan TCP Socket ke komputer teman Anda.

---

# BAGIAN B: DEKRIPSI

## Langkah B1: Kunci yang Berjalan Mundur (`decrypt_message`, Baris 182-186)

Teman Anda menerima sosis Hexadecimal lewat jaringan. Program mereka memanggil `decrypt_message(cipher_hex, key_text="RAHASIA1")`.

```python
# Baris 182-186
def decrypt_message(cipher_hex, key_text):
    key_bytes = key_text.encode('utf-8').ljust(8, b'0')[:8]
    key_bin = des_utils.bytes2bin(key_bytes)
    keys = generate_keys(key_bin)
    keys.reverse()  # Decryption uses reversed keys
```

### Penjelasan Detail:

**Baris 183-185** — Persis sama seperti enkripsi. Kunci `"RAHASIA1"` diproses untuk menghasilkan 16 Anak Kunci yang identik: `[K1, K2, K3, ..., K16]`.

**Baris 186: `keys.reverse()`** — **INI ADALAH SATU-SATUNYA PERBEDAAN ANTARA ENKRIPSI DAN DEKRIPSI DI SELURUH ALGORITMA DES!**

Fungsi `.reverse()` di Python membalik urutan elemen di dalam list:
```
Sebelum: [K1, K2, K3, ..., K14, K15, K16]
Sesudah: [K16, K15, K14, ..., K3, K2, K1]
```

**Kenapa harus dibalik?**
Bayangkan Anda memakai baju dengan cara: kaos dalam → kemeja → jas. Untuk melepasnya (dekripsi), Anda harus membalik urutannya: jas dulu → kemeja → baru kaos dalam. Begitu pula dengan DES — lapisan kunci yang terakhir dipasang saat enkripsi, harus menjadi yang pertama dilepas saat dekripsi.

Secara matematis, ini dimungkinkan oleh sifat operasi **XOR** yang bersifat *self-inverse*:
- Jika `A ⊕ B = C`, maka `C ⊕ B = A`.
- Artinya, jika Anda XOR sesuatu dua kali dengan kunci yang sama, hasilnya kembali ke semula.

Dengan kunci yang dibalik urutannya, mesin `process_block` yang **sama persis** akan secara otomatis **merajut kembali** data yang hancur!

---

## Langkah B2: Membedah Sosis Hexadecimal (`decrypt_message`, Baris 188-189)

```python
# Baris 188: Mengubah Hexadecimal kembali jadi Biner
cipher_bin = des_utils.hex2bin(cipher_hex)

# Baris 189: Menyiapkan keranjang kosong
plain_bytes = bytearray()
```

### Penjelasan Detail:

**Baris 188:** Teks Hex seperti `"A1B2C3D4E5F6A7B8"` (16 karakter hex) diubah jadi string biner 64 karakter (`"1010000110110010..."`).

Fungsi `hex2bin()` dari `des_utils.py`:
```python
# des_utils.py, Baris 1-2
def hex2bin(s):
    return bin(int(s, 16))[2:].zfill(len(s) * 4)
```
- `int(s, 16)` → Ubah hex jadi desimal.
- `bin(...)` → Ubah desimal jadi biner (awalan `0b`).
- `[2:]` → Buang awalan `0b`.
- `.zfill(len(s) * 4)` → Pastikan panjangnya pas (1 hex = 4 biner, maka 16 hex = 64 biner).

**Baris 189: `plain_bytes = bytearray()`** — `bytearray` adalah versi "bisa diedit" dari tipe `bytes`. Digunakan sebagai keranjang kosong karena kita akan terus menambahkan data ke dalamnya (menggunakan `.extend()`).

---

## Langkah B3: Ban Berjalan Dekripsi (`decrypt_message`, Baris 191-196)

```python
# Baris 191: Looping — memotong biner per 64-bit (= 8 Byte)
for i in range(0, len(cipher_bin), 64):

    # Baris 192: Mengambil potongan 64-bit
    block_bin = cipher_bin[i:i+64]

    # Baris 193-194: Pengaman — jika potongan terakhir kurang dari 64-bit, hentikan
    if len(block_bin) < 64:
        break

    # Baris 195: Memasukkan ke MESIN YANG SAMA dengan kunci TERBALIK!
    plain_bin = process_block(block_bin, keys)

    # Baris 196: Mengubah biner hasil dekripsi jadi Byte, tambahkan ke keranjang
    plain_bytes.extend(des_utils.bin2bytes(plain_bin))
```

### Penjelasan Detail:

**Baris 191: `for i in range(0, len(cipher_bin), 64):`**
Berbeda dengan enkripsi yang melompat per 8 (Byte), di sini lompatannya per **64** (karena datanya sudah berbentuk biner, dan 8 Byte = 64-bit).

**Baris 193-194: `if len(block_bin) < 64: break`**
Pengaman. Jika ternyata sisa potongan terakhir kurang dari 64 karakter biner (potongan cacat/rusak), looping dihentikan paksa (`break`) daripada memproses data yang tidak lengkap.

**Baris 195: `plain_bin = process_block(block_bin, keys)`**
Perhatikan: fungsi yang dipanggil adalah **`process_block`** — mesin yang **sama persis** dengan yang dipakai saat enkripsi! Tidak ada fungsi `process_block_decrypt` atau semacamnya. Yang berbeda hanyalah isi variabel `keys` yang sudah dibalik urutannya (`K16` pertama, `K1` terakhir).

Karena kunci dibalik, setiap putaran Feistel di dalam `process_block` secara matematis **membatalkan** (undo) apa yang dilakukan oleh putaran Feistel saat enkripsi. Mangkuk Kiri dan Kanan yang diacak-acak tadi pelan-pelan kembali ke posisi aslinya.

**Baris 196: `plain_bytes.extend(des_utils.bin2bytes(plain_bin))`**
Biner 64-bit yang sudah kembali ke bentuk aslinya diubah jadi angka-angka Byte (menggunakan `bin2bytes`), lalu ditambahkan ke keranjang `plain_bytes`.

---

## Langkah B4: Membuang Ganjalan & Menampilkan Teks Asli (`decrypt_message`, Baris 198-199)

```python
# Baris 198: Membuang padding
unpadded_bytes = des_utils.unpad(plain_bytes)

# Baris 199: Mengubah Byte kembali jadi teks yang bisa dibaca manusia
return unpadded_bytes.decode('utf-8', errors='ignore')
```

### Penjelasan Detail:

**Baris 198:** Ingat, saat enkripsi kita menambahkan ganjalan `[04, 04, 04, 04]` di belakang kata "HALO". Ganjalan ini masih ada di `plain_bytes`. Fungsi `unpad()` membaca byte terakhir (`04`), lalu memotong 4 byte terakhir. Tersisalah Byte murni dari kata "HALO".

**Baris 199: `.decode('utf-8', errors='ignore')`** 
Mengubah angka-angka Byte kembali menjadi huruf abjad:
```
72 → H,  65 → A,  76 → L,  79 → O
```
Parameter `errors='ignore'` adalah jaring pengaman. Jika ada 1-2 bit yang rusak saat transmisi jaringan (menyebabkan angka Byte-nya tidak cocok dengan huruf manapun), Python tidak akan *crash*. Ia akan melewati huruf yang rusak tersebut dan melanjutkan sisanya.

Hasilnya: **String `"HALO"` ditampilkan di terminal teman Anda!** 🎉

---

## Rangkuman Visual Keseluruhan Alur Enkripsi-Dekripsi

```
╔══════════════════════════════════════════════════════════════════╗
║                        KOMPUTER PENGIRIM                        ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   User mengetik: "HALO"                                         ║
║        │                                                         ║
║        ▼                                                         ║
║   [encode] → Byte: [72, 65, 76, 79]                            ║
║        │                                                         ║
║        ▼                                                         ║
║   [pad] → Byte: [72, 65, 76, 79, 04, 04, 04, 04]              ║
║        │                                                         ║
║        ▼                                                         ║
║   [bytes2bin] → Biner 64-bit                                    ║
║        │                                                         ║
║        ▼                                                         ║
║   ┌─────────────── process_block ───────────────┐               ║
║   │  1. Acak posisi (Tabel IP)                  │               ║
║   │  2. Belah jadi L (32-bit) dan R (32-bit)    │               ║
║   │  3. 16x Putaran Feistel:                    │               ║
║   │     ┌─────────── feistel() ──────────┐      │               ║
║   │     │ a. Expansion  (32→48 bit)      │      │               ║
║   │     │ b. XOR dengan Anak Kunci       │      │  keys =       ║
║   │     │ c. S-BOX      (48→32 bit)      │◄─────┤  [K1→K16]    ║
║   │     │ d. Permutasi P                 │      │               ║
║   │     └────────────────────────────────┘      │               ║
║   │  4. Swap (R + L)                            │               ║
║   │  5. Acak posisi (Tabel IP_INV)              │               ║
║   └─────────────────────┬───────────────────────┘               ║
║                         │                                        ║
║                         ▼                                        ║
║   [bin2hex] → Ciphertext: "A1B2C3D4E5F6A7B8"                   ║
║                         │                                        ║
║                         ▼                                        ║
║              ══ KIRIM VIA TCP SOCKET ══                          ║
╚═════════════════════════╪════════════════════════════════════════╝
                          │
            ══════════════╪══════════════
                 JARINGAN INTERNET
            (data yang lewat = Ciphertext)
            ══════════════╪══════════════
                          │
╔═════════════════════════╪════════════════════════════════════════╗
║                         ▼                                        ║
║              ══ TERIMA VIA TCP SOCKET ══                         ║
║                         │                                        ║
║                         ▼                                        ║
║   [hex2bin] → Biner 64-bit                                      ║
║                         │                                        ║
║                         ▼                                        ║
║   ┌─────────────── process_block ───────────────┐               ║
║   │  MESIN YANG SAMA PERSIS!                    │               ║
║   │  1. Acak posisi (Tabel IP)                  │               ║
║   │  2. Belah jadi L (32-bit) dan R (32-bit)    │               ║
║   │  3. 16x Putaran Feistel:                    │               ║
║   │     ┌─────────── feistel() ──────────┐      │               ║
║   │     │ a. Expansion  (32→48 bit)      │      │  keys =       ║
║   │     │ b. XOR dengan Anak Kunci       │      │  [K16→K1]    ║
║   │     │ c. S-BOX      (48→32 bit)      │◄─────┤  TERBALIK!   ║
║   │     │ d. Permutasi P                 │      │               ║
║   │     └────────────────────────────────┘      │               ║
║   │  4. Swap (R + L)                            │               ║
║   │  5. Acak posisi (Tabel IP_INV)              │               ║
║   └─────────────────────┬───────────────────────┘               ║
║                         │                                        ║
║                         ▼                                        ║
║   [bin2bytes] → Byte: [72, 65, 76, 79, 04, 04, 04, 04]         ║
║                         │                                        ║
║                         ▼                                        ║
║   [unpad] → Byte: [72, 65, 76, 79]                              ║
║                         │                                        ║
║                         ▼                                        ║
║   [decode] → Teks: "HALO"  ← PESAN ASLI KEMBALI! 🎉            ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                       KOMPUTER PENERIMA                          ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Catatan Penting untuk Demo

Jika asdos bertanya *"Jelaskan perbedaan proses enkripsi dan dekripsi di program DES kamu!"*, jawab:

> "Enkripsi dan dekripsi di program kami menggunakan **fungsi `process_block` yang sama persis 100%**, Kak. Ini dimungkinkan oleh arsitektur Feistel Network. Satu-satunya perbedaan adalah **urutan Subkey-nya dibalik**. Saat enkripsi, Subkey dipakai berurutan dari K1 sampai K16. Saat dekripsi, kita cukup memanggil `keys.reverse()` sehingga urutannya menjadi K16 mundur sampai K1. Karena sifat operasi XOR yang *self-inverse* (jika di-XOR dua kali dengan kunci yang sama akan kembali ke semula), mesin yang sama dengan kunci terbalik secara otomatis merajut kembali Ciphertext menjadi Plaintext."

---

*← Kembali ke **Part 1: Perjalanan Kunci (Key Schedule)***
