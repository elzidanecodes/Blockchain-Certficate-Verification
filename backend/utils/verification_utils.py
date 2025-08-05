import numpy as np
from utils.qr_utils import extract_certificate_id_from_qr
from utils.ocr_utils import extract_text_from_image
from crypto.hash_utils import generate_md5_hash
from crypto.rsa_utils import verify_signature
from ipfs.ipfs_utils import upload_to_ipfs
from database.mongo import get_certificate_by_id, save_verify_log
from config import AES_SECRET_KEY, contract
from crypto.aes_utils import decrypt_data
from utils.image_utils import regenerate_verified_certificate
from utils.ocr_utils import reader


def process_single_certificate(npy_path, filename, username="admin"):
    try:
        image_np = np.load(npy_path)
        certificate_id = extract_certificate_id_from_qr(image_np)
        if not certificate_id:
            return {"file": filename, "status": "QR tidak ditemukan"}
        text_lines = reader.readtext(image_np, detail=0)
        extracted = extract_text_from_image(text_lines)
        if not extracted:
            return {"certificate_id": certificate_id, "status": "OCR gagal"}

        no_sertif = extracted["no_sertifikat"]
        name = extracted["name"]
        student_id = extracted["student_id"]
        hash_input = f"{no_sertif}|{name}|{student_id}"
        hash_ulang = generate_md5_hash(hash_input)

        from routes.blockchain import get_certificate_data
        valid, cert_id, signature = get_certificate_data(certificate_id)
        if not valid:
            return {"certificate_id": certificate_id, "status": "ID tidak ada di blockchain"}

        rsa_valid = verify_signature(hash_ulang, signature)
        contract_address = contract.address

        ipfs_cid, ipfs_url, qr_base64 = None, None, ""
        img_bytes = None

        if rsa_valid:
            cert_db = get_certificate_by_id(certificate_id, contract_address)
            encrypted = cert_db.get("encrypted_data_sertif")
            if not encrypted:
                return {"certificate_id": certificate_id, "status": "Data terenkripsi tidak ditemukan"}

            decrypted_data = decrypt_data(encrypted, AES_SECRET_KEY)
            if not decrypted_data:
                return {"certificate_id": certificate_id, "status": "Dekripsi gagal"}

            img_bytes, _, qr_base64 = regenerate_verified_certificate(decrypted_data, certificate_id)
            ipfs = upload_to_ipfs(img_bytes)
            if ipfs:
                ipfs_cid = ipfs.get("cid")
                ipfs_url = ipfs.get("url")

        save_verify_log({
            "certificate_id": certificate_id,
            "no_sertifikat": no_sertif,
            "contract_address": contract_address,
            "ipfs_cid": ipfs_cid,
            "ipfs_url": ipfs_url,
            "qr_code": qr_base64,
            "hash": hash_ulang,
            "verified_by": username,
            "valid": rsa_valid,
            "result": "success" if rsa_valid else "failed",
            "note": "Sertifikat berhasil diverifikasi" if rsa_valid else "Verifikasi gagal"
        })

        return {"certificate_id": certificate_id, "status": "success" if rsa_valid else "invalid"}

    except Exception as e:
        return {"file": filename, "status": f"Error: {str(e)}"}