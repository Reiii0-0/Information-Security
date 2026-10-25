#!/bin/bash

echo "=================================================="
echo "=   Setup & Run Tugas 2 (KDC / Alice / Bob)      ="
echo "=================================================="

if ! command -v python3 &> /dev/null; then
    echo "[*] Menginstal Python..."
    pkg update -y && pkg install python -y
fi

echo "Pilih entitas yang ingin dijalankan di perangkat ini:"
echo "  1) KDC Server (kdc.py)"
echo "  2) Alice - Initiator (alice.py)"
echo "  3) Bob - Responder (bob.py)"
read -p "Pilihan (1/2/3): " role_choice

case "$role_choice" in
    1) python3 kdc.py ;;
    2) python3 alice.py ;;
    3) python3 bob.py ;;
    *) echo "[!] Pilihan tidak valid." ; exit 1 ;;
esac
