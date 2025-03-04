import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import json

base_dir = os.path.dirname(os.path.abspath(__file__))
private_key_path = os.path.join(base_dir, "private_key.pem")
public_key_path = os.path.join(base_dir, "public_key.pem")

# Fungsi untuk membuat pasangan kunci RSA
def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    public_key = private_key.public_key()
    
    with open(private_key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(public_key_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

# Fungsi untuk memuat kunci RSA
def load_keys():
    with open(private_key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    with open(public_key_path, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return private_key, public_key

# Pastikan kunci ada
if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
    generate_rsa_keys()

private_key, public_key = load_keys()

# Fungsi untuk enkripsi data
def encrypt_data(data):
    encrypted = public_key.encrypt(
        json.dumps(data).encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted.hex()
