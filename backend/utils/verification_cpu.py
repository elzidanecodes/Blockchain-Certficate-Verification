from celery import shared_task
import numpy as np
import time
import cv2

from utils.qr_utils import extract_certificate_id_from_qr
from utils.ocr_utils import extract_text_from_image, get_reader
from crypto.hash_utils import generate_md5_hash
from crypto.rsa_utils import verify_signature
from crypto.aes_utils import decrypt_data
from routes.blockchain import get_certificate_data
from utils.image_utils import regenerate_verified_certificate
from database.mongo import get_certificate_by_id
from config import AES_SECRET_KEY, contract


@shared_task
def verification_cpu(data: dict) -> dict:
    start = time.time()
    """
    Task CPU: scan QR, OCR, verifikasi RSA, dekripsi AES, regenerate image.
    """
    try:
        image_np = np.array(data["image_np"]).astype("uint8")
        filename = data["filename"]
        username = data["username"]

        certificate_id = extract_certificate_id_from_qr(image_np)
        print("⏱️ QR decode:", time.time() - start)
        start = time.time()
        if not certificate_id:
            return {"file": filename, "status": "QR tidak ditemukan"}

        # Ambil signature dari blockchain
        is_valid, returned_id, signature = get_certificate_data(certificate_id)
        if not is_valid:
            return {"file": filename, "status": "ID tidak ada di blockchain"}

        # OCR untuk ambil data hash
        # Konversi ke grayscale
        if len(image_np.shape) == 3 and image_np.shape[2] == 3:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        text_lines = get_reader().readtext(image_np, detail=0)
        extracted = extract_text_from_image(text_lines)
        print("⏱️ OCR:", time.time() - start)
        start = time.time()
        if not extracted:
            return {"file": filename, "status": "OCR gagal"}

        # Hash untuk verifikasi
        hash_input = f"{extracted['no_sertifikat']}|{extracted['name']}|{extracted['student_id']}"
        hash_value = generate_md5_hash(hash_input)
        signature_valid = verify_signature(hash_value, signature)
        
        print("⏱️ RSA:", time.time() - start)
        start = time.time()
        if not signature_valid:
            return {"file": filename, "status": "Signature tidak valid"}

        # Ambil data terenkripsi
        cert_db = get_certificate_by_id(certificate_id, contract.address)
        encrypted = cert_db.get("encrypted_data_sertif")
        if not encrypted:
            return {"file": filename, "status": "Data terenkripsi tidak ditemukan"}

        decrypted_data = decrypt_data(encrypted, AES_SECRET_KEY)
        print("⏱️ AES:", time.time() - start)
        start = time.time()
        if not decrypted_data:
            return {"file": filename, "status": "Dekripsi gagal"}

        # Regenerasi sertifikat terverifikasi
        img_bytes, img_base64, qr_base64 = regenerate_verified_certificate(decrypted_data, certificate_id)
        print("⏱️ Regenerate:", time.time() - start)
        

        return {
            "filename": filename,
            "username": username,
            "certificate_id": certificate_id,
            "hash": hash_value,
            "rsa_valid": signature_valid,
            "extracted_data": extracted,
            "decrypted_data": decrypted_data,
            "img_bytes": img_bytes,
            "img_base64": img_base64,
            "qr_base64": qr_base64
        }

    except Exception as e:
        return {
            "file": data.get("filename", "unknown"),
            "status": "error",
            "message": str(e)
        }