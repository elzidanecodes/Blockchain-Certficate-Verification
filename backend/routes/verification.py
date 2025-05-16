from flask import Blueprint, request, jsonify
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import easyocr
import base64
import io
import cv2
import re
import numpy as np
from pyzbar.pyzbar import decode
from urllib.parse import urlparse, parse_qs
from config import web3, contract
from crypto.hash_utils import generate_md5_hash
from crypto.rsa_utils import verify_signature, load_public_key
from database.mongo import get_certificate_by_id, save_verification_result

verification_bp = Blueprint("verification", __name__)
reader = easyocr.Reader(['en', 'id'], gpu=False)

def extract_text_from_image(results):
    print("📄 Hasil EasyOCR:")
    for r in results:
        print("-", r)

    if not results or len(results) < 3:
        print("❌ OCR hasil terlalu sedikit:", results)
        return ""

    course_id = ""
    name = ""
    start_date = ""
    end_date = ""

    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # =====================[ 1. CARI COURSE_ID DAN NAMA ]=====================
    for i, text in enumerate(results):
        if re.match(r'^[A-Z]{2,4}\d{4,}$', text.strip()) and not course_id:
            course_id = text.strip()
            # Gabungkan nama dari baris selanjutnya (maks 2 baris)
            name_parts = []
            for j in range(1, 4):  # tambahkan satu baris, total maksimal 3
                if i + j < len(results):
                    next_line = results[i + j].strip()
                    if re.match(r'^\d{1,2} [A-Za-z]+ \d{4}$', next_line):
                        break
                    if re.match(r'^[A-Z]{2,4}\d{4,}$', next_line):
                        break
                    if len(next_line.split()) > 4:
                        break  # ❗hindari kalimat panjang seperti deskripsi pelatihan
                    name_parts.append(next_line)
            name = " ".join(name_parts).strip()
            break

    # =====================[ 2. CARI TANGGAL ]=====================
    joined_text = " ".join(results)
    date_matches = re.findall(r'\d{1,2} [A-Za-z]+ \d{4}', joined_text)

    # Tangani jika tanggal terpecah: ["08", "May", "2025"]
    for i in range(len(results) - 2):
        d, m, y = results[i:i+3]
        if d.isdigit() and m in months and y.isdigit():
            full_date = f"{d} {m} {y}"
            if full_date not in date_matches:
                date_matches.append(full_date)

    if len(date_matches) >= 2:
        start_date, end_date = date_matches[:2]

    # =====================[ DEBUG ]=====================
    print("📌 name:", name)
    print("📌 course_id:", course_id)
    print("📌 dates:", date_matches)

    # =====================[ VALIDASI AKHIR ]=====================
    if all([name, course_id, start_date, end_date]):
        final_data = f"{name}|{course_id}|{start_date}|{end_date}"
        print("📌 Ekstrak final:", final_data)
        return final_data
    else:
        print("❌ Data tidak lengkap.")
        return ""

def extract_certificate_id_from_qr(image):
    decoded_objects = decode(image)
    for obj in decoded_objects:
        data = obj.data.decode("utf-8")
        if data.startswith("http://127.0.0.1:5000"):
            parsed_url = urlparse(data)
            query = parse_qs(parsed_url.query)
            return query.get("certificate_id", [None])[0]
    return None

@verification_bp.route("/verify_certificate", methods=["POST"])
def verify():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        img = Image.open(file.stream)
        img_np = np.array(img)

        certificate_id = request.form.get("certificate_id") or extract_certificate_id_from_qr(img_np)
        if not certificate_id:
            return jsonify({"error": "QR Code not valid or certificate_id not found"}), 400

        print("🔎 Certificate ID yang terdeteksi:", certificate_id)

        results = reader.readtext(img_np, detail=0)
        print("🧠 OCR Results Mentah:", results)

        extracted_text = extract_text_from_image(results)
        if not extracted_text or not extracted_text.strip():
            print("❌ extracted_text kosong atau tidak valid:", extracted_text)
            return jsonify({"error": "Could not extract valid certificate data"}), 400

        print("📦 extracted_text:", extracted_text)

        hash_ulang = generate_md5_hash(extracted_text)
        print("🔐 Hash ulang (MD5):", hash_ulang)

        valid, cert_id, blockchain_signature_b64 = contract.functions.getCertificate(certificate_id).call()
        print("🧾 Dari blockchain:", valid, cert_id, blockchain_signature_b64)

        if not valid or not blockchain_signature_b64:
            return jsonify({"error": "Certificate not found or invalid on blockchain"}), 404

        public_key = load_public_key()
        rsa_valid = verify_signature(hash_ulang, blockchain_signature_b64)
        print("🔏 Signature RSA valid:", rsa_valid)

        result_valid = rsa_valid

        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        label_text = "Signature: VALID" if result_valid else "Signature: INVALID"
        label_color = "green" if result_valid else "red"
        draw.text((100, img.height - 50), label_text, fill=label_color, font=font)

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        contract_address = contract.address
        save_verification_result({
            "certificate_id": certificate_id,
            "contract_address": contract_address,
            "timestamp": datetime.utcnow(),
            "image_base64": img_base64,
            "hash": hash_ulang,
            "valid": result_valid
        })


        return jsonify({
            "message": "Verification completed",
            "certificate_id": certificate_id,
            "valid": result_valid
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500