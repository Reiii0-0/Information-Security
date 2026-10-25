import secrets
import socket
import sys
import threading
import aes_manual
import aes_utils


def calc_f(n2: int) -> int:
    return n2 - 1


class AliceNode:
    def __init__(self, id_a: str, id_b: str, ka: str, kdc_ip: str, kdc_port: int, bob_ip: str, bob_port: int) -> None:
        self.id_a = id_a
        self.id_b = id_b
        self.ka = ka
        self.kdc_ip = kdc_ip
        self.kdc_port = kdc_port
        self.bob_ip = bob_ip
        self.bob_port = bob_port
        self.ks: str = ""
        self.pending_ks: str = ""
        self.bob_sock: socket.socket | None = None
        self.auth_event = threading.Event()
        self.chat_ready = False
        self.lock = threading.Lock()
        self.running = True

    def stop(self) -> None:
        self.running = False
        with self.lock:
            sock = self.bob_sock
            self.bob_sock = None
        if sock:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                sock.close()
            except OSError:
                pass

    def request_kdc_session_key(self) -> tuple[str, str]:
        n1 = str(secrets.randbelow(900000) + 100000)
        req_step1 = f"{self.id_a}||{self.id_b}||{n1}"
        print(f"\n[STEP 1 A -> KDC] : {req_step1}")

        with socket.create_connection((self.kdc_ip, self.kdc_port), timeout=5.0) as kdc_sock:
            kdc_sock.sendall((req_step1 + "\n").encode("utf-8"))
            chunks = []
            while True:
                chunk = kdc_sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk.decode("utf-8", errors="replace"))
                if "\n" in chunks[-1]:
                    break
            resp_step2 = "".join(chunks).strip()

        if resp_step2.startswith("ERROR||"):
            raise RuntimeError(f"KDC menolak request: {resp_step2.split('||', 1)[1]}")

        parts = resp_step2.split("||")
        if len(parts) != 2:
            raise ValueError("Respons Langkah 2 dari KDC tidak valid.")

        cipher_alice_hex, ticket_bob_hex = parts[0], parts[1]
        print(f"[STEP 2 KDC -> A] : E(Ka, [Ks||IDA||IDB||N1]) Hex = {cipher_alice_hex}")
        print(f"                    E(Kb, [Ks||IDA]) Hex          = {ticket_bob_hex}")

        with self.lock:
            ka_curr = self.ka
        plain_alice = aes_manual.decrypt_message(cipher_alice_hex, ka_curr)
        a_parts = plain_alice.split("||")
        if len(a_parts) != 4:
            raise ValueError("Isi paket KDC untuk Alice tidak sesuai format.")

        ks_new, recv_ida, recv_idb, recv_n1 = a_parts
        if recv_ida != self.id_a or recv_idb != self.id_b or recv_n1 != n1:
            raise ValueError(f"Verifikasi Nonce N1/ID gagal! Kirim={n1}, Terima={recv_n1}")

        print(f"[DEKRIPSI PAKET A]: Ks={ks_new} | IDA={recv_ida} | IDB={recv_idb} | N1={recv_n1} (COCOK)")
        return ks_new, ticket_bob_hex

    def initiate_handshake(self) -> bool:
        if self.bob_sock is None:
            self.connect_to_bob()
        assert self.bob_sock is not None

        self.auth_event.clear()
        ks_new, ticket_bob_hex = self.request_kdc_session_key()
        with self.lock:
            self.pending_ks = ks_new

        step3_msg = f"STEP3||{ticket_bob_hex}"
        print(f"[STEP 3 A -> B]   : Tiket E(Kb, [Ks||IDA]) Hex = {ticket_bob_hex}")
        try:
            self.bob_sock.sendall((step3_msg + "\n").encode("utf-8"))
        except OSError:
            self.connect_to_bob()
            assert self.bob_sock is not None
            self.bob_sock.sendall((step3_msg + "\n").encode("utf-8"))

        if not self.auth_event.wait(timeout=5.0):
            raise TimeoutError("Waktu tunggu Mutual Authentication (Langkah 4-5) habis.")
        with self.lock:
            return bool(self.ks)

    def handle_incoming_line(self, line: str) -> None:
        if line.startswith("STEP4||"):
            cipher_n2_hex = line.split("||", 1)[1]
            print(f"\n[STEP 4 B -> A]   : E(Ks, N2) Hex = {cipher_n2_hex}")
            try:
                with self.lock:
                    ks_temp = self.pending_ks
                n2_str = aes_manual.decrypt_message(cipher_n2_hex, ks_temp)
                n2_val = int(n2_str)
                fn2_val = calc_f(n2_val)
                print(f"[DEKRIPSI N2]     : N2 = {n2_val} -> f(N2) = N2 - 1 = {fn2_val}")

                cipher_fn2_hex = aes_manual.encrypt_message(str(fn2_val), ks_temp)
                step5_msg = f"STEP5||{cipher_fn2_hex}"
                print(f"[STEP 5 A -> B]   : E(Ks, f(N2)) Hex = {cipher_fn2_hex}")
                if self.bob_sock:
                    self.bob_sock.sendall((step5_msg + "\n").encode("utf-8"))
            except Exception as e:
                print(f"[!] Gagal memproses Langkah 4 dari Bob: {e}")
                with self.lock:
                    self.ks = ""
                self.auth_event.set()

        elif line.startswith("AUTH_OK||"):
            with self.lock:
                self.ks = self.pending_ks
                active_ks = self.ks
            print(f"[MUTUAL AUTH OK]  : Handshake 5 Langkah Selesai! Session Key Ks = {active_ks}")
            self.auth_event.set()

        elif line.startswith("AUTH_FAIL||"):
            reason = line.split("||", 1)[1]
            print(f"\n[!] Mutual Authentication Gagal dari Bob: {reason}")
            with self.lock:
                self.ks = ""
            self.auth_event.set()

        else:
            print(f"\n[CIPHERTEXT TERIMA DARI BOB]: {line}")
            with self.lock:
                active_ks = self.ks
            try:
                plain = aes_manual.decrypt_message(line, active_ks)
                print(f"[PLAINTEXT DARI BOB]        : {plain}")
            except Exception as e:
                print(f"[!] Gagal dekripsi pesan Bob (Ks={active_ks}): {e}")
            if self.chat_ready:
                print("Alice> ", end="", flush=True)

    def receive_loop(self, sock: socket.socket) -> None:
        buffer = ""
        while self.running:
            try:
                data = sock.recv(4096)
                if not data:
                    print("\n[!] Koneksi ditutup oleh Bob.")
                    with self.lock:
                        if self.bob_sock is sock:
                            self.bob_sock = None
                    if self.chat_ready:
                        print("Alice> ", end="", flush=True)
                    break
                buffer += data.decode("utf-8", errors="replace")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line:
                        self.handle_incoming_line(line)
            except Exception as e:
                if self.running:
                    with self.lock:
                        if self.bob_sock is sock:
                            self.bob_sock = None
                    print(f"\n[!] Error koneksi: {e}")
                    if self.chat_ready:
                        print("Alice> ", end="", flush=True)
                break

    def connect_to_bob(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[*] Menghubungkan ke Responder Bob di {self.bob_ip}:{self.bob_port}...")
        sock.connect((self.bob_ip, self.bob_port))
        print("[*] Terhubung dengan Bob!")
        with self.lock:
            self.bob_sock = sock
        t = threading.Thread(target=self.receive_loop, args=(sock,), daemon=True)
        t.start()

    def send_chat(self, message: str) -> None:
        with self.lock:
            sock = self.bob_sock
            active_ks = self.ks
        if not sock:
            raise RuntimeError("Koneksi ke Bob tidak aktif. Jalankan /rekey untuk menghubungkan ulang.")
        if not active_ks:
            raise RuntimeError("Session Key Ks belum terbentuk. Jalankan /rekey terlebih dahulu.")
        cipher_hex = aes_manual.encrypt_message(message, active_ks)
        print(f"[CIPHERTEXT KIRIM KE BOB]   : {cipher_hex}")
        sock.sendall((cipher_hex + "\n").encode("utf-8"))


def main() -> None:
    print("==================================================")
    print("=          INITIATOR NODE A (ALICE) CLI          =")
    print("==================================================")
    kdc_ip = input("Masukkan IP KDC (default 172.28.0.10): ").strip() or "172.28.0.10"
    kdc_port_in = input("Masukkan Port KDC (default 5000): ").strip()
    kdc_port = int(kdc_port_in) if kdc_port_in else 5000

    bob_ip = input("Masukkan IP Bob (default 172.28.0.12): ").strip() or "172.28.0.12"
    bob_port_in = input("Masukkan Port Bob (default 5001): ").strip()
    bob_port = int(bob_port_in) if bob_port_in else 5001

    ka = input("Masukkan Master Key Alice Ka (default KDC_ALICE_KEY123): ").strip() or "KDC_ALICE_KEY123"

    alice = AliceNode("ALICE", "BOB", ka, kdc_ip, kdc_port, bob_ip, bob_port)
    try:
        alice.connect_to_bob()
        alice.initiate_handshake()
    except Exception as e:
        print(f"[!] Gagal inisiasi awal: {e}")
        print("[*] Anda tetap dapat memperbaiki kunci dengan /setmaster lalu ketik /rekey.")

    alice.chat_ready = True
    print("\n--- SESI KOMUNIKASI AES DUA ARAH AKTIF ---")
    print("Perintah: /keys | /setkey <ks_baru> | /setmaster <ka_baru> | /rekey | /exit\n")

    while alice.running:
        try:
            msg = input("Alice> ").strip()
            if not msg:
                continue
            if msg == "/keys":
                with alice.lock:
                    norm_ka = aes_utils.normalize_key(alice.ka).decode("utf-8", errors="replace")
                    norm_ks = aes_utils.normalize_key(alice.ks).decode("utf-8", errors="replace") if alice.ks else "-"
                    print(f"[*] ID={alice.id_a} | Master Ka={alice.ka} (16B: {norm_ka}) | Session Ks={alice.ks} (16B: {norm_ks})")
            elif msg.startswith("/setkey "):
                new_ks = msg.split(" ", 1)[1].strip()
                if new_ks and "||" not in new_ks:
                    with alice.lock:
                        alice.ks = new_ks
                    print(f"[*] Session Key Ks Alice diubah secara manual ke: {new_ks}")
                else:
                    print("[!] Kunci tidak valid.")
            elif msg.startswith("/setmaster "):
                new_ka = msg.split(" ", 1)[1].strip()
                if new_ka and "||" not in new_ka:
                    with alice.lock:
                        alice.ka = new_ka
                    print(f"[*] Master Key Ka Alice diubah ke: {new_ka}")
                else:
                    print("[!] Kunci tidak valid.")
            elif msg == "/rekey":
                try:
                    alice.initiate_handshake()
                except Exception as e:
                    print(f"[!] Handshake ulang (/rekey) gagal: {e}")
            elif msg == "/exit":
                alice.stop()
                sys.exit(0)
            else:
                alice.send_chat(msg)
        except (KeyboardInterrupt, EOFError):
            print("\n[*] Menutup Alice Node...")
            alice.stop()
            sys.exit(0)
        except Exception as e:
            print(f"[!] Error: {e}")


if __name__ == "__main__":
    main()
