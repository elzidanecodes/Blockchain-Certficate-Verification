from celery import shared_task
from utils.rsa_logic import verify_certificate_signature

@shared_task(name="tasks.run_signature_check")
def run_signature_check(data: dict):
    try:
        certificate_id = data.get("certificate_id")
        hash_value = data.get("hash")

        if not certificate_id or not hash_value:
            data["status"] = "Data tidak lengkap untuk verifikasi signature"
            return data

        hasil = verify_certificate_signature(certificate_id, hash_value)
        data.update(hasil)
        data["status"] = "success"
        return data

    except Exception as e:
        data["status"] = f"Verifikasi signature gagal: {str(e)}"
        return data
