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
import time

import re
from typing import Dict, Tuple

def _norm(s: str) -> str:
    if s is None:
        return ""
    s = s.lower().strip()
    s = re.sub(r'\s+', ' ', s)                  # normalisasi spasi
    s = re.sub(r'[^a-z0-9/\-_. ]', '', s)       # buang karakter aneh (noise OCR)
    return s

def _levenshtein(a: str, b: str) -> int:
    n, m = len(a), len(b)
    if n == 0: return m
    if m == 0: return n
    prev = list(range(m+1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            ins = cur[j-1] + 1
            delete = prev[j] + 1
            sub = prev[j-1] + (0 if ca == cb else 1)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]

def _sim_ratio(a: str, b: str) -> float:
    a, b = _norm(a), _norm(b)
    if not a and not b:
        return 1.0
    dist = _levenshtein(a, b)
    M = max(len(a), len(b))
    return 1.0 - (dist / M if M else 0.0)

def compute_ocr_accuracy(ocr: Dict[str, str], gt: Dict[str, str]) -> Tuple[float, Dict[str, float]]:
    """
    Hitung akurasi OCR per-field (persentase 0..100) + rata-rata.
    Field: no_sertifikat, name, student_id, department, test_date
    """
    fields = ["no_sertifikat", "name", "student_id", "department", "test_date"]
    per_field = {}
    sims = []
    for f in fields:
        s = _sim_ratio(ocr.get(f, ""), gt.get(f, ""))
        per_field[f] = round(s * 100, 2)
        sims.append(s)
    avg = round(sum(sims) / len(fields) * 100, 2)
    return avg, per_field

def compute_hash_match_rate(hash_from_ocr: str, hash_from_gt: str) -> float:
    """100 kalau match, 0 kalau tidak."""
    return 100.0 if (hash_from_ocr or "").lower() == (hash_from_gt or "").lower() else 0.0



def process_single_certificate(npy_path, filename, username="admin"):
    start_time = time.perf_counter() 
    certificate_id = None
    contract_address = getattr(contract, "address", None)

    try:
        image_np = np.load(npy_path)

        # 1) QR → certificate_id
        certificate_id = extract_certificate_id_from_qr(image_np)
        if not certificate_id:
            verification_time = round(time.perf_counter() - start_time, 4)
            # log kegagalan + waktu
            save_verify_log({
                "certificate_id": None,
                "file_name": filename,
                "contract_address": contract_address,
                "verified_by": username,
                "valid": False,
                "result": "failed",
                "note": "QR tidak ditemukan",
                "metrics": {
                    "OCR_Accuracy": None,
                    "OCR_Accuracy_Per_Field": {},
                    "Hash_Match_Rate": None,
                    "RSA_Verification_Success": 0.0,
                    "Verification_Time": verification_time,
                }
            })
            return {"file": filename, "status": "QR tidak ditemukan", "verification_time": verification_time}

        # 2) OCR → fields
        text_lines = reader.readtext(image_np, detail=0)
        extracted = extract_text_from_image(text_lines)
        if not extracted:
            verification_time = round(time.perf_counter() - start_time, 4)
            save_verify_log({
                "certificate_id": certificate_id,
                "file_name": filename,
                "contract_address": contract_address,
                "verified_by": username,
                "valid": False,
                "result": "failed",
                "note": "OCR gagal",
                "metrics": {
                    "OCR_Accuracy": 0.0,
                    "OCR_Accuracy_Per_Field": {},
                    "Hash_Match_Rate": 0.0,
                    "RSA_Verification_Success": 0.0,
                    "Verification_Time": verification_time,
                }
            })
            return {"certificate_id": certificate_id, "status": "OCR gagal", "verification_time": verification_time}

        # alias
        ocr_fields = extracted or {}
        no_sertif = ocr_fields.get("no_sertifikat", "")
        name = ocr_fields.get("name", "")
        student_id = ocr_fields.get("student_id", "")

        # 3) HASH dari OCR (format sama seperti generate)
        ocr_concat = f"{no_sertif}|{name}|{student_id}"
        hash_ulang = generate_md5_hash(ocr_concat)

        # 4) Ambil data dari blockchain
        from routes.blockchain import get_certificate_data
        valid, cert_id, signature = get_certificate_data(certificate_id)
        if not valid:
            verification_time = round(time.perf_counter() - start_time, 4)
            save_verify_log({
                "certificate_id": certificate_id,
                "file_name": filename,
                "contract_address": contract_address,
                "verified_by": username,
                "valid": False,
                "result": "failed",
                "note": "ID tidak ada di blockchain",
                "hash": hash_ulang,
                "metrics": {
                    "OCR_Accuracy": None,
                    "OCR_Accuracy_Per_Field": {},
                    "Hash_Match_Rate": None,
                    "RSA_Verification_Success": 0.0,
                    "Verification_Time": verification_time,
                }
            })
            return {"certificate_id": certificate_id, "status": "ID tidak ada di blockchain", "verification_time": verification_time}

        # 5) Verifikasi RSA
        rsa_valid = verify_signature(hash_ulang, signature)

        ipfs_cid, ipfs_url, qr_base64 = None, None, ""
        ocr_accuracy = None
        ocr_accuracy_per_field = {}
        hash_match_rate = None
        rsa_verification_success = 100.0 if rsa_valid else 0.0

        # 6) Jika RSA valid → decrypt GT dan hitung metrik
        if rsa_valid:
            cert_db = get_certificate_by_id(certificate_id, contract_address)
            encrypted = cert_db.get("encrypted_data_sertif")
            if not encrypted:
                verification_time = round(time.perf_counter() - start_time, 4)
                save_verify_log({
                    "certificate_id": certificate_id,
                    "file_name": filename,
                    "contract_address": contract_address,
                    "verified_by": username,
                    "valid": False,
                    "result": "failed",
                    "note": "Data terenkripsi tidak ditemukan",
                    "hash": hash_ulang,
                    "metrics": {
                        "OCR_Accuracy": None,
                        "OCR_Accuracy_Per_Field": {},
                        "Hash_Match_Rate": None,
                        "RSA_Verification_Success": 0.0,
                        "Verification_Time": verification_time,
                    }
                })
                return {"certificate_id": certificate_id, "status": "Data terenkripsi tidak ditemukan", "verification_time": verification_time}

            decrypted_data = decrypt_data(encrypted, AES_SECRET_KEY)
            if not decrypted_data:
                verification_time = round(time.perf_counter() - start_time, 4)
                save_verify_log({
                    "certificate_id": certificate_id,
                    "file_name": filename,
                    "contract_address": contract_address,
                    "verified_by": username,
                    "valid": False,
                    "result": "failed",
                    "note": "Dekripsi gagal",
                    "hash": hash_ulang,
                    "metrics": {
                        "OCR_Accuracy": None,
                        "OCR_Accuracy_Per_Field": {},
                        "Hash_Match_Rate": None,
                        "RSA_Verification_Success": 0.0,
                        "Verification_Time": verification_time,
                    }
                })
                return {"certificate_id": certificate_id, "status": "Dekripsi gagal", "verification_time": verification_time}

            # GT fields
            gt_fields = {
                "no_sertifikat": decrypted_data.get("no_sertifikat", ""),
                "name":          decrypted_data.get("name", ""),
                "student_id":    decrypted_data.get("student_id", ""),
                "department":    decrypted_data.get("department", ""),
                "test_date":     decrypted_data.get("test_date", ""),
            }

            # OCR Accuracy (per-field & rata2)
            ocr_accuracy, ocr_accuracy_per_field = compute_ocr_accuracy(ocr_fields, gt_fields)

            # Hash Match Rate (MD5 OCR vs MD5 GT)
            gt_concat = f"{gt_fields['no_sertifikat']}|{gt_fields['name']}|{gt_fields['student_id']}"
            hash_from_gt = generate_md5_hash(gt_concat).lower()
            hash_from_ocr = (hash_ulang or "").lower()
            hash_match_rate = compute_hash_match_rate(hash_from_ocr, hash_from_gt)

            # regenerate & upload IPFS
            img_bytes, _, qr_base64 = regenerate_verified_certificate(decrypted_data, certificate_id)
            ipfs = upload_to_ipfs(img_bytes)
            if ipfs:
                ipfs_cid = ipfs.get("cid")
                ipfs_url = ipfs.get("url")

        # 7) Akhiri timer & simpan log
        verification_time = round(time.perf_counter() - start_time, 4)  # ⏱ selesai

        save_verify_log({
            "certificate_id": certificate_id,
            "file_name": filename,
            "no_sertifikat": no_sertif,
            "name": name,
            "student_id": student_id,
            "contract_address": contract_address,
            "ipfs_cid": ipfs_cid,
            "ipfs_url": ipfs_url,
            "qr_code": qr_base64,
            "hash": hash_ulang,
            "verified_by": username,
            "valid": rsa_valid,
            "result": "success" if rsa_valid else "failed",
            "note": "Sertifikat berhasil diverifikasi" if rsa_valid else "Verifikasi gagal",

            # === METRICS ===
            "metrics": {
                "OCR_Accuracy": ocr_accuracy,                         # float 0..100
                "OCR_Accuracy_Per_Field": ocr_accuracy_per_field,     # dict per field
                "Hash_Match_Rate": hash_match_rate,                   # 0/100
                "RSA_Verification_Success": rsa_verification_success, # 0/100
                "Verification_Time": verification_time                # ⏱ detik
            }
        })

        return {
            "certificate_id": certificate_id,
            "status": "success" if rsa_valid else "invalid",
            "verification_time": verification_time,  # ikut di return juga
            "metrics": {
                "OCR_Accuracy": ocr_accuracy,
                "Hash_Match_Rate": hash_match_rate,
                "RSA_Verification_Success": rsa_verification_success
            }
        }

    except Exception as e:
        verification_time = round(time.perf_counter() - start_time, 4)
        # log error juga biar CSV tetap ada waktunya
        save_verify_log({
            "certificate_id": certificate_id,
            "file_name": filename,
            "contract_address": contract_address,
            "verified_by": username,
            "valid": False,
            "result": "failed",
            "note": f"Error: {str(e)}",
            "metrics": {
                "OCR_Accuracy": None,
                "OCR_Accuracy_Per_Field": {},
                "Hash_Match_Rate": None,
                "RSA_Verification_Success": 0.0,
                "Verification_Time": verification_time,
            }
        })
        return {"file": filename or "unknown", "status": f"Error: {str(e)}", "verification_time": verification_time}