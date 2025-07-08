from flask import Blueprint, request, jsonify, send_file, after_this_request
from datetime import datetime
import time
from PIL import Image, ImageDraw, ImageFont
import easyocr
import base64
import io
import numpy as np
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
import zipfile
import tempfile
from PIL import Image 
from datetime import datetime
from pyzbar.pyzbar import decode
from io import BytesIO
from urllib.parse import urlparse, parse_qs
from flask import session
from config import contract, AES_SECRET_KEY
from crypto.hash_utils import generate_md5_hash
from crypto.rsa_utils import verify_signature
from database.mongo import get_certificate_by_id, save_verify_log, collection_verify_logs
from routes.blockchain import get_certificate_data
from routes.certificate import regenerate_verified_certificate
from crypto.aes_utils import decrypt_data
from ipfs.ipfs_utils import upload_to_ipfs
from database.auth import get_fingerprint

verification_bp = Blueprint("verification", __name__)
reader = easyocr.Reader(['en', 'id'], gpu=True)

def extract_text_from_image(results):

    print("📄 Hasil EasyOCR:")
    for r in results:
        print("-", r)

    if not results or len(results) < 3:
        print("❌ OCR hasil terlalu sedikit:", results)
        return ""

    no_sertifikat = ""
    name = ""
    student_id = ""
    department = ""
    test_date = ""

    combined = list(map(str.strip, results))
    for i, line in enumerate(combined):
        line_lower = line.lower()

        # Tangkap No Sertifikat
        if "no:" in line_lower and not no_sertifikat:
            # Ambil setelah "No:" jika satu baris
            if ":" in line:
                parts = line.split(":")
                if len(parts) > 1 and len(parts[1].strip()) > 5:
                    no_sertifikat = parts[1].strip()
            # Atau baris berikutnya
            elif i + 1 < len(combined):
                next_line = combined[i + 1].strip()
                if len(next_line) > 5:
                    no_sertifikat = next_line

        # Tangkap Nama (setelah label 'Name')
        elif "name" in line_lower and not name:
            if i + 1 < len(combined):
                possible_name = combined[i + 1].strip()
                if len(possible_name.split()) >= 2:
                    name = possible_name

        # Tangkap Student ID
        elif "student id" in line_lower and not student_id:
            if i + 1 < len(combined):
                sid = combined[i + 1].strip()
                if sid.isdigit() and len(sid) >= 6:
                    student_id = sid
            elif line.strip().isdigit() and len(line.strip()) >= 6:
                student_id = line.strip()
                
        # Department
        elif "department" in line_lower and not department:
            if i + 1 < len(combined):
                department = combined[i + 1].strip()

        # Test Date
        elif "test date" in line_lower and not test_date:
            if i + 1 < len(combined):
                test_date_line = combined[i + 1].strip()
                if test_date_line.startswith(":"):
                    test_date_line = test_date_line[1:].strip()
                test_date = test_date_line

    ocr_string = f"{no_sertifikat}|{name}|{student_id}|{department}|{test_date}"
    print("📌 Ekstrak OCR:", ocr_string)

    if all([no_sertifikat, name, student_id]):
        return {
            "no_sertifikat": no_sertifikat,
            "name": name,
            "student_id": student_id,
            "department": department,
            "test_date": test_date
        }
    return {}

def extract_certificate_id_from_qr(image):
    decoded_objects = decode(image)
    for obj in decoded_objects:
        data = obj.data.decode("utf-8")
        if data.startswith("https://127.0.0.1:5000"):
            parsed_url = urlparse(data)
            query = parse_qs(parsed_url.query)
            return query.get("certificate_id", [None])[0]
    return None

@verification_bp.route("/verify_certificate", methods=["POST"])
def verify():
    # Validasi session fingerprint
    expected_fingerprint = session.get("fingerprint")
    current_fingerprint = get_fingerprint()

    if expected_fingerprint != current_fingerprint:
        session.clear()
        return jsonify({"error": "Session mismatch"}), 401

    # Validasi role
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        img = Image.open(file.stream).convert("RGB")
        img_resize = img.resize((img.width // 2, img.height // 2))
        img_np = np.array(img_resize)

        # Ambil certificate_id dari QR
        certificate_id = extract_certificate_id_from_qr(img_np)
        if not certificate_id:
            return jsonify({"error": "QR Code tidak valid"}), 400
        
        # ❗️ Cek apakah sudah diverifikasi sebelumnya
        existing_log = collection_verify_logs.find_one({
            "certificate_id": {"$regex": f"^{certificate_id}$", "$options": "i"},
            "valid": True
        })
        if existing_log:
            return jsonify({
                "already_verified": True,
                "certificate_id": certificate_id,
                "note": existing_log.get("note", "Sertifikat ini sudah diverifikasi sebelumnya."),
                "verified_at": existing_log.get("timestamp").strftime("%Y-%m-%d %H:%M:%S"),
            }), 200

        # OCR
        start_ocr = time.time()
        print("🔍 Mulai OCR pada gambar...")
        results = reader.readtext(img_np, detail=0)
        end_ocr = time.time()
        print(f"⏱️ OCR waktu: {round(end_ocr - start_ocr, 2)} detik")

        extracted_text = extract_text_from_image(results)
        if not extracted_text:
            return jsonify({"error": "Gagal mengekstrak data dari gambar"}), 400

        no_sertif = extracted_text["no_sertifikat"]
        name = extracted_text["name"]
        student_id = extracted_text["student_id"]
        department = extracted_text.get("department", "")
        test_date = extracted_text.get("test_date", "")

        hash_input = f"{no_sertif}|{name}|{student_id}"
        hash_ulang = generate_md5_hash(hash_input)
        print("🔍 Hash input:", hash_input)

        # Ambil signature dari blockchain
        valid, cert_id, blockchain_signature_b64 = get_certificate_data(certificate_id)
        
        if not valid:
            return jsonify({"error": "Certificate ID tidak ditemukan di blockchain"}), 404

        rsa_valid = verify_signature(hash_ulang, blockchain_signature_b64)
        contract_address = contract.address
        
        if rsa_valid:
            # 🔎 Ambil data terenkripsi dari MongoDB
            dataCert_db = get_certificate_by_id(certificate_id, contract_address)
            encrypted_info = dataCert_db.get("encrypted_data_sertif")
            if not encrypted_info:
                return jsonify({"error": "Data sertifikat tidak ditemukan di database"}), 404
            
            decrypted_data = decrypt_data(encrypted_info, AES_SECRET_KEY)
            if not decrypted_data:
                return jsonify({"error": "Gagal mendekripsi data sertifikat"}), 500
            
            img_bytes, img_base64, qr_base64 = regenerate_verified_certificate(decrypted_data, certificate_id)
            # Upload sertifikat hasil verifikasi ke IPFS
            
            ipfs_result = upload_to_ipfs(img_bytes)

            if ipfs_result:
                ipfs_cid = ipfs_result.get("cid")
                ipfs_url = ipfs_result.get("url")
                print("✅ Uploaded to IPFS with CID:", ipfs_cid)
            else:
                ipfs_cid = None
                ipfs_url = None
                print("❌ Gagal upload ke IPFS")

        save_verify_log({
            "certificate_id": certificate_id,
            "no_sertifikat": no_sertif,
            "contract_address": contract_address,
            "ipfs_cid": ipfs_cid,
            "ipfs_url": ipfs_url,
            "qr_code": qr_base64,
            "hash": hash_ulang,
            "verified_by": session.get("username", "admin"),
            "valid": rsa_valid,
            "result": "success" if rsa_valid else "failed",
            "note": "Sertifikat berhasil diverifikasi" if rsa_valid else "Verifikasi gagal"
        })


        return jsonify({
            "message": "Verifikasi selesai",
            "certificate_id": certificate_id,
            "valid": rsa_valid,
            "image_base64": img_base64,
            "ipfs_url": ipfs_url,
            "hash": hash_ulang,
            "name": name,
            "student_id": student_id,
            "no_sertifikat": no_sertif,
            "department": department,
            "test_date": test_date
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@verification_bp.route("/verify_certificate_zip", methods=["POST"])
def verify_certificate_zip():
    expected_fingerprint = session.get("fingerprint")
    current_fingerprint = get_fingerprint()

    if expected_fingerprint != current_fingerprint:
        session.clear()
        return jsonify({"error": "Session mismatch"}), 401

    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    username = session.get("username", "admin")
    uploaded_zip = request.files['file']

    try:
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        results = []
        zip_memory = BytesIO()

        def process_file(filename):
            try:
                path = os.path.join(temp_dir, filename)
                img = Image.open(path).convert("RGB")
                img_resize = img.resize((img.width // 2, img.height // 2))
                img_np = np.array(img_resize)

                certificate_id = extract_certificate_id_from_qr(img_np)
                if not certificate_id:
                    return {"file": filename, "status": "QR tidak ditemukan"}

                existing_log = collection_verify_logs.find_one({
                    "certificate_id": {"$regex": f"^{certificate_id}$", "$options": "i"},
                    "valid": True
                })
                if existing_log:
                    return {"certificate_id": certificate_id, "status": "Sudah diverifikasi"}
                
                start_ocr = time.time()
                print(f"🔍 Mulai OCR pada {filename}...")
                text_lines = reader.readtext(img_np, detail=0)
                end_ocr = time.time()
                print(f"⏱️ OCR waktu: {round(end_ocr - start_ocr, 2)} detik")

                extracted = extract_text_from_image(text_lines)
                if not extracted:
                    return {"certificate_id": certificate_id, "status": "OCR gagal"}

                no_sertif = extracted["no_sertifikat"]
                name = extracted["name"]
                student_id = extracted["student_id"]

                hash_input = f"{no_sertif}|{name}|{student_id}"
                hash_ulang = generate_md5_hash(hash_input)

                valid, cert_id, signature = get_certificate_data(certificate_id)
                if not valid:
                    return {"certificate_id": certificate_id, "status": "ID tidak ada di blockchain"}

                rsa_valid = verify_signature(hash_ulang, signature)
                contract_address = contract.address

                ipfs_cid = None
                ipfs_url = None
                qr_base64 = ""
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

                    # Tambahkan file ke ZIP memory langsung
                    zip_lock.acquire()
                    try:
                        with zipfile.ZipFile(zip_memory, 'a', zipfile.ZIP_DEFLATED) as zipf:
                            zipf.writestr(f"{certificate_id}.png", img_bytes)
                    finally:
                        zip_lock.release()

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

        from threading import Lock
        zip_lock = Lock()

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(process_file, os.listdir(temp_dir)))

        shutil.rmtree(temp_dir)
        zip_memory.seek(0)
        zip_base64 = base64.b64encode(zip_memory.read()).decode("utf-8")
        verified_success = [r for r in results if r.get("status") == "success"]

        return jsonify({
            "message": "Verifikasi selesai",
            "success": True,
            "verified_count": len(verified_success),
            "jumlah_total": len(results),
            "hasil": results,
            "zip_base64": zip_base64
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# Endpoint untuk API verifikasi sertifikat 
@verification_bp.route("/api/verify/<certificate_id>")
def api_verify_certificate(certificate_id):
    print("🔍 incoming certificate_id:", certificate_id)
    log = collection_verify_logs.find_one({
        "certificate_id": {"$regex": f"^{certificate_id}$", "$options": "i"}
    })
    if not log or not log.get("valid", False):
        return jsonify({"valid": False, "message": "Sertifikat belum diverifikasi"}), 404

    contract_address = log.get("contract_address") or contract.address

    return jsonify({
        "valid": True,
        "certificate_id": certificate_id,
        "name": log.get("name"),
        "student_id": log.get("student_id"),
        "department": log.get("department"),
        "no_sertifikat": log.get("no_sertifikat"),
        "test_date": log.get("test_date"),
        "hash": log.get("hash"),
        "ipfs_cid": log.get("ipfs_cid"),
        "ipfs_url": log.get("ipfs_url"),
        "verified_at": log.get("timestamp").strftime("%Y-%m-%d"),
        "note": log.get("note", "")
    })

@verification_bp.route("/download_zip", methods=["GET"])
def download_verified_zip():
    zip_path = session.get("last_verified_zip")
    if not zip_path or not os.path.exists(zip_path):
        return jsonify({"error": "File ZIP tidak ditemukan"}), 404

    @after_this_request
    def cleanup(response):
        try:
            os.remove(zip_path)
            shutil.rmtree(os.path.dirname(zip_path), ignore_errors=True)
        except Exception as e:
            print(f"❌ Gagal hapus sementara: {e}")
        return response

    return send_file(zip_path, as_attachment=True, download_name="hasil_verifikasi.zip")
    
@verification_bp.route("/get_verified_image/<certificate_id>", methods=["GET"])
def get_verified_image(certificate_id):
    
    
    contract_address = contract.address
    record = get_certificate_by_id(certificate_id, contract_address)

    if not record or "verification_result" not in record:
        return jsonify({"error": "Data tidak ditemukan"}), 404

    image_base64 = record["verification_result"].get("image_base64", "")
    return jsonify({"image_base64": image_base64})