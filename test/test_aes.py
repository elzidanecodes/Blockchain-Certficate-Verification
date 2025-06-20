import os
import sys
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from crypto.aes_utils import encrypt_data, decrypt_data
from config import AES_SECRET_KEY

@pytest.fixture
def plaintext():
    return "23374/PL2.3/KM/20220|Laita Zidan|2141762100"

@pytest.fixture
def aes_key():
    key = AES_SECRET_KEY
    if not key:
        raise ValueError("AES_SECRET_KEY is not set in the environment variables.")
    return key

def test_encrypt_decrypt_aes(plaintext, aes_key):
    encrypted = encrypt_data(plaintext, aes_key)
    decrypted = decrypt_data(encrypted, aes_key)

    assert isinstance(encrypted, str), "Encrypted output harus berupa string base64"
    assert decrypted == plaintext, "Hasil dekripsi tidak sesuai dengan data asli"
