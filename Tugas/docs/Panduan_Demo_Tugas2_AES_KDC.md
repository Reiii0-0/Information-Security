# 📘 PANDUAN DEMO & BEDAH MATERI TUGAS 2: KDC 5-STEP & AES-128 MANUAL

Dokumen ini disusun khusus untuk persiapan demo individual di depan dosen/asisten. Seluruh penjelasan teoritis dan matematis ditempatkan di sini agar file `.py` di dalam `Tugas/2/` tetap bersih dari komentar berlebihan (sesuai Ketentuan #7).

---

## 🚀 BAGIAN 1: SKENARIO EKSEKUSI DEMO (3 IP ADDRESS BERBEDA)

Topologi jaringan pada `docker-compose.yml` menggunakan subnet `172.28.0.0/24` dengan **3 IP statis berbeda**:
* **KDC Server (`ki_kdc`):** `172.28.0.10` (Port `5000`)
* **Alice Initiator (`ki_alice`):** `172.28.0.11`
* **Bob Responder (`ki_bob`):** `172.28.0.12` (Port `5001`)

### Langkah 0: Siapkan Wireshark Sebelum Demo
1. Jalankan container terlebih dahulu agar interface jaringan Docker terbentuk:
   ```bash
   cd Tugas/2
   docker compose up -d --build
   ```
2. Cari nama interface bridge Docker untuk subnet `172.28.0.0/24`:
   ```bash
   ip -o -4 addr show | grep 172.28.0.1
   ```
   *(Biasanya bernama `br-xxxxxxxxxxxx`, atau pilih interface **`any`** di Wireshark).*
3. Buka **Wireshark**, pilih interface tersebut, lalu masukkan **Display Filter** berikut:
   ```text
   ip.addr == 172.28.0.0/24 && (tcp.port == 5000 || tcp.port == 5001) && tcp.len > 0
   ```
   *(Filter `tcp.len > 0` menyembunyikan paket kosong ACK/SYN sehingga asisten hanya melihat paket data Langkah 1 s.d. 5 dan payload chat Hex secara bersih!)*

---

### Langkah 1: Jalankan 3 Terminal Entitas (Urutan: KDC $\rightarrow$ Bob $\rightarrow$ Alice)

**Terminal 1 — Jalankan KDC (`172.28.0.10`):**
```bash
docker exec -it ki_kdc python kdc.py
```
* Tekan **Enter** pada Port (`5000`), Master Key $K_a$ (`KDC_ALICE_KEY123`), dan Master Key $K_b$ (`KDC_BOB_KEY_4567`) — atau ketik kunci ASCII pilihan asisten.

**Terminal 2 — Jalankan Responder Bob (`172.28.0.12`):**
```bash
docker exec -it ki_bob python bob.py
```
* Tekan **Enter** pada Port (`5001`) dan Master Key $K_b$ (`KDC_BOB_KEY_4567`). Bob akan berstatus *mendengarkan koneksi*.

**Terminal 3 — Jalankan Initiator Alice (`172.28.0.11`):**
```bash
docker exec -it ki_alice python alice.py
```
* Tekan **Enter** pada IP KDC (`172.28.0.10`), Port KDC (`5000`), IP Bob (`172.28.0.12`), Port Bob (`5001`), dan Master Key $K_a$ (`KDC_ALICE_KEY123`).
* Begitu ditekan Enter, **Langkah 1 s.d. 5 otomatis berjalan** dan menampilkan log lengkap di ketiga terminal!

---

## 🧪 BAGIAN 2: SKENARIO PENGUJIAN INTERAKTIF SAAT DEMO (TANPA RESTART)

Jika asisten meminta pengujian variasi kunci di tengah demo:

1. **Cek Kunci Aktif di Masing-Masing Node:**
   Ketik `/keys` di terminal KDC, Alice, atau Bob.
2. **Uji Ganti Master Key & Rotasi Session Key Baru (`/rekey`):**
   * Di KDC: ketik `/setka KUNCI_ALICE_BARU`
   * Di Alice: ketik `/setmaster KUNCI_ALICE_BARU`
   * Di Alice: ketik `/rekey` $\rightarrow$ Alice akan meminta Session Key $K_s$ baru ke KDC dan menjalankan ulang Langkah 1–5 secara *live*!
3. **Uji Set Session Key Spesifik dari KDC:**
   * Di KDC: ketik `/setks KUNCI_SESI_DEMO1`
   * Di Alice: ketik `/rekey` $\rightarrow$ KDC akan membagikan `KUNCI_SESI_DEMO1` ke Alice dan Bob!
4. **Uji Simulasi Kunci Salah / Penyadap:**
   * Di Bob: ketik `/setkey KUNCI_SALAH_9999`
   * Kirim pesan dari Alice $\rightarrow$ Bob akan menampilkan `[!] Gagal dekripsi pesan Alice: Integritas padding PKCS#7 gagal`.
   * Kembalikan kunci dengan mengetik `/rekey` di Alice!

---

## 🧠 BAGIAN 3: JAWABAN PERTANYAAN LISAN DOSEN / ASISTEN (PAHAM LUAR KEPALA)

### 1. Bedah Protokol KDC 5 Langkah (Needham-Schroeder)
* **Langkah 1 ($A \rightarrow KDC$): `IDA || IDB || N1`**
  * *Mengapa ada Nonce $N_1$?* Untuk mencegah **Replay Attack**. Ketika KDC membalas di Langkah 2 dengan menyertakan $N_1$ di dalam amplop terenkripsi $K_a$, Alice yakin balasan tersebut adalah balasan segar untuk permintaannya saat ini, bukan rekaman paket lama yang diputar ulang oleh penyerang.
* **Langkah 2 ($KDC \rightarrow A$): `E(Ka, [Ks || IDA || IDB || N1]) || E(Kb, [Ks || IDA])`**
  * *Mengapa KDC mengirim tiket Bob ke Alice, bukan langsung ke Bob?* Agar alur komunikasi terpusat melalui inisiator (Alice) dan Alice dapat menyertakan tiket tersebut bersamaan saat membuka koneksi ke Bob. Alice **tidak bisa** membaca maupun mengubah isi tiket Bob karena dienkripsi dengan $K_b$.
  * *Mengapa `IDB` juga dimasukkan ke dalam amplop Alice?* Untuk mencegah *Man-in-the-Middle* mengganti tujuan di Langkah 1 (memastikan KDC membuat kunci memang untuk komunikasi dengan Bob).
* **Langkah 3 ($A \rightarrow B$): `E(Kb, [Ks || IDA])`**
  * Bob mendekripsi tiket menggunakan $K_b$, sehingga Bob mendapatkan $K_s$ dan mengetahui bahwa pengirimnya adalah `IDA` (Alice).
* **Langkah 4 ($B \rightarrow A$): `E(Ks, N2)` & Langkah 5 ($A \rightarrow B$): `E(Ks, f(N2))`**
  * *Mengapa masih perlu Langkah 4 dan 5 padahal Bob sudah dapat $K_s$ di Langkah 3?* Untuk mencegah **Replay Attack pada Langkah 3**! Tanpa Langkah 4–5, penyerang yang merekam tiket Langkah 3 kemarin bisa mengirim ulang tiket lama itu ke Bob hari ini dan berpura-pura menjadi Alice. Dengan menantang Alice mendekripsi nonce baru $N_2$ dan membalas $f(N_2) = N_2 - 1$ menggunakan $K_s$, Bob membuktikan bahwa lawan bicaranya saat ini benar-benar memegang $K_s$ secara *live*.

---

### 2. Bedah Algoritma AES-128 Manual (`aes_manual.py` & `aes_utils.py`)
* **Ukuran Blok & Kunci AES-128:**
  * Ukuran blok selalu **128-bit (16 byte)** yang disusun ke dalam matriks **State $4 \times 4$ byte secara *column-major*** (isi kolom ke bawah dulu, baru pindah kolom kanan).
  * Ukuran kunci 128-bit (16 karakter ASCII) menghasilkan **10 Ronde** (ditambah 1 Initial `AddRoundKey` di Ronde 0, sehingga total membutuhkan **11 Round Keys** atau 44 *words*).
* **4 Transformasi di Setiap Ronde Enkripsi:**
  1. `sub_bytes(state)`: Substitusi non-linear setiap byte menggunakan tabel **S-Box** ($16 \times 16 = 256$ elemen, invers perkalian di $GF(2^8)$ diikuti transformasi afin). Memberikan sifat **Confusion**.
  2. `shift_rows(state)`: Geser siklik ke kiri tiap baris matriks:
     * Baris 0: tidak digeser
     * Baris 1: geser kiri 1 byte
     * Baris 2: geser kiri 2 byte
     * Baris 3: geser kiri 3 byte
     *(Tujuannya menyebarkan byte antar kolom yang berbeda).*
  3. `mix_columns(state)`: Mengalikan setiap kolom dengan matriks tetap di dalam **Galois Field $GF(2^8)$** menggunakan fungsi `xtime` (polinomial irreduksibel $x^8 + x^4 + x^3 + x + 1$ atau `0x1B`). Memberikan sifat **Diffusion** (1 byte berubah akan mengubah seluruh 4 byte di kolom tersebut).
  4. `add_round_key(state, round_key)`: Operasi **XOR** byte-demi-byte antara matriks State dan *Round Key* saat ini.
* **Pertanyaan Favorit: *"Mengapa pada Ronde ke-10 (terakhir) tidak ada `MixColumns`?"***
  * Karena `MixColumns` di ronde terakhir tidak menambah keamanan kriptografis (hanya operasi linear yang langsung bisa dibalik sebelum XOR kunci terakhir), dan menghilangkannya membuat struktur enkripsi dan dekripsi menjadi simetris serta lebih efisien.
* **Bagaimana `key_expansion` Bekerja?**
  * Kunci awal 16 byte dibagi menjadi 4 *word* pertama ($W_0, W_1, W_2, W_3$), masing-masing 4 byte.
  * Untuk membentuk $W_i$ ($i = 4 \dots 43$):
    * Jika $i$ **bukan** kelipatan 4: $W_i = W_{i-4} \oplus W_{i-1}$.
    * Jika $i$ **kelipatan 4**: $W_{i-1}$ diputar kiri 1 byte (`RotWord`), disubstitusi dengan `S_BOX` (`SubWord`), lalu byte pertamanya di-XOR dengan konstanta ronde `RCON[(i // 4) - 1]`, baru di-XOR dengan $W_{i-4}$.
