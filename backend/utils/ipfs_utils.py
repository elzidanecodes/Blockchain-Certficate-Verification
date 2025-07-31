# ipfs_utils.py
from celery import shared_task
from utils.ipfs_logic import regenerate_and_upload_ipfs

@shared_task(name="tasks.run_regenerate_ipfs")
def run_regenerate_ipfs(data: dict):
    try:
        if not data.get("rsa_valid", False):
            data["status"] = "Lewat: RSA tidak valid"
            return data

        encrypted = data.get("encrypted_data")
        certificate_id = data.get("certificate_id")

        if not encrypted or not certificate_id:
            data["status"] = "Data terenkripsi atau ID kosong"
            return data

        hasil = regenerate_and_upload_ipfs(encrypted, certificate_id)
        data.update(hasil)
        data["status"] = "success"
        return data

    except Exception as e:
        data["status"] = f"Gagal IPFS: {str(e)}"
        return data