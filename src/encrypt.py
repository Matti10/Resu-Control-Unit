from ucryptolib import aes

def get_aes_key_fromMac(mac):
    pad = b"MyAESKEYPADDER"   # 10 bytes
    return mac + pad  # 6 + 10 = 16 bytes

# Padding functions (PKCS#7)
def pad(data):
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len]) * pad_len

def unpad(data):
    return data[:-data[-1]]

# Encrypt (returns bytes)
def encrypt(data, key):
    cipher = aes(key, 1)  # 1 = ECB mode
    padded = pad(data)
    return cipher.encrypt(padded)

# Decrypt (returns bytes)
def decrypt(data, key):
    cipher = aes(key, 1)
    decrypted = cipher.decrypt(data)
    return unpad(decrypted)
