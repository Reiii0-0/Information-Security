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
│   ├── 2/                                  # [Tugas 2] Key Distribution (KDC) & Chat AES Murni
│   │   └── README.md                       # Spesifikasi dan panduan Tugas 2
│   │
│   └── docs/                               # Panduan & analisis mendalam praktikum
│       ├── Panduan_Demo_Lengkap.md         # Cheat-sheet langkah demo asisten
│       ├── Penjelasan_DES_Sangat_Detail.md # Penjelasan teoritis matematika & tabel substitusi
│       ├── Part1_Perjalanan_Kunci.md       # Rincian permutasi pembangkitan 16 subkunci
│       └── Part2_Perjalanan_Pesan.md       # Rincian enkripsi 64-bit plaintext
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

### 2. Panduan Lengkap Skenario Demo
Silakan baca panduan lengkap pada [Tugas/docs/Panduan_Demo_Lengkap.md](Tugas/docs/Panduan_Demo_Lengkap.md).

---

## 🔐 Rencana Proyek Tugas 2: Key Distribution Scenario (KDC) & AES Chat
Informasi spesifikasi lengkap dan rancangan arsitektur sistem dapat dibaca pada [Tugas/2/README.md](Tugas/2/README.md).
