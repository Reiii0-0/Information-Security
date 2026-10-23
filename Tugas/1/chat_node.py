import socket
import threading
import sys
import des_manual

def receive_messages(sock, secret_key):
    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print("\n[!] Koneksi ditutup oleh rekan.")
                sock.close()
                sys.exit(0)
            
            cipher_hex = data.decode('utf-8')
            print(f"\n[ENCRYPTED PAYLOAD TERIMA]: {cipher_hex}")
            
            try:
                plain_text = des_manual.decrypt_message(cipher_hex, secret_key)
                print(f"[DECRYPTED PESAN]: {plain_text}\n> ", end="")
            except Exception as e:
                print(f"[!] Gagal mendekripsi pesan: {e}\n> ", end="")
        except Exception as e:
            print(f"\n[!] Error menerima data: {e}")
            sock.close()
            sys.exit(1)

def start_host(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(1)
    print(f"[*] Menunggu koneksi di port {port}...")
    
    conn, addr = server.accept()
    print(f"[*] Terhubung dengan Client di {addr[0]}:{addr[1]}")
    return conn

def start_client(ip, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[*] Menghubungkan ke Host {ip}:{port}...")
    try:
        client.connect((ip, port))
        print("[*] Berhasil terhubung dengan Host!")
        return client
    except Exception as e:
        print(f"[!] Gagal terhubung: {e}")
        sys.exit(1)

def main():
    print("========================================")
    print("=     DES Secure P2P Chat Terminal     =")
    print("========================================")
    role = input("Pilih peran (host/client): ").strip().lower()
    
    conn = None
    if role == 'host':
        port_str = input("Masukkan Port (default 5000): ").strip()
        port = int(port_str) if port_str else 5000
        conn = start_host(port)
    elif role == 'client':
        ip = input("Masukkan IP Host (default 127.0.0.1): ").strip()
        if not ip:
            ip = '127.0.0.1'
        port_str = input("Masukkan Port Host (default 5000): ").strip()
        port = int(port_str) if port_str else 5000
        conn = start_client(ip, port)
    else:
        print("Peran tidak valid.")
        sys.exit(1)
        
    secret_key = input("Masukkan 8-karakter Kunci Rahasia (Secret Key): ")
    if len(secret_key) != 8:
        print("[!] Peringatan: Kunci panjangnya tidak 8 karakter. Sistem akan menyesuaikan secara otomatis (potong/tambah 0).")
    
    print("\n--- CHAT DIMULAI. Ketik pesan Anda di bawah. ---")
    
    # Start receiver thread
    t = threading.Thread(target=receive_messages, args=(conn, secret_key))
    t.daemon = True
    t.start()
    
    while True:
        try:
            msg = input("> ")
            if msg.strip():
                cipher_hex = des_manual.encrypt_message(msg, secret_key)
                conn.send(cipher_hex.encode('utf-8'))
        except KeyboardInterrupt:
            print("\n[!] Keluar...")
            conn.close()
            sys.exit(0)

if __name__ == "__main__":
    main()
