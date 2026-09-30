def hex2bin(s):
    return bin(int(s, 16))[2:].zfill(len(s) * 4)

def bin2hex(s):
    return hex(int(s, 2))[2:].zfill(len(s) // 4)

def bytes2bin(b):
    return ''.join(format(byte, '08b') for byte in b)

def bin2bytes(s):
    byte_list = []
    for i in range(0, len(s), 8):
        b = s[i:i+8]
        if len(b) == 8:
            byte_list.append(int(b, 2))
    return bytes(byte_list)

def xor(a, b):
    return ''.join('1' if i != j else '0' for i, j in zip(a, b))

def pad(data_bytes):
    pad_len = 8 - (len(data_bytes) % 8)
    return data_bytes + bytes([pad_len] * pad_len)

def unpad(data_bytes):
    if not data_bytes:
        return data_bytes
    pad_len = data_bytes[-1]
    if 0 < pad_len <= 8:
        return data_bytes[:-pad_len]
    return data_bytes
