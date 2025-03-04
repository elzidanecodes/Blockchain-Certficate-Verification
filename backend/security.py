import os
import hashlib
import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

base_dir = os.path.dirname(os.path.abspath(__file__))
private_key_path = os.path.join(base_dir, "private_key.pem")
public_key_path = os.path.join(base_dir, "public_key.pem")

# Fungsi untuk membuat kunci RSA jika belum ada
def generate_rsa_keys():
    if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
        print("Generating new RSA keys...")
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()

        # Simpan private key
        with open(private_key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Simpan public key
        with open(public_key_path, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

        print("RSA keys generated successfully.")

# Load kunci RSA
def load_private_key():
    try:
        with open(private_key_path, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    except Exception as e:
        print(f"Error loading RSA keys: {e}")
        generate_rsa_keys()
        return load_private_key()

# Fungsi untuk menghasilkan hash MD5 dengan timestamp
def generate_md5_hash(data):
    timestamp = str(int(time.time()))
    combined_data = data + timestamp
    return hashlib.md5(combined_data.encode()).hexdigest()
