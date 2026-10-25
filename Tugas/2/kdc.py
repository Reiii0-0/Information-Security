import secrets
import socket
import string
import sys
import threading
import aes_manual
import aes_utils

ALPHABET = string.ascii_letters + string.digits


class KDCServer:
    def __init__(self, host: str, port: int, ka: str, kb: str) -> None:
        self.host = host
        self.port = port
        self.ka = ka
        self.kb = kb
        self.custom_ks: str | None = None
        self.server_sock: socket.socket | None = None
        self.lock = threading.Lock()
        self.running = True

    def stop(self) -> None:
        self.running = False
        if self.server_sock:
            try:
                self.server_sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self.server_sock.close()
            except OSError:
                pass

    def generate_session_key(self) -> str:
        with self.lock:
            if self.custom_ks:
                return self.custom_ks
        return ''.join(secrets.choice(ALPHABET) for _ in range(16))

    def process_request(self, raw_request: str) -> str:
        parts = raw_request.strip().split("||")
        if len(parts) != 3 or not all(parts):
            raise ValueError("Format Langkah 1 harus: IDA||IDB||N1")

        id_a, id_b, n1 = parts[0].strip(), parts[1].strip(), parts[2].strip()
        if not n1.isdigit():
            raise ValueError("Nonce N1 harus berupa angka.")

        ks = self.generate_session_key()
        with self.lock:
            ka_curr, kb_curr = self.ka, self.kb

        payload_alice = f"{ks}||{id_a}||{id_b}||{n1}"
        payload_bob = f"{ks}||{id_a}"

        cipher_alice_hex = aes_manual.encrypt_message(payload_alice, ka_curr)
        ticket_bob_hex = aes_manual.encrypt_message(payload_bob, kb_curr)

        print(f"\n[STEP 1 DITERIMA] : IDA={id_a} | IDB={id_b} | N1={n1}")
        print(f"[SESSION KEY Ks]  : {ks} (ASCII 16-byte)")
        print(f"[PLAIN PAKET A]   : {payload_alice}")
        print(f"[CIPHER PAKET A]  : {cipher_alice_hex}")
        print(f"[PLAIN TIKET B]   : {payload_bob}")
        print(f"[CIPHER TIKET B]  : {ticket_bob_hex}")
        print("KDC> ", end="", flush=True)

        return f"{cipher_alice_hex}||{ticket_bob_hex}\n"

    def handle_client(self, conn: socket.socket, addr: tuple[str, int]) -> None:
        try:
            conn.settimeout(5.0)
            data = conn.recv(4096)
            if not data:
                return
            req_str = data.decode('utf-8', errors='replace').strip()
            print(f"\n[*] Request masuk dari {addr[0]}:{addr[1]}")
            response = self.process_request(req_str)
            conn.sendall(response.encode('utf-8'))
        except Exception as e:
            err_msg = f"ERROR||{e}\n"
            try:
                conn.sendall(err_msg.encode('utf-8'))
            except Exception:
                pass
            print(f"\n[!] Gagal memproses request dari {addr[0]}: {e}\nKDC> ", end="", flush=True)
        finally:
            conn.close()

    def serve_forever(self) -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        self.server_sock = server
        print(f"[*] KDC Server aktif mendengarkan di {self.host}:{self.port}")
        while self.running:
            try:
                conn, addr = server.accept()
                t = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                t.start()
            except Exception:
                if not self.running:
                    break


def main() -> None:
    print("==================================================")
    print("=       KEY DISTRIBUTION CENTER (KDC) NODE       =")
    print("==================================================")
    port_in = input("Masukkan Port KDC (default 5000): ").strip()
    port = int(port_in) if port_in else 5000

    ka = input("Masukkan Master Key Alice Ka (default KDC_ALICE_KEY123): ").strip() or "KDC_ALICE_KEY123"
    kb = input("Masukkan Master Key Bob Kb (default KDC_BOB_KEY_4567): ").strip() or "KDC_BOB_KEY_4567"

    kdc = KDCServer("0.0.0.0", port, ka, kb)
    server_thread = threading.Thread(target=kdc.serve_forever, daemon=True)
    server_thread.start()

    print("\nPerintah Interaktif KDC: /keys | /setka <key> | /setkb <key> | /setks <key|auto> | /exit")
    while True:
        try:
            cmd = input("KDC> ").strip()
            if not cmd:
                continue
            if cmd == "/keys":
                with kdc.lock:
                    norm_ka = aes_utils.normalize_key(kdc.ka).decode("utf-8", errors="replace")
                    norm_kb = aes_utils.normalize_key(kdc.kb).decode("utf-8", errors="replace")
                    mode_ks = kdc.custom_ks if kdc.custom_ks else "AUTO (CSPRNG 16-char)"
                    print(f"[*] Ka={kdc.ka} (16B: {norm_ka}) | Kb={kdc.kb} (16B: {norm_kb}) | Ks={mode_ks}")
            elif cmd.startswith("/setka "):
                new_ka = cmd.split(" ", 1)[1].strip()
                if new_ka and "||" not in new_ka:
                    with kdc.lock:
                        kdc.ka = new_ka
                    print(f"[*] Master Key Ka diubah menjadi: {new_ka}")
                else:
                    print("[!] Kunci tidak boleh kosong atau mengandung '||'.")
            elif cmd.startswith("/setkb "):
                new_kb = cmd.split(" ", 1)[1].strip()
                if new_kb and "||" not in new_kb:
                    with kdc.lock:
                        kdc.kb = new_kb
                    print(f"[*] Master Key Kb diubah menjadi: {new_kb}")
                else:
                    print("[!] Kunci tidak boleh kosong atau mengandung '||'.")
            elif cmd.startswith("/setks "):
                val = cmd.split(" ", 1)[1].strip()
                if "||" in val:
                    print("[!] Session Key tidak boleh mengandung '||'.")
                else:
                    with kdc.lock:
                        kdc.custom_ks = None if val.lower() == "auto" else val
                    print(f"[*] Mode Session Key Ks diatur ke: {val}")
            elif cmd == "/exit":
                kdc.stop()
                sys.exit(0)
            else:
                print("[!] Perintah: /keys | /setka <key> | /setkb <key> | /setks <key|auto> | /exit")
        except (KeyboardInterrupt, EOFError):
            print("\n[*] Menutup KDC Server...")
            kdc.stop()
            sys.exit(0)


if __name__ == "__main__":
    main()
