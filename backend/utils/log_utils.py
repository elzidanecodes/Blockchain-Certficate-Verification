from database.mongo import save_verify_log
from config import contract

def save_log(data: dict, verified_by: str = "admin") -> dict:
    try:
        certificate_id = data.get("certificate_id")
        contract_address = contract.address

        if not certificate_id:
            return {"status": "error", "message": "certificate_id tidak ditemukan"}

        save_verify_log({
            "certificate_id": certificate_id,
            "no_sertifikat": data.get("no_sertifikat"),
            "contract_address": contract_address,
            "ipfs_cid": data.get("ipfs_cid"),
            "ipfs_url": data.get("ipfs_url"),
            "qr_code": data.get("qr_code"),
            "hash": data.get("hash"),
            "verified_by": verified_by,
            "valid": data.get("valid", False),
            "result": "success" if data.get("valid") else "failed", 
            "note": "Sertifikat berhasil diverifikasi" if data.get("valid") else "Verifikasi gagal"
        })


        return {"status": "success", "certificate_id": certificate_id}

    except Exception as e:
        return {"status": "error", "message": str(e)}