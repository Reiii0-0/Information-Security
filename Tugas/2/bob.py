import secrets
import socket
import sys
import threading
import aes_manual
import aes_utils


def calc_f(n2: int) -> int:
    return n2 - 1


class BobNode:
    def __init__(self, id_b: str, kb: str, host: str, port: int) -> None:
        self.id_b = id_b
        self.kb = kb
        self.host = host
        self.port = port
        self.ks: str = ""
        self.pending_ks: str = ""
        self.expected_fn2: int | None = None
        self.alice_sock: socket.socket | None = None
        self.server_sock: socket.socket | None = None
        self.auth_event = threading.Event()
        self.chat_ready = False
        self.lock = threading.Lock()
        self.running = True

    def stop(self) -> None:
        self.running = False
        with self.lock:
            socks = [self.alice_sock, self.server_sock]
            self.alice_sock = None
            self.server_sock = None
        for s in socks:
            if s:
                try:
                    s.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                try:
                    s.close()
                except OSError:
                    pass

    def handle_incoming_line(self, line: str) -> None:
        if line.startswith("STEP3||"):
            ticket_bob_hex = line.split("||", 1)[1]
            print(f"\n[STEP 3 A -> B]   : Tiket E(Kb, [Ks||IDA]) Hex = {ticket_bob_hex}")
            try:
                with self.lock:
                    kb_curr = self.kb
                plain_ticket = aes_manual.decrypt_message(ticket_bob_hex, kb_curr)
                t_parts = plain_ticket.split("||")
                if len(t_parts) != 2:
                    raise ValueError("Format tiket Bob tidak valid.")

                ks_new, caller_id = t_parts[0], t_parts[1]
                n2_val = secrets.randbelow(900000) + 100000
                with self.lock:
                    self.pending_ks = ks_new
                    self.expected_fn2 = calc_f(n2_val)

                print(f"[DEKRIPSI TIKET B]: Ks={ks_new} | Initiator={caller_id}")
                cipher_n2_hex = aes_manual.encrypt_message(str(n2_val), ks_new)
                step4_msg = f"STEP4||{cipher_n2_hex}"
                print(f"[STEP 4 B -> A]   : Nonce N2={n2_val} | E(Ks, N2) Hex = {cipher_n2_hex}")
                if self.alice_sock:
                    self.alice_sock.sendall((step4_msg + "\n").encode("utf-8"))
            except Exception as e:
                print(f"[!] Gagal mendekripsi Tiket Langkah 3 (Kb salah/tiket rusak): {e}")
                if self.alice_sock:
                    self.alice_sock.sendall((f"AUTH_FAIL||Dekripsi tiket gagal: {e}\n").encode("utf-8"))
                if self.chat_ready:
                    print("Bob> ", end="", flush=True)

        elif line.startswith("STEP5||"):
            cipher_fn2_hex = line.split("||", 1)[1]
            print(f"[STEP 5 A -> B]   : E(Ks, f(N2)) Hex = {cipher_fn2_hex}")
            try:
                with self.lock:
                    ks_temp = self.pending_ks
                    exp_fn2 = self.expected_fn2
                fn2_str = aes_manual.decrypt_message(cipher_fn2_hex, ks_temp)
                fn2_recv = int(fn2_str)
                if exp_fn2 is None or fn2_recv != exp_fn2:
                    raise ValueError(f"f(N2) tidak cocok! Harusnya {exp_fn2}, diterima {fn2_recv}")

                with self.lock:
                    self.ks = ks_temp
                    self.expected_fn2 = None
                print(f"[MUTUAL AUTH OK]  : f(N2)={fn2_recv} VALID! Session Key Ks = {ks_temp}")
                if self.alice_sock:
                    self.alice_sock.sendall(b"AUTH_OK||\n")
                self.auth_event.set()
            except Exception as e:
                print(f"[!] Verifikasi Langkah 5 gagal: {e}")
                if self.alice_sock:
                    self.alice_sock.sendall((f"AUTH_FAIL||{e}\n").encode("utf-8"))
            if self.chat_ready:
                print("Bob> ", end="", flush=True)

        else:
            print(f"\n[CIPHERTEXT TERIMA DARI ALICE]: {line}")
            with self.lock:
                active_ks = self.ks
            try:
                plain = aes_manual.decrypt_message(line, active_ks)
                print(f"[PLAINTEXT DARI ALICE]        : {plain}")
            except Exception as e:
                print(f"[!] Gagal dekripsi pesan Alice (Ks={active_ks}): {e}")
            if self.chat_ready:
                print("Bob> ", end="", flush=True)

    def receive_loop(self, conn: socket.socket) -> None:
        buffer = ""
        while self.running:
            try:
                data = conn.recv(4096)
                if not data:
                    print("\n[*] Alice memutus koneksi. Menunggu koneksi ulang Alice...")
                    if self.chat_ready:
                        print("Bob> ", end="", flush=True)
                    break
                buffer += data.decode("utf-8", errors="replace")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line:
                        self.handle_incoming_line(line)
            except Exception as e:
                if self.running:
                    print(f"\n[!] Error koneksi: {e}")
                    if self.chat_ready:
                        print("Bob> ", end="", flush=True)
                break
        conn.close()

    def accept_forever(self, server: socket.socket) -> None:
        while self.running:
            try:
                conn, addr = server.accept()
                print(f"\n[*] Terhubung dengan Initiator Alice dari {addr[0]}:{addr[1]}")
                with self.lock:
                    if self.alice_sock:
                        try:
                            self.alice_sock.close()
                        except Exception:
                            pass
                    self.alice_sock = conn
                t = threading.Thread(target=self.receive_loop, args=(conn,), daemon=True)
                t.start()
            except Exception:
                if not self.running:
                    break

    def start_server(self) -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(5)
        self.server_sock = server
        print(f"[*] Responder Bob mendengarkan koneksi di {self.host}:{self.port}...")
        t = threading.Thread(target=self.accept_forever, args=(server,), daemon=True)
        t.start()

    def wait_for_alice(self) -> None:
        self.start_server()

    def send_chat(self, message: str) -> None:
        with self.lock:
            sock = self.alice_sock
            active_ks = self.ks
        if not sock:
            raise RuntimeError("Koneksi dari Alice belum aktif.")
        if not active_ks:
            raise RuntimeError("Session Key Ks belum terbentuk. Tunggu handshake dari Alice.")
        cipher_hex = aes_manual.encrypt_message(message, active_ks)
        print(f"[CIPHERTEXT KIRIM KE ALICE]   : {cipher_hex}")
        sock.sendall((cipher_hex + "\n").encode("utf-8"))


def main() -> None:
    print("==================================================")
    print("=          RESPONDER NODE B (BOB) CLI            =")
    print("==================================================")
    port_in = input("Masukkan Port Bob (default 5001): ").strip()
    port = int(port_in) if port_in else 5001

    kb = input("Masukkan Master Key Bob Kb (default KDC_BOB_KEY_4567): ").strip() or "KDC_BOB_KEY_4567"

    bob = BobNode("BOB", kb, "0.0.0.0", port)
    bob.chat_ready = True
    bob.start_server()
    print("[*] Menunggu inisiasi Handshake Langkah 3-5 dari Alice...")
    print("Perintah: /keys | /setkey <ks_baru> | /setmaster <kb_baru> | /exit\n")

    while bob.running:
        try:
            msg = input("Bob> ").strip()
            if not msg:
                continue
            if msg == "/keys":
                with bob.lock:
                    norm_kb = aes_utils.normalize_key(bob.kb).decode("utf-8", errors="replace")
                    norm_ks = aes_utils.normalize_key(bob.ks).decode("utf-8", errors="replace") if bob.ks else "-"
                    print(f"[*] ID={bob.id_b} | Master Kb={bob.kb} (16B: {norm_kb}) | Session Ks={bob.ks} (16B: {norm_ks})")
            elif msg.startswith("/setkey "):
                new_ks = msg.split(" ", 1)[1].strip()
                if new_ks and "||" not in new_ks:
                    with bob.lock:
                        bob.ks = new_ks
                    print(f"[*] Session Key Ks Bob diubah secara manual ke: {new_ks}")
                else:
                    print("[!] Kunci tidak valid.")
            elif msg.startswith("/setmaster "):
                new_kb = msg.split(" ", 1)[1].strip()
                if new_kb and "||" not in new_kb:
                    with bob.lock:
                        bob.kb = new_kb
                    print(f"[*] Master Key Kb Bob diubah ke: {new_kb}")
                else:
                    print("[!] Kunci tidak valid.")
            elif msg == "/exit":
                bob.stop()
                sys.exit(0)
            else:
                bob.send_chat(msg)
        except (KeyboardInterrupt, EOFError):
            print("\n[*] Menutup Bob Node...")
            bob.stop()
            sys.exit(0)
        except Exception as e:
            print(f"[!] Error: {e}")


if __name__ == "__main__":
    main()
