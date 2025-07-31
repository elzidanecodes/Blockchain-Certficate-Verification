from celery import shared_task
from utils.image_logic import regenerate_verified_certificate

@shared_task(name="tasks.run_regenerate_certificate")
def run_regenerate_certificate(data: dict):
    try:
        decrypted = data.get("decrypted")
        certificate_id = data.get("certificate_id")

        if not decrypted or not certificate_id:
            data["status"] = "Regenerate gagal: data tidak lengkap"
            return data

        img_bytes, _, qr_base64 = regenerate_verified_certificate(decrypted, certificate_id)
        data["img_bytes"] = img_bytes
        data["qr_code"] = qr_base64
        return data

    except Exception as e:
        data["status"] = f"Gagal regenerate certificate: {str(e)}"
        return data
