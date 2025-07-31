from celery import shared_task
from crypto.aes_utils import decrypt_data
from database.mongo import get_certificate_by_id
from config import AES_SECRET_KEY, contract

@shared_task(name="tasks.run_decrypt")
def run_decrypt(data: dict):
    try:
        if not data.get("rsa_valid"):
            data["status"] = "Lewati dekripsi: RSA tidak valid"
            return data

        certificate_id = data.get("certificate_id")
        if not certificate_id:
            data["status"] = "Gagal dekripsi: Certificate ID kosong"
            return data

        contract_address = data.get("contract_address") or contract.address
        cert_db = get_certificate_by_id(certificate_id, contract_address)
        encrypted = cert_db.get("encrypted_data_sertif")
        if not encrypted:
            data["status"] = "Data terenkripsi tidak ditemukan"
            return data

        decrypted_data = decrypt_data(encrypted, AES_SECRET_KEY)
        if not decrypted_data:
            data["status"] = "Dekripsi gagal"
            return data

        data["decrypted"] = decrypted_data
        return data

    except Exception as e:
        data["status"] = f"Gagal dekripsi: {str(e)}"
        return data