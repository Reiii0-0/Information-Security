def normalize_key(key_text: str) -> bytes:
    return key_text.encode('utf-8').ljust(16, b'0')[:16]


def pad(data_bytes: bytes) -> bytes:
    pad_len = 16 - (len(data_bytes) % 16)
    return data_bytes + bytes([pad_len] * pad_len)


def unpad(data_bytes: bytes) -> bytes:
    if not data_bytes or len(data_bytes) % 16 != 0:
        raise ValueError("Panjang data dekripsi tidak valid.")
    pad_len = data_bytes[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError("Nilai padding PKCS#7 tidak valid.")
    if data_bytes[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Integritas padding PKCS#7 gagal (kunci salah atau data rusak).")
    return data_bytes[:-pad_len]


def bytes_to_matrix(block: bytes) -> list[list[int]]:
    return [[block[r + 4 * c] for c in range(4)] for r in range(4)]


def matrix_to_bytes(state: list[list[int]]) -> bytes:
    return bytes(state[r][c] for c in range(4) for r in range(4))


def xtime(a: int) -> int:
    return ((a << 1) ^ 0x1B) & 0xFF if (a & 0x80) else (a << 1)


def gmul(a: int, b: int) -> int:
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        a = xtime(a)
        b >>= 1
    return p
