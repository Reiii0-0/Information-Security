# 🔑 PART 1: Perjalanan Kunci Rahasia (Key Schedule)

## Pendahuluan

Algoritma DES (Data Encryption Standard) membutuhkan **16 buah Anak Kunci** yang berbeda-beda untuk mengenkripsi pesan. Padahal, *user* hanya memasukkan **1 buah Kunci Utama** (misalnya kata sandi `"RAHASIA1"`).

Dokumen ini menjelaskan secara sangat detail bagaimana kode kita mengubah 1 Kunci Utama menjadi 16 Anak Kunci, **baris demi baris**, beserta penjelasan setiap tabel yang digunakan.

---

## Langkah 0: Kunci Disiapkan (`encrypt_message`, Baris 166-169)

Sebelum masuk ke pabrik pembuat kunci, kunci mentah dari *user* harus dirapikan dulu.

```python
# Baris 166: Mengubah teks kunci jadi Byte, memastikan panjangnya TEPAT 8 karakter
key_bytes = key_text.encode('utf-8').ljust(8, b'0')[:8]

# Baris 168: Mengubah Byte menjadi deretan Biner (string '0' dan '1')
key_bin = des_utils.bytes2bin(key_bytes)

# Baris 169: Memasukkan biner kunci ke pabrik pembuat 16 Anak Kunci
keys = generate_keys(key_bin)
```

### Penjelasan Detail:

**Baris 166** melakukan 3 hal sekaligus dalam 1 baris:

1. `key_text.encode('utf-8')` — Teks kunci `"RAHASIA1"` diubah menjadi angka-angka Byte. Setiap huruf memiliki kode angka masing-masing (ASCII). Contoh: huruf `R` = 82, `A` = 65, `H` = 72, dst.

2. `.ljust(8, b'0')` — "Left Justify". Jika kunci yang diketik user kurang dari 8 huruf (misalnya cuma `"abc"` = 3 huruf), maka Python akan menambahkan karakter `'0'` di sebelah kanan sampai totalnya genap 8. Hasilnya: `"abc00000"`. Ini memastikan kunci **tidak pernah kurang** dari 8 karakter.

3. `[:8]` — Slicing. Jika sebaliknya, kunci yang diketik terlalu panjang (misalnya `"rahasia_sangat_panjang"` = 22 huruf), maka Python hanya akan mengambil 8 huruf pertama saja dan membuang sisanya. Ini memastikan kunci **tidak pernah lebih** dari 8 karakter.

Hasilnya: Kunci yang keluar dari baris ini **dijamin berukuran tepat 8 Byte = 64-bit**. Tidak kurang, tidak lebih.

**Baris 168** memanggil fungsi `bytes2bin()` dari file `des_utils.py`:

```python
# des_utils.py, Baris 7-8
def bytes2bin(b):
    return ''.join(format(byte, '08b') for byte in b)
```

Fungsi ini mengambil setiap Byte (misal angka 82 untuk huruf `R`), lalu mengubahnya menjadi string biner 8-digit: `"01010010"`. Dilakukan untuk semua 8 huruf, lalu disambung. Hasilnya adalah 1 string biner panjang berisi 64 karakter (`0` dan `1`).

Contoh untuk kunci `"RAHASIA1"`:
```
R        A        H        A        S        I        A        1
01010010 01000001 01001000 01000001 01010011 01001001 01000001 00110001
```
Total: **64-bit**. Inilah `key_bin`.

**Baris 169** melempar `key_bin` (64-bit) ke fungsi `generate_keys()`. Di sinilah perjalanan sesungguhnya dimulai!

---

## Langkah 1: Penyusutan Kunci dengan Tabel PC-1 (`generate_keys`, Baris 115-118)

```python
# Baris 115-116: Membuat fungsi dan menyiapkan lemari kosong untuk 16 Anak Kunci
def generate_keys(key_bin):
    keys = []

    # Baris 118: Melewatkan kunci 64-bit ke tabel PC1
    key_pc1 = permute(key_bin, PC1)
```

### Apa itu Tabel PC-1? (Baris 44-53)

```python
PC1 = [
    57, 49, 41, 33, 25, 17, 9,
    1,  58, 50, 42, 34, 26, 18,
    10, 2,  59, 51, 43, 35, 27,
    19, 11, 3,  60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7,  62, 54, 46, 38, 30, 22,
    14, 6,  61, 53, 45, 37, 29,
    21, 13, 5,  28, 20, 12, 4
]
```

**Fakta Penting:** Hitung jumlah angka di dalam tabel PC1. Jumlahnya ada **56 buah**. Padahal kunci yang masuk berukuran 64-bit. Artinya, 8-bit akan dibuang!

**Bit mana yang dibuang?** Bit urutan ke-8, 16, 24, 32, 40, 48, 56, dan 64. Angka-angka ini **tidak ada** di dalam tabel PC1. Delapan bit ini aslinya adalah *Parity Bit* (bit pengecekan error) yang fungsinya hanya untuk memastikan data tidak rusak saat ditransmisikan lewat kabel komputer di zaman 1970-an. Secara kriptografi, mereka tidak berguna.

**Bagaimana Cara Kerja Tabel Ini?** Tabel ini dibaca oleh fungsi `permute()`:

```python
# Baris 112-113
def permute(data, table):
    return ''.join(data[i-1] for i in table)
```

Bayangkan `data` (kunci 64-bit) adalah deretan 64 huruf yang berdiri berjejer, masing-masing bernomor urut 1 sampai 64:

```
Urutan:  1  2  3  4  5  6  7  8  9 10 11 12 ... 57 58 59 60 61 62 63 64
Nilai:   0  1  0  1  0  0  1  0  0  1  0  0 ...  1  0  1  1  0  1  0  1
```

Fungsi `permute` membaca tabel PC1 angka demi angka:
- Angka pertama PC1 = **57**. Fungsi mengambil bit urutan ke-57 dari kunci, yaitu `1`. Ditaruh di posisi pertama output.
- Angka kedua PC1 = **49**. Fungsi mengambil bit urutan ke-49, ditaruh di posisi kedua output.
- ...dan seterusnya sampai 56 angka habis.

**Kenapa ada `i-1`?** Karena penemu DES menomori bit mulai dari 1 (konvensi matematika), tapi Python menomori array mulai dari 0. Jadi angka 57 di tabel sebenarnya merujuk ke index `57-1 = 56` di Python.

**Hasil Langkah 1:** Variabel `key_pc1` sekarang berisi string biner sepanjang **56 karakter** (56-bit). Kunci telah menyusut, dan posisi bit-bitnya sudah teracak.

---

## Langkah 2: Pembelahan Kunci (`generate_keys`, Baris 120-121)

```python
# Baris 120: Mengambil 28 karakter pertama (dari index 0 sampai 27)
c0 = key_pc1[:28]

# Baris 121: Mengambil 28 karakter sisanya (dari index 28 sampai 55)
d0 = key_pc1[28:]
```

### Penjelasan Detail:

Kunci 56-bit tadi dipotong tepat di tengah-tengah menjadi dua bagian:
- **`c0`** = Separuh **Kiri** (28-bit). Disebut juga "C Register".
- **`d0`** = Separuh **Kanan** (28-bit). Disebut juga "D Register".

Sintaks Python `[:28]` artinya: "Ambil semua karakter dari awal sampai sebelum index ke-28 (yaitu index 0 hingga 27, total 28 karakter)."

Sintaks `[28:]` artinya: "Ambil semua karakter mulai dari index ke-28 sampai habis (yaitu index 28 hingga 55, total 28 karakter)."

Mulai dari sini, `c0` dan `d0` akan hidup terpisah. Mereka akan diputar-putar secara independen di dalam *looping* 16 kali berikutnya.

---

## Langkah 3: Looping 16 Kali — Geser dan Cetak (`generate_keys`, Baris 123-126)

Ini adalah jantung dari pabrik pembuat Anak Kunci.

```python
# Baris 123: Looping sebanyak 16 kali, mengambil angka dari tabel SHIFTS satu per satu
for shift in SHIFTS:

    # Baris 124: Menggeser c0 ke kiri sebanyak 'shift' langkah (Circular Left Shift)
    c0 = c0[shift:] + c0[:shift]

    # Baris 125: Menggeser d0 ke kiri sebanyak 'shift' langkah (Circular Left Shift)
    d0 = d0[shift:] + d0[:shift]

    # Baris 126: Menggabungkan c0 dan d0, lalu mencetak Anak Kunci dengan tabel PC2
    keys.append(permute(c0 + d0, PC2))
```

### Tabel SHIFTS (Baris 66)

```python
SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
```

Tabel ini berisi **16 angka** — satu angka untuk setiap putaran. Angka-angka ini menentukan **berapa langkah** `c0` dan `d0` harus bergeser ke kiri pada putaran tersebut.

- Putaran 1: geser **1** langkah
- Putaran 2: geser **1** langkah
- Putaran 3: geser **2** langkah
- Putaran 4: geser **2** langkah
- ...
- Putaran 9: geser **1** langkah
- ...
- Putaran 16: geser **1** langkah

**Fakta Menarik:** Jika Anda menjumlahkan semua angka di tabel SHIFTS: `1+1+2+2+2+2+2+2+1+2+2+2+2+2+2+1 = 28`. Angka 28 ini sama persis dengan panjang `c0` dan `d0`. Artinya, setelah 16 putaran selesai, kedua register telah menyelesaikan tepat **1 rotasi penuh** dan kembali ke posisi awalnya!

### Circular Left Shift — Bedah Mendalam (Baris 124)

```python
c0 = c0[shift:] + c0[:shift]
```

Ini adalah teknik Python yang sangat elegan untuk melakukan pergeseran melingkar.

**Contoh Konkret — Geser 1 Langkah:**

Misalkan `c0 = "1100101"` (7 karakter, disederhanakan) dan `shift = 1`.

```
c0[shift:]  →  c0[1:]  →  "100101"    (Ambil dari index 1 sampai habis)
c0[:shift]  →  c0[:1]  →  "1"         (Ambil dari awal sampai sebelum index 1)
```

Digabungkan: `"100101"` + `"1"` = **`"1001011"`**

Apa yang terjadi? Karakter paling kiri (`"1"`) **dicabut** dari depan dan **ditempelkan** di belakang. Semua karakter lainnya secara otomatis maju 1 langkah ke kiri.

```
Sebelum: [1] [1] [0] [0] [1] [0] [1]
          ↓ dicabut                ↓ ditempel di sini
Sesudah: [1] [0] [0] [1] [0] [1] [1]
```

**Contoh Konkret — Geser 2 Langkah:**

Misalkan `c0` sekarang nilainya `"1001011"` dan `shift = 2`.

```
c0[shift:]  →  c0[2:]  →  "01011"     (Ambil dari index 2 sampai habis)
c0[:shift]  →  c0[:2]  →  "10"        (Ambil 2 karakter dari awal)
```

Digabungkan: `"01011"` + `"10"` = **`"0101110"`**

Dua karakter paling kiri (`"10"`) dicabut dan ditempel di belakang.

```
Sebelum: [1] [0] [0] [1] [0] [1] [1]
          ↓   ↓  dicabut          ↓ ditempel di sini
Sesudah: [0] [1] [0] [1] [1] [1] [0]
```

**Poin Penting:**
- Apakah `c0` dan `d0` digeser ke arah yang sama? **YA.** Keduanya sama-sama digeser ke **kiri**.
- Apakah seluruh 28-bit ikut bergeser? **YA.** Seluruh 28-bit bergeser serentak, bukan sebagian saja.
- Apakah ada data yang hilang? **TIDAK.** Bit yang jatuh dari ujung kiri muncul lagi di ujung kanan (melingkar). Maka disebut *Circular* (Melingkar).
- `c0` dan `d0` bergeser secara **mandiri** (masing-masing berputar di roda mereka sendiri).

### Menggabungkan dan Mencetak Anak Kunci — Tabel PC-2 (Baris 126)

Setelah `c0` dan `d0` selesai digeser pada putaran tersebut, mereka digabungkan kembali:

```python
keys.append(permute(c0 + d0, PC2))
```

**`c0 + d0`** — Operator `+` pada string di Python artinya menyambung. Kiri (28-bit) disambung dengan Kanan (28-bit) menjadi satu string panjang **56-bit**.

**`permute(..., PC2)`** — String 56-bit tadi dilewatkan ke tabel PC2.

### Apa itu Tabel PC-2? (Baris 55-64)

```python
PC2 = [
    14, 17, 11, 24, 1,  5,
    3,  28, 15, 6,  21, 10,
    23, 19, 12, 4,  26, 8,
    16, 7,  27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]
```

**Fakta Penting:** Hitung jumlah angka di dalam tabel PC2. Jumlahnya ada **48 buah**. Padahal data yang masuk berukuran 56-bit. Artinya, tabel PC2 akan **membuang 8-bit lagi** dan hanya mengambil 48-bit.

Cara kerjanya sama persis dengan PC1:
- Angka pertama = **14**. Ambil bit urutan ke-14 dari gabungan `c0+d0`, taruh di posisi pertama output.
- Angka kedua = **17**. Ambil bit urutan ke-17, taruh di posisi kedua output.
- ...dan seterusnya sampai 48 angka habis.

8 bit yang tidak ada di tabel PC2 (yaitu bit urutan ke-9, 18, 22, 25, 35, 38, 43, 54) **dibuang** dan tidak masuk ke Anak Kunci. Bit mana yang dibuang berbeda-beda posisinya di setiap putaran karena `c0` dan `d0` terus bermutasi akibat pergeseran.

**`keys.append(...)`** — Anak Kunci 48-bit yang baru dicetak ini dimasukkan ke dalam laci (list) `keys`. Fungsi `append` artinya "tambahkan di urutan paling belakang".

Proses **geser → gabung → cetak** ini diulang terus-menerus sebanyak 16 kali. Karena setiap putaran menggeser `c0` dan `d0` dengan jumlah langkah yang berbeda-beda, maka 56-bit yang masuk ke PC2 selalu berubah bentuknya. Akibatnya, 16 Anak Kunci yang dicetak **pasti berbeda-beda semua meskipun berasal dari Kunci Utama yang sama!**

---

## Langkah 4: Mengembalikan 16 Anak Kunci (`generate_keys`, Baris 127)

```python
# Baris 127: Mengembalikan laci berisi 16 Anak Kunci ke pemanggil fungsi
return keys
```

Setelah 16 kali *looping* selesai, variabel `keys` sekarang berisi:
```
keys = [
    K1  (48-bit),   # Anak Kunci untuk Putaran Feistel ke-1
    K2  (48-bit),   # Anak Kunci untuk Putaran Feistel ke-2
    K3  (48-bit),   # Anak Kunci untuk Putaran Feistel ke-3
    ...
    K16 (48-bit),   # Anak Kunci untuk Putaran Feistel ke-16
]
```

Laci ini dikembalikan (`return`) ke fungsi pemanggil (`encrypt_message`). Ke-16 Anak Kunci ini sekarang siap digunakan di dalam mesin Feistel untuk menghancurkan pesan asli menjadi *Ciphertext*.

---

## Rangkuman Visual Alur Key Schedule

```
┌─────────────────────────────────────────────────────────┐
│                    INPUT: KUNCI USER                     │
│                     "RAHASIA1"                           │
│                     (8 huruf)                            │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │    encode() + ljust + [:8]  │
        │   Ubah ke Byte, paksa 8    │
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │        bytes2bin()          │
        │   Ubah Byte → Biner        │
        │   Hasil: 64-bit            │
        └─────────────┬───────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │       Tabel PC-1            │
        │   Buang 8 Parity Bit       │
        │   Acak posisi              │
        │   64-bit → 56-bit          │
        └─────────────┬───────────────┘
                      │
               ┌──────┴──────┐
               │  Belah Dua  │
               ▼             ▼
           ┌───────┐     ┌───────┐
           │  C0   │     │  D0   │
           │ 28-bit│     │ 28-bit│
           └───┬───┘     └───┬───┘
               │             │
    ┌──────────┴─────────────┴──────────┐
    │     LOOPING 16 KALI (PUTARAN)     │
    │                                    │
    │  ┌──────────────────────────────┐  │
    │  │ 1. Geser C0 ke kiri         │  │
    │  │    (sesuai tabel SHIFTS)     │  │
    │  │ 2. Geser D0 ke kiri         │  │
    │  │    (sesuai tabel SHIFTS)     │  │
    │  └──────────────┬───────────────┘  │
    │                 │                  │
    │                 ▼                  │
    │  ┌──────────────────────────────┐  │
    │  │ 3. Gabungkan C0 + D0        │  │
    │  │    Hasil: 56-bit            │  │
    │  └──────────────┬───────────────┘  │
    │                 │                  │
    │                 ▼                  │
    │  ┌──────────────────────────────┐  │
    │  │ 4. Tabel PC-2               │  │
    │  │    Buang 8-bit, acak posisi │  │
    │  │    56-bit → 48-bit          │  │
    │  │    = 1 ANAK KUNCI (Subkey)  │  │
    │  └──────────────┬───────────────┘  │
    │                 │                  │
    │                 ▼                  │
    │  ┌──────────────────────────────┐  │
    │  │ 5. Simpan ke laci (keys)    │  │
    │  └──────────────────────────────┘  │
    │                                    │
    │    (Ulangi dari langkah 1 dengan   │
    │     C0 dan D0 yang sudah digeser)  │
    └────────────────┬───────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────┐
    │          OUTPUT: LACI KUNCI        │
    │                                    │
    │   K1  = 48-bit  (Putaran 1)       │
    │   K2  = 48-bit  (Putaran 2)       │
    │   K3  = 48-bit  (Putaran 3)       │
    │   ...                              │
    │   K16 = 48-bit  (Putaran 16)      │
    │                                    │
    │   Total: 16 Anak Kunci berbeda    │
    └────────────────────────────────────┘
```

---

## Catatan Penting untuk Demo

Jika asdos bertanya *"Jelaskan proses Key Schedule di program DES kamu!"*, Anda cukup menjawab:

> "Kunci yang dimasukkan user berukuran 64-bit, Kak. Pertama, kunci ini dilewatkan ke tabel PC-1 yang membuang 8 parity bit sehingga menyisakan 56-bit. Kemudian 56-bit ini dibelah jadi dua register masing-masing 28-bit, yaitu C dan D. Lalu kita masuk ke looping 16 kali, di mana setiap putaran: C dan D digeser ke kiri (Circular Left Shift) sesuai jadwal tabel SHIFTS, digabungkan kembali jadi 56-bit, lalu ditekan ke tabel PC-2 yang mengambil 48-bit darinya. Hasil cetakan 48-bit itulah Subkey untuk putaran tersebut. Setelah 16 putaran selesai, kita mendapatkan 16 Subkey berbeda yang siap digunakan di Feistel Network."

---

*Lanjut ke **Part 2: Perjalanan Pesan (Enkripsi & Dekripsi)** →*
