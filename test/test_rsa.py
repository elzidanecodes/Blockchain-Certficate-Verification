import os
import sys
import base64

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from crypto.rsa_utils import sign_data, verify_signature, load_private_key

# Data asli
MESSAGE_ORIGINAL = "23374/PL2.3/KM/20220|Laita Zidan|2141762100"
MESSAGE_TAMPERED = "23374/PL2.3/KM/20220|Laita Zidan|9999999999"

def test_rsa_signature_valid():
    private_key = load_private_key()
    signature = sign_data(MESSAGE_ORIGINAL, private_key)
    assert isinstance(signature, str)
    assert verify_signature(MESSAGE_ORIGINAL, signature) is True

def test_rsa_signature_invalid_on_tampered_data():
    private_key = load_private_key()
    signature = sign_data(MESSAGE_ORIGINAL, private_key)
    assert verify_signature(MESSAGE_TAMPERED, signature) is False

def test_signature_is_base64_string():
    private_key = load_private_key()
    signature = sign_data(MESSAGE_ORIGINAL, private_key)
    try:
        decoded = base64.b64decode(signature.encode())
        assert isinstance(decoded, bytes)
    except Exception:
        assert False, "Signature bukan base64 valid"