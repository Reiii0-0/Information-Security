# Keamanan Informasi (Information Security)

Repository perkuliahan dan penugasan proyek **Keamanan Informasi (KI)** - Departemen Teknik Informatika, Fakultas FTEIC, Institut Teknologi Sepuluh Nopember (ITS).

---

## 📁 Struktur Direktori

```text
.
├── Materi/                                 # Bahan ajar & slide resmi perkuliahan
│   ├── KI 01.pdf                           # Pengantar Keamanan Informasi & Prinsip CIA
│   ├── KI 02.pdf                           # Kriptografi Klasik (Symmetric Ciphers)
│   ├── KI 03.pdf                           # Block Ciphers & Data Encryption Standard (DES)
│   ├── KI 04.pdf                           # Advanced Encryption Standard (AES)
│   ├── KI 12.pdf                           # Keamanan Jaringan & Protokol Komunikasi
│   └── KI 14.pdf                           # Manajemen Kunci & Otentikasi Digital
│
├── Tugas/                                  # Penugasan & Proyek Praktik
│   ├── 1/                                  # [Tugas 1] P2P Secure Chat menggunakan DES Murni
│   │   ├── chat_node.py                    # Terminal P2P chat engine (TCP Socket & threading)
│   │   ├── des_manual.py                   # Algoritma DES murni (IP, Feistel, S-Box, PC-1/PC-2)
│   │   ├── des_utils.py                    # Utilitas padding PKCS#7 & manipulasi bit
│   │   ├── Dockerfile & docker-compose.yml # Virtualisasi 2 node (Jane Doe & John Doe)
│   │   └── termux_setup.sh                 # Skrip deployment di Android Termux
│   │
│   ├── 2/                                  # [Tugas 2] Key Distribution (KDC) & Chat AES-128 Murni
│   │   ├── aes_manual.py                   # Engine AES-128 murni (SubBytes, ShiftRows, MixColumns, KeyExpansion)
│   │   ├── aes_utils.py                    # Utilitas matriks State 4x4, PKCS#7 padding, & GF(2^8)
│   │   ├── kdc.py                          # Server KDC (Master Key Ka & Kb, Generator Ks, Langkah 1-2)
│   │   ├── alice.py                        # Node Initiator Alice (Handshake Langkah 1-5, /rekey, Chat AES)
│   │   ├── bob.py                          # Node Responder Bob (Verifikasi Langkah 3-5 & Chat AES)
│   │   ├── Dockerfile & docker-compose.yml # Virtualisasi 3 node (KDC, Alice, Bob) di 3 IP berbeda
│   │   └── termux_setup.sh                 # Skrip eksekusi multi-device fisik (Termux/LAN)
│   │
│   └── docs/                               # Panduan & analisis mendalam praktikum
│       ├── Panduan_Demo_Lengkap.md         # Cheat-sheet langkah demo Tugas 1 (DES)
│       ├── Penjelasan_DES_Sangat_Detail.md # Penjelasan teoritis matematika & tabel substitusi DES
│       ├── Part1_Perjalanan_Kunci.md       # Rincian permutasi pembangkitan 16 subkunci DES
│       ├── Part2_Perjalanan_Pesan.md       # Rincian enkripsi 64-bit plaintext DES
│       └── Panduan_Demo_Tugas2_AES_KDC.md  # Cheat-sheet demo & bedah materi Tugas 2 (KDC & AES-128)
│
├── .gitignore                              # File konfigurasi abaikan Git
└── README.md                               # Panduan utama repositori
```

---

## 🚀 Panduan Eksekusi Tugas 1: Simulasi P2P Chat DES

### 1. Menjalankan via Docker Compose (Multi-Node)
```bash
cd Tugas/1
docker compose up -d

# Terminal Jane Doe (Host - IP: 172.20.0.10)
docker exec -it ki_jane_doe python chat_node.py

# Terminal John Doe (Client - IP: 172.20.0.11)
docker exec -it ki_john_doe python chat_node.py
```

### 2. Panduan Lengkap Skenario Demo Tugas 1
Silakan baca panduan lengkap pada [Tugas/docs/Panduan_Demo_Lengkap.md](Tugas/docs/Panduan_Demo_Lengkap.md).

---

## 🔐 Panduan Eksekusi Tugas 2: Key Distribution Scenario (KDC) & AES-128 Chat

### 1. Menjalankan via Docker Compose (3 Entitas di 3 IP Berbeda)
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

### 2. Panduan Lengkap Skenario Demo & Bedah Materi Tugas 2
Silakan baca panduan lengkap pada [Tugas/2/README.md](Tugas/2/README.md) dan [Tugas/docs/Panduan_Demo_Tugas2_AES_KDC.md](Tugas/docs/Panduan_Demo_Tugas2_AES_KDC.md).
