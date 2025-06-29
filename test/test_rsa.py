import os
import sys
import base64
import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

# Path keys folder
KEYS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../keys/"))

os.makedirs(KEYS_DIR, exist_ok=True)

MESSAGE_ORIGINAL = "23374/PL2.3/KM/20220|Laita Zidan|2141762100"
MESSAGE_TAMPERED = "23374/PL2.3/KM/20220|Laita Zidan|9999999999"

def generate_and_save_rsa_keys(key_size, label):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )
    public_key = private_key.public_key()

    private_path = os.path.join(KEYS_DIR, f"private_key_{label}.pem")
    with open(private_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    public_path = os.path.join(KEYS_DIR, f"public_key_{label}.pem")
    with open(public_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    return private_key, public_key

def sign_data(data, private_key):
    signature = private_key.sign(
        data.encode(),
        padding.PKCS1v15(),
        hashes.MD5()
    )
    return base64.b64encode(signature).decode()

def verify_signature(data, signature_b64, public_key):
    signature = base64.b64decode(signature_b64)
    try:
        public_key.verify(
            signature,
            data.encode(),
            padding.PKCS1v15(),
            hashes.MD5()
        )
        return True
    except Exception:
        return False

def benchmark_rsa(key_size, label):
    print(f"\nRSA {key_size} bit ({label})")
    private_key, public_key = generate_and_save_rsa_keys(key_size, label)

    start_sign = time.time()
    signature = sign_data(MESSAGE_ORIGINAL, private_key)
    end_sign = time.time()
    sign_time = end_sign - start_sign

    start_verify = time.time()
    result_valid = verify_signature(MESSAGE_ORIGINAL, signature, public_key)
    end_verify = time.time()
    verify_time = end_verify - start_verify

    result_invalid = verify_signature(MESSAGE_TAMPERED, signature, public_key)

    print(f"Panjang Signature (Base64): {len(signature)} karakter")
    print(f"Waktu Signing          : {sign_time:.6f} detik")
    print(f"Waktu Verifikasi       : {verify_time:.6f} detik")
    print(f"Signature Valid?        : {result_valid}")
    print(f"Tampered Valid?         : {result_invalid}")

if __name__ == "__main__":
    benchmark_rsa(1024, "1024")
    benchmark_rsa(2048, "2048")