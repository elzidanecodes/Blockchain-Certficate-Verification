from celery import shared_task
from utils.log_logic import simpan_log_verifikasi

@shared_task(name="tasks.run_logging")
def run_logging(data: dict):
    try:
        if "certificate_id" not in data:
            data["status"] = "Gagal log: certificate_id tidak ditemukan"
            return data

        username = data.get("verified_by", "admin")
        hasil = simpan_log_verifikasi(data, verified_by=username)
        data.update(hasil)
        return data

    except Exception as e:
        data["status"] = f"Gagal menyimpan log: {str(e)}"
        return data