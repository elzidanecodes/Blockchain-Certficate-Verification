from flask import Blueprint, request, jsonify
from datetime import datetime
import time
from PIL import Image, ImageDraw, ImageFont
import easyocr
import base64
import io
import numpy as np
import os
from PIL import Image 
from pyzbar.pyzbar import decode
from urllib.parse import urlparse, parse_qs
from config import web3, contract
from crypto.hash_utils import generate_md5_hash
from crypto.rsa_utils import verify_signature, load_public_key
from database.mongo import get_certificate_by_id, save_verification_result

verification_bp = Blueprint("verification", __name__)
reader = easyocr.Reader(['en', 'id'], gpu=False)

def extract_text_from_image(results):
    from datetime import datetime
    import re

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
            name_parts = []
            for j in range(1, 4):
                if i + j < len(results):
                    next_line = results[i + j].strip()
                    if re.match(r'^\d{1,2} [A-Za-z]+ \d{4}$', next_line):
                        break
                    if re.match(r'^[A-Z]{2,4}\d{4,}$', next_line):
                        break
                    if len(next_line.split()) > 4:
                        break
                    name_parts.append(next_line)
            name = " ".join(name_parts).strip()
            break

    # =====================[ 2. CARI DAN BENTUK TANGGAL LENGKAP ]=====================
    raw_dates = []
    for i in range(len(results) - 2):
        d, m, y = results[i:i+3]
        if d.isdigit() and m in months and y.isdigit():
            full_date = f"{int(d):02d} {m} {y}"
            raw_dates.append(full_date)

    # Fallback: juga cari tanggal langsung dari gabungan string
    joined_text = " ".join(results)
    regex_dates = re.findall(r'\d{1,2} [A-Za-z]+ \d{4}', joined_text)
    for d in regex_dates:
        if d not in raw_dates:
            raw_dates.append(d)

    def parse_date(dstr):
        try:
            return datetime.strptime(dstr, "%d %B %Y")
        except:
            return None

    if len(raw_dates) >= 2:
        candidates = []
        for i in range(len(raw_dates)):
            for j in range(i + 1, len(raw_dates)):
                d1 = parse_date(raw_dates[i])
                d2 = parse_date(raw_dates[j])
                if d1 and d2:
                    delta = abs((d2 - d1).days)
                    if 5 <= delta <= 365:
                        start, end = sorted([d1, d2])
                        candidates.append((start.strftime("%d %B %Y"), end.strftime("%d %B %Y"), delta))
        if candidates:
            best = sorted(candidates, key=lambda x: x[2])[0]
            start_date, end_date = best[0], best[1]

    # =====================[ DEBUG + VALIDASI ]=====================
    print("📌 name:", name)
    print("📌 course_id:", course_id)
    print("📌 dates:", raw_dates)

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
    step_durations = {}

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

        start_ocr = time.perf_counter()
        extracted_text = extract_text_from_image(results)
        step_durations["extract"] = time.perf_counter() - start_ocr

        if not extracted_text or not extracted_text.strip():
            print("❌ extracted_text kosong atau tidak valid:", extracted_text)
            return jsonify({"error": "Could not extract valid certificate data"}), 400

        print("📦 extracted_text:", extracted_text)
        
        # Parsing hasil OCR yang sudah di-join
        try:
            name, course_id, start_date, end_date = extracted_text.split("|")
        except:
            name = "-"
            course_id = "-"
            start_date = "-"
            end_date = "-"

        

        hash_ulang = generate_md5_hash(extracted_text)
        print("🔐 Hash ulang (MD5):", hash_ulang)
        
        start_blockchain = time.perf_counter()
        valid, cert_id, blockchain_signature_b64 = contract.functions.getCertificate(certificate_id).call()
        step_durations["blockchain"] = time.perf_counter() - start_blockchain
        print("🧾 Dari blockchain:", valid, cert_id, blockchain_signature_b64)

        if not valid or not blockchain_signature_b64:
            return jsonify({"error": "Certificate not found or invalid on blockchain"}), 404

        start_rsa = time.perf_counter()
        rsa_valid = verify_signature(hash_ulang, blockchain_signature_b64)
        step_durations["rsa"] = time.perf_counter() - start_rsa
        print("🔏 Signature RSA valid:", rsa_valid)
        result_valid = rsa_valid
        
        start_generate = time.perf_counter()
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        label_text = "Signature: VALID" if result_valid else "Signature: INVALID"
        label_color = "green" if result_valid else "red"
        draw.text((100, img.height - 50), label_text, fill=label_color, font=font)

        # ===== Tambahkan tanda tangan =====
        if result_valid:
            try:
                ttd_path = os.path.abspath(os.path.join("static", "ttd.png"))
                ttd_img = Image.open(ttd_path).convert("RGBA").resize((250, 100))
                img.paste(ttd_img, (513, 1300), ttd_img)  # posisi di bawah tanggal, sesuaikan jika perlu
            except Exception as e:
                print("⚠️ Gagal menambahkan tanda tangan:", str(e))


        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        step_durations["generate"] = time.perf_counter() - start_generate
        
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
            "valid": rsa_valid,
            "image_base64": img_base64,
            "hash": hash_ulang,
            "name": name,
            "course_id": course_id,
            "start_date": start_date,
            "end_date": end_date,
            "verified_at": datetime.utcnow().isoformat(),
            "step_durations": {
                "extract": int(step_durations["extract"] * 1000),
                "blockchain": int(step_durations["blockchain"] * 1000),
                "rsa": int(step_durations["rsa"] * 1000),
                "generate": int(step_durations["generate"] * 1000),
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@verification_bp.route("/get_verified_image/<certificate_id>", methods=["GET"])
def get_verified_image(certificate_id):
    contract_address = contract.address
    record = get_certificate_by_id(certificate_id, contract_address)

    if not record or "verification_result" not in record:
        return jsonify({"error": "Data tidak ditemukan"}), 404

    image_base64 = record["verification_result"].get("image_base64", "")
    return jsonify({"image_base64": image_base64})