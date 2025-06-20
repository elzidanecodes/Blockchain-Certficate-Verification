import sys
import os
sys.path.append(os.path.abspath('../backend'))

from crypto.aes_utils import encrypt_data, decrypt_data
from config import AES_SECRET_KEY

def test_aes_encrypt_decrypt():
    print("[🔒] Testing AES Encryption and Decryption...")


    plain = "23374/PL2.3/KM/20220|Laita Zidan|2141762100"
    

    key = AES_SECRET_KEY
    if not key:
        raise ValueError("AES_SECRET_KEY is not set in the environment variables.")
    encrypted = encrypt_data(plain, key)
    print("🔐 Encrypted (base64):", encrypted)

    decrypted = decrypt_data(encrypted, key)
    print("🔓 Decrypted:", decrypted)

    assert decrypted == plain, "[❌] Hasil dekripsi tidak sesuai dengan data asli"
    print("[✅] Enkripsi & dekripsi AES berhasil dan data utuh.")

if __name__ == "__main__":
    test_aes_encrypt_decrypt()
