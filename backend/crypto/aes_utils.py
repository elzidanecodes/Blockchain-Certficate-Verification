from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import json

BLOCK_SIZE = 16

def pad(data):
    pad_len = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + chr(pad_len) * pad_len

def unpad(data):
    pad_len = ord(data[-1])
    return data[:-pad_len]

def encrypt_data(data_dict, secret_key):
    data = pad(json.dumps(data_dict))
    key = secret_key[:32].encode()  # 32 bytes = AES-256
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(data.encode())
    return base64.b64encode(iv + encrypted).decode()

def decrypt_data(encrypted_data, secret_key):
    key = secret_key[:32].encode()
    encrypted = base64.b64decode(encrypted_data)
    iv = encrypted[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted[16:])
    return json.loads(unpad(decrypted.decode()))
