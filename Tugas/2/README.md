# Tugas 2 Keamanan Informasi: Key Distribution Scenario (KDC) & Manual AES

Proyek implementasi skenario distribusi kunci simetris (**Key Distribution Center - KDC**) dan enkripsi komunikasi pesan dua arah menggunakan algoritma **Advanced Encryption Standard (AES) Murni** tanpa library eksternal.

---

## 🎯 Spesifikasi & Ketentuan Tugas

1. **3 Entitas Berbeda (3 IP Address):**
   - **KDC (Key Distribution Center):** Server pihak ketiga tepercaya pemegang *master key* $K_a$ dan $K_b$.
   - **Alice (Initiator / Node A):** Penginisiasi sesi komunikasi.
   - **Bob (Responder / Node B):** Penerima inisiasi komunikasi.
   - Harus berjalan di **3 alamat IP berbeda** (misal: 3 perangkat fisik via LAN/WiFi, atau multi-container/VM).

2. **Protokol Key Distribution (5 Langkah):**
   - **Langkah 1 ($A \rightarrow KDC$):** $ID_A \parallel ID_B \parallel N_1$
   - **Langkah 2 ($KDC \rightarrow A$):** $E(K_a, [K_s \parallel ID_A \parallel ID_B \parallel N_1]) \parallel E(K_b, [K_s \parallel ID_A])$
   - **Langkah 3 ($A \rightarrow B$):** $E(K_b, [K_s \parallel ID_A])$
   - **Langkah 4 ($B \rightarrow A$):** $E(K_s, N_2)$ *(Authentication Challenge)*
   - **Langkah 5 ($A \rightarrow B$):** $E(K_s, f(N_2))$ *(Challenge Response, misal $f(N_2) = N_2 - 1$)*

3. **Komunikasi Dua Arah (Full-Duplex):**
   - Setelah langkah 5 selesai, Alice dan Bob dapat saling mengirim dan menerima pesan secara asinkron (dua arah).
   - Enkripsi pesan menggunakan session key $K_s$ dengan algoritma **AES**.

4. **Format Data:**
   - **Plaintext & Key:** Format teks ASCII / UTF-8.
   - **Ciphertext di Jaringan:** Format Hexadecimal (Hex string).
   - Kunci dapat diubah secara dinamis dan tidak di-*hardcode*.

5. **Ketentuan Kode & Demo:**
   - **AES & KDC Murni/Manual:** Dilarang menggunakan library kripto (`pycryptodome`, `cryptography`, dll).
   - **Wireshark Ready:** Menyiapkan filter interface jaringan untuk membuktikan data terenkripsi (Hex) saat transmisi.
   - **Demo Tanpa Catatan:** Memahami seluruh proses matematis dan arsitektur kode.

---

## 📁 Rencana Struktur File Tugas 2

```text
Tugas/2/
├── aes_manual.py       # Core Engine AES (SubBytes, ShiftRows, MixColumns, AddRoundKey, KeyExpansion)
├── aes_utils.py        # Utilitas konversi bit/hex/bytes & PKCS#7 padding
├── kdc.py              # Server KDC penghasil session key Ks & tiket enkripsi
├── alice.py            # Node Alice (Initiator handshake & terminal chat)
├── bob.py              # Node Bob (Responder handshake & terminal chat)
├── docker-compose.yml  # Opsi virtualisasi 3 node dengan 3 IP statis
└── README.md           # Panduan eksekusi & pengujian
```

---

## ⏳ Alur Pengerjaan & Timeline Deadline

> **🚨 HARD DEADLINE PENGUMPULAN:** **Selasa, 27 Oktober 2026 pukul 23.59 WIB**  
> **Link Pengumpulan:** [Google Form Pengumpulan Tugas 2](https://forms.gle/eS1wGZJM6yjHScKa7)

| Fase | Target Tanggal | Fokus Utama | Luaran / Output |
| :--- | :--- | :--- | :--- |
| **Fase 1** | **Sabtu, 24 Okt 2026** | **Core AES-128 Manual** | `aes_manual.py` lolos uji enkripsi & dekripsi NIST |
| **Fase 2** | **Minggu, 25 Okt 2026** | **KDC & Socket Handshake** | Handshake 5 langkah sukses bertukar tiket $K_s$ |
| **Fase 3** | **Senin, 26 Okt 2026** | **Chat 2 Arah & 3 IP Address** | Alice & Bob chat bolak-balik antar 3 IP berbeda |
| **Fase 4** | **Selasa, 27 Okt 2026** | **Wireshark, Final Review & Submit** | Rekam Wireshark, hapus komentar contekan, kumpul GForm |

---

## 📋 Checklist To-Do Proyek (Task List)

### 🔹 Fase 1: Engine AES Manual (24 Okt 2026)
- [ ] Buat tabel S-Box & Inverse S-Box standar AES (`aes_manual.py`)
- [ ] Implementasi algoritma *Key Expansion* (menghasilkan 11 round keys 128-bit)
- [ ] Implementasi 4 transformasi ronde: `SubBytes`, `ShiftRows`, `MixColumns`, `AddRoundKey`
- [ ] Implementasi operasi inverse dekripsi: `InvSubBytes`, `InvShiftRows`, `InvMixColumns`
- [ ] Implementasi utilitas PKCS#7 padding & konversi string ASCII $\leftrightarrow$ Hex
- [ ] Unit testing: Validasi hasil enkripsi & dekripsi dengan NIST test vector

### 🔹 Fase 2: Skenario Distribusi Kunci KDC (25 Okt 2026)
- [ ] Buat program `kdc.py`: simpan master key $K_a$ dan $K_b$, generator $K_s$ acak
- [ ] Implementasi **Langkah 1 ($A \rightarrow KDC$)**: Request inisiasi ($ID_A \parallel ID_B \parallel N_1$)
- [ ] Implementasi **Langkah 2 ($KDC \rightarrow A$)**: Paket terenkripsi $K_a$ dan tiket $K_b$
- [ ] Implementasi **Langkah 3 ($A \rightarrow B$)**: Alice meneruskan tiket ke Bob
- [ ] Implementasi **Langkah 4 & 5 (Mutual Auth)**: Challenge $N_2$ & respons $f(N_2) = N_2 - 1$
- [ ] Verifikasi Bob dan Alice berhasil mendapatkan session key $K_s$ yang identik

### 🔹 Fase 3: Komunikasi Dua Arah & Uji Jaringan 3 IP (26 Okt 2026)
- [ ] Implementasi threading socket di `alice.py` dan `bob.py` (bisa kirim & terima asinkron)
- [ ] Integrasikan enkripsi pesan chat dengan AES manual menggunakan session key $K_s$
- [ ] Tampilkan ciphertext di layar pengirim dan penerima dalam format **Hexadecimal**
- [ ] Fitur interaktif: CLI untuk mengubah pesan dan mengganti key secara dinamis
- [ ] Buat `docker-compose.yml` (3 container: `kdc`, `alice`, `bob` dengan IP statis 172.28.0.x)
- [ ] Uji coba komunikasi antar 3 IP address yang berbeda

### 🔹 Fase 4: Validasi Wireshark, Pembersihan & Pengumpulan (27 Okt 2026)
- [ ] Setup Wireshark: pasang filter port & buktikan payload yang lewat adalah Hex ciphertext
- [ ] Pastikan tidak ada kebocoran plaintext di paket jaringan Wireshark
- [ ] Audit kode: bersihkan komentar contekan yang menyerupai catatan (sesuai aturan dosen)
- [ ] Pastikan riwayat commit mencerminkan kontribusi kedua anggota tim
- [ ] Push commit final ke repositori GitHub `Reiii0-0/Information-Security`
- [ ] Submit link repositori ke [Google Form](https://forms.gle/eS1wGZJM6yjHScKa7) sebelum 23.59 WIB
