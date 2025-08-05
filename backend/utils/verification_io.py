from celery import shared_task
from ipfs.ipfs_utils import upload_to_ipfs
from utils.log_utils import save_log

@shared_task
def verification_io(cpu_result: dict) -> dict:
    """
    Task IO: upload hasil verifikasi ke IPFS dan simpan log.
    Return lengkap agar cocok dengan frontend Validation.jsx.
    """
    try:

        # Validasi field wajib
        if "certificate_id" not in cpu_result or "img_bytes" not in cpu_result:
            return {
                "file": cpu_result.get("filename", "unknown"),
                "valid": False,
                "note": "Data tidak lengkap dari CPU task"
            }

        # Upload ke IPFS
        ipfs_result = upload_to_ipfs(
            cpu_result["img_bytes"],
            cpu_result["filename"]
        )

        # Simpan log verifikasi
        save_log({
            "certificate_id": cpu_result["certificate_id"],
            "no_sertifikat": cpu_result["decrypted_data"].get("no_sertifikat"),
            "contract_address": "",
            "ipfs_cid": ipfs_result.get("cid", ""),
            "ipfs_url": ipfs_result.get("url", ""),
            "qr_code": cpu_result.get("qr_base64", ""),
            "hash": cpu_result["hash"],
            "verified_by": cpu_result.get("username", "admin"),
            "valid": cpu_result["rsa_valid"]
        })

        # Ambil data hasil dekripsi untuk frontend
        decrypted = cpu_result["decrypted_data"]

        return {
            "file": cpu_result["filename"],
            "valid": cpu_result["rsa_valid"],
            "note": "Sertifikat berhasil diverifikasi." if cpu_result["rsa_valid"] else "Verifikasi gagal.",
            "certificate_id": cpu_result["certificate_id"],
            "no_sertifikat": decrypted.get("no_sertifikat"),
            "name": decrypted.get("name"),
            "student_id": decrypted.get("student_id"),
            "department": decrypted.get("department"),
            "test_date": decrypted.get("test_date"),
            "hash": cpu_result["hash"],
            "image_base64": cpu_result.get("img_base64", ""),
            "ipfs_url": ipfs_result.get("url", ""),
            "step_durations": cpu_result.get("step_durations", {})
        }

    except Exception as e:
        return {
            "file": cpu_result.get("filename", "unknown"),
            "valid": False,
            "note": f"Gagal verifikasi: {str(e)}"
        }