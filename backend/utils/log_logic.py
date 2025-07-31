from database.mongo import save_verify_log
from config import contract

def simpan_log_verifikasi(data, verified_by="admin"):
    certificate_id = data.get("certificate_id")
    contract_address = contract.address

    save_verify_log({
        "certificate_id": certificate_id,
        "no_sertifikat": data.get("no_sertifikat"),
        "contract_address": contract_address,
        "ipfs_cid": data.get("ipfs_cid"),
        "ipfs_url": data.get("ipfs_url"),
        "qr_code": data.get("qr_code"),
        "hash": data.get("hash"),
        "verified_by": verified_by,
        "valid": data.get("rsa_valid", False),
        "result": "success" if data.get("rsa_valid") else "failed",
        "note": "Sertifikat berhasil diverifikasi" if data.get("rsa_valid") else "Verifikasi gagal"
    })

    return {
        "certificate_id": certificate_id,
        "status": "success" if data.get("rsa_valid") else "failed"
    }