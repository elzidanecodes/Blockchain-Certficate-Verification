from celery import shared_task
from crypto.hash_utils import generate_md5_hash

@shared_task(name="tasks.run_hashing")
def run_hashing(data: dict):
    try:
        extracted = data.get("extracted", {})
        no_sertif = extracted.get("no_sertifikat")
        name = extracted.get("name")
        student_id = extracted.get("student_id")

        if not all([no_sertif, name, student_id]):
            data["status"] = "Gagal hashing: data tidak lengkap"
            return data

        hash_input = f"{no_sertif}|{name}|{student_id}"
        data["hash_input"] = hash_input
        data["hash"] = generate_md5_hash(hash_input)
        return data

    except Exception as e:
        data["status"] = f"Gagal hashing: {str(e)}"
        return data