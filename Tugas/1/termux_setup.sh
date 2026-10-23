#!/data/data/com.termux/files/usr/bin/bash
# Script Setup & Run untuk Termux
# Script ini akan memastikan Python sudah terinstall sebelum menjalankan aplikasi.

echo "======================================"
echo "    Instalasi Prasyarat Termux        "
echo "======================================"

# Cek apakah python sudah terinstall
if ! command -v python &> /dev/null; then
    echo "[!] Python belum terinstall. Sedang menginstall..."
    pkg update -y
    pkg install python -y
    echo "[*] Python berhasil diinstall!"
else
    echo "[*] Python sudah terinstall."
fi

echo "======================================"
echo "    Menjalankan Aplikasi Chat P2P     "
echo "======================================"

python chat_node.py
