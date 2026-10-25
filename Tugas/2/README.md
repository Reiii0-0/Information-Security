# Tugas 2 Keamanan Informasi: Key Distribution Scenario (KDC) & Manual AES

Implementasi skenario distribusi kunci simetris (**Key Distribution Center - KDC**) 5 langkah (Needham-Schroeder) dan komunikasi pesan dua arah (*full-duplex*) menggunakan algoritma **Advanced Encryption Standard (AES-128) Murni** tanpa library kriptografi eksternal.

---

## 🎯 Spesifikasi & Arsitektur Sistem

1. **3 Entitas Berbeda (3 IP Address):**
   - **KDC (`172.28.0.10:5000`):** Server pihak ketiga tepercaya pemegang *master key* $K_a$ dan $K_b$ serta generator *session key* $K_s$.
   - **Alice (`172.28.0.11`):** Initiator (Node A) yang memulai request ke KDC dan membuka sesi ke Bob.
   - **Bob (`172.28.0.12:5001`):** Responder (Node B) yang memvalidasi tiket KDC dan melakukan *mutual authentication*.

2. **Protokol Key Distribution & Mutual Authentication (5 Langkah):**
   - **Langkah 1 ($A \rightarrow KDC$):** `IDA || IDB || N1` (Plaintext ASCII)
   - **Langkah 2 ($KDC \rightarrow A$):** $E(K_a, [K_s \parallel ID_A \parallel ID_B \parallel N_1]) \parallel E(K_b, [K_s \parallel ID_A])$ (Hex)
   - **Langkah 3 ($A \rightarrow B$):** $E(K_b, [K_s \parallel ID_A])$ (Hex)
   - **Langkah 4 ($B \rightarrow A$):** $E(K_s, N_2)$ *(Authentication Challenge - Hex)*
   - **Langkah 5 ($A \rightarrow B$):** $E(K_s, f(N_2))$ dengan $f(N_2) = N_2 - 1$ *(Challenge Response - Hex)*

3. **Komunikasi Dua Arah & Interaktivitas Tanpa Restart:**
   - Setelah Langkah 5 terverifikasi, Alice dan Bob dapat saling mengirim dan menerima pesan secara simultan (*full-duplex*) dengan enkripsi AES-128 menggunakan $K_s$.
   - Mendukung perintah interaktif *live* di terminal:
     - `/keys` : Melihat kunci aktif ($K_a / K_b / K_s$).
     - `/setkey <ks_baru>` : Mengubah Session Key $K_s$ secara dinamis tanpa mematikan program.
     - `/setmaster <k_baru>` : Mengubah Master Key $K_a$ / $K_b$ secara dinamis.
     - `/rekey` : **(Fitur Bonus)** Meminta Session Key $K_s$ baru ke KDC dan menjalankan ulang Langkah 1–5 secara *live*.

---

## 📂 Struktur File

```text
Tugas/2/
├── aes_manual.py       # Core Engine AES-128 Murni (SubBytes, ShiftRows, MixColumns, AddRoundKey, KeyExpansion)
├── aes_utils.py        # Utilitas konversi matriks 4x4, PKCS#7 padding 16-byte, & Galois Field GF(2^8)
├── kdc.py              # Server KDC penghasil session key Ks & enkripsi tiket Langkah 1-2
├── alice.py            # Node Initiator A (Handshake Langkah 1-5, /rekey, & Full-Duplex AES Chat)
├── bob.py              # Node Responder B (Verifikasi Langkah 3-5 & Full-Duplex AES Chat)
├── Dockerfile          # Image container Python 3
├── docker-compose.yml  # Orkestrasi 3 node dengan 3 IP statis (172.28.0.10, .11, .12)
├── termux_setup.sh     # Skrip eksekusi cepat untuk perangkat fisik kedua/ketiga (Termux/LAN)
└── README.md           # Dokumentasi eksekusi & pengujian
```

---

## 🚀 Cara Menjalankan (Mode 3 IP via Docker Compose)

```bash
cd Tugas/2
docker compose up -d --build

# Terminal 1 - KDC Server (IP: 172.28.0.10, Port: 5000)
docker exec -it ki_kdc python kdc.py

# Terminal 2 - Responder Bob (IP: 172.28.0.12, Port: 5001)
docker exec -it ki_bob python bob.py

# Terminal 3 - Initiator Alice (IP: 172.28.0.11)
docker exec -it ki_alice python alice.py
```

### Filter Wireshark untuk Demo:
```text
ip.addr == 172.28.0.0/24 && (tcp.port == 5000 || tcp.port == 5001) && tcp.len > 0
```

Panduan skenario demo selengkapnya dan penjelasan matematis tersedia di [../docs/Panduan_Demo_Tugas2_AES_KDC.md](../docs/Panduan_Demo_Tugas2_AES_KDC.md).

---

## 📋 Status Checklist Proyek

### 🔹 Fase 1: Engine AES Manual
- [x] Buat tabel S-Box & Inverse S-Box standar AES (`aes_manual.py`)
- [x] Implementasi algoritma *Key Expansion* (menghasilkan 11 round keys 128-bit)
- [x] Implementasi 4 transformasi ronde: `SubBytes`, `ShiftRows`, `MixColumns`, `AddRoundKey`
- [x] Implementasi operasi inverse dekripsi: `InvSubBytes`, `InvShiftRows`, `InvMixColumns`
- [x] Implementasi utilitas PKCS#7 padding & konversi string ASCII $\leftrightarrow$ Hex
- [x] Unit testing: Validasi hasil enkripsi & dekripsi dengan NIST test vector

### 🔹 Fase 2: Skenario Distribusi Kunci KDC
- [x] Buat program `kdc.py`: simpan master key $K_a$ dan $K_b$, generator $K_s$ acak
- [x] Implementasi **Langkah 1 ($A \rightarrow KDC$)**: Request inisiasi ($ID_A \parallel ID_B \parallel N_1$)
- [x] Implementasi **Langkah 2 ($KDC \rightarrow A$)**: Paket terenkripsi $K_a$ dan tiket $K_b$
- [x] Implementasi **Langkah 3 ($A \rightarrow B$)**: Alice meneruskan tiket ke Bob
- [x] Implementasi **Langkah 4 & 5 (Mutual Auth)**: Challenge $N_2$ & respons $f(N_2) = N_2 - 1$
- [x] Verifikasi Bob dan Alice berhasil mendapatkan session key $K_s$ yang identik

### 🔹 Fase 3: Komunikasi Dua Arah & Uji Jaringan 3 IP
- [x] Implementasi threading socket di `alice.py` dan `bob.py` (bisa kirim & terima asinkron)
- [x] Integrasikan enkripsi pesan chat dengan AES manual menggunakan session key $K_s$
- [x] Tampilkan ciphertext di layar pengirim dan penerima dalam format **Hexadecimal**
- [x] Fitur interaktif: CLI untuk mengubah pesan dan mengganti key secara dinamis
- [x] Buat `docker-compose.yml` (3 container: `kdc`, `alice`, `bob` dengan IP statis 172.28.0.x)
- [x] Uji coba komunikasi antar 3 IP address yang berbeda

### 🔹 Fase 4: Validasi Wireshark, Pembersihan & Dokumentasi
- [x] Setup filter Wireshark & verifikasi payload jaringan berupa Hex ciphertext
- [x] Pastikan tidak ada kebocoran plaintext di paket jaringan
- [x] Audit kode: pastikan bebas dari komentar contekan sesuai aturan dosen
