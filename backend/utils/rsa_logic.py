# rsa_logic.py
from crypto.rsa_utils import verify_signature
from routes.blockchain import get_certificate_data

def verify_certificate_signature(certificate_id, hash_value):
    valid, cert_id, signature = get_certificate_data(certificate_id)

    if not valid:
        raise ValueError("ID tidak ditemukan di blockchain")

    rsa_valid = verify_signature(hash_value, signature)
    return {
        "rsa_valid": rsa_valid,
        "valid": valid,
        "signature": signature,
        "cert_id": cert_id
    }
