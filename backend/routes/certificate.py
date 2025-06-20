from flask import Blueprint, request, jsonify, send_file
import io
import base64
import os
import qrcode
from PIL import ImageFont
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from config import contract, AES_SECRET_KEY
from database.mongo import save_certificate_data, get_certificate_by_id
from crypto.hash_utils import generate_md5_hash
from crypto.rsa_utils import load_private_key, sign_data
from crypto.aes_utils import encrypt_data
from routes.blockchain import store_signature

certificate_bp = Blueprint("certificate", __name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FONT_DIR = os.path.join(os.path.dirname(BASE_DIR), "static", "font")
TEMPLATE_PATH = os.path.join(os.path.dirname(BASE_DIR), "static", "pect_template.png")

# Fungsi untuk format tanggal
def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d %B %Y")
    except ValueError:
        return date_str

# Fungsi untuk mengambil certificate ID terbaru dari blockchain
def get_certificate_id_from_blockchain():
    return contract.functions.certificateCounter().call()

def generate_certificate(data):

    # Validasi input
    required_fields = [
        "no_sertifikat", "name", "student_id", "department", "test_date",
        "listening", "reading", "writing", "total_lr", "total_writing"
    ]
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"Missing required field: {field}")

    # Format hash input
    hash_input = f"{data['no_sertifikat']}|{data['name']}|{data['student_id']}"
    print("📌 HASH input saat generate:", hash_input)
    md5_hash = generate_md5_hash(hash_input)

    # Digital signature
    private_key = load_private_key()
    signature = sign_data(md5_hash, private_key)

    # Enkripsi data user
    user_info = {
        **{k: data[k] for k in required_fields},
    }
    encrypted_info = encrypt_data(user_info, AES_SECRET_KEY)

    # Transaksi ke blockchain
    certificate_id = store_signature(signature)
    contract_address = contract.address

    # Buat QR code
    qr_data = f"https://127.0.0.1:5000/verify?certificate_id={certificate_id}"
    qr_img = qrcode.make(qr_data).convert("RGBA").resize((200, 200))
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode()
    
    # Ambil pixel dan buat transparan
    datas = qr_img.getdata()
    newData = []
    for item in datas:
        # Jika putih, buat transparan
        if item[:3] == (255, 255, 255):
            newData.append((255, 255, 255, 0))  # 0 = transparan
        else:
            newData.append(item)

    qr_img.putdata(newData)

    # Load template sertifikat
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError("Template sertifikat tidak ditemukan")

    img = Image.open(TEMPLATE_PATH)
    draw = ImageDraw.Draw(img)

    # Font
    try:
        font_path = os.path.join(FONT_DIR, "Montserrat-SemiBold.ttf")
        font_default = ImageFont.truetype(font_path, 25)
        
    except IOError:
        font_default = font_big = ImageFont.load_default()

    # Insert data ke posisi yang sesuai
    draw.text((1005, 454), data["no_sertifikat"], font=font_default, fill="black")
    draw.text((415, 502), data["name"], font=font_default, fill="black")
    draw.text((415, 536), data["student_id"], font=font_default, fill="black")
    draw.text((1225, 502), data["department"], font=font_default, fill="black")
    draw.text((1225, 536), data["test_date"], font=font_default, fill="black")

    draw.text((640, 655), str(data["listening"]), font=font_default, fill="black")
    draw.text((980, 655), str(data["reading"]), font=font_default, fill="black")
    draw.text((1310, 655), str(data["total_lr"]), font=font_default, fill="black")

    draw.text((830, 948), str(data["writing"]), font=font_default, fill="black")
    draw.text((1130, 948), str(data["total_writing"]), font=font_default, fill="black")

    img.paste(qr_img, (880, 1090), qr_img)

    # Simpan hasil sertifikat ke buffer base64
    cert_buffer = io.BytesIO()
    img.save(cert_buffer, format="PNG")
    cert_base64 = base64.b64encode(cert_buffer.getvalue()).decode()

    # Simpan ke database
    save_certificate_data(
        certificate_id=certificate_id,
        contract_address=contract_address,
        encrypted_data_sertif=encrypted_info,
        qr_base64=qr_base64,
        cert_base64=cert_base64
    )

    return certificate_id

# Regenerate sertifikat terverifikasi
def regenerate_verified_certificate(data, certificate_id):
    # Load template
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError("Template sertifikat tidak ditemukan")

    img = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Load font
    try:
        font_path = os.path.join(FONT_DIR, "Montserrat-SemiBold.ttf")
        font = ImageFont.truetype(font_path, 25)
    except:
        font = ImageFont.load_default()

    # 🖊️ Tulis ulang seluruh data ke template
    draw.text((1005, 454), data["no_sertifikat"], font=font, fill="black")
    draw.text((415, 502), data["name"], font=font, fill="black")
    draw.text((415, 536), data["student_id"], font=font, fill="black")
    draw.text((1225, 502), data["department"], font=font, fill="black")
    draw.text((1225, 536), data["test_date"], font=font, fill="black")

    draw.text((640, 655), str(data["listening"]), font=font, fill="black")
    draw.text((980, 655), str(data["reading"]), font=font, fill="black")
    draw.text((1310, 655), str(data["total_lr"]), font=font, fill="black")
    draw.text((830, 948), str(data["writing"]), font=font, fill="black")
    draw.text((1130, 948), str(data["total_writing"]), font=font, fill="black")

    # Generate QR final → link publik
    qr_data = f"https://localhost:5173/verify/{certificate_id}"
    qr_img = qrcode.make(qr_data).convert("RGBA").resize((200, 200))

    # Transparan background putih
    datas = qr_img.getdata()
    newData = []
    for item in datas:
        if item[:3] == (255, 255, 255):
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    qr_img.putdata(newData)

    img.paste(qr_img, (880, 1090), qr_img)

    # Tambahkan tanda tangan
    try:
        ttd_img = Image.open("static/ttd.png").convert("RGBA").resize((250, 100))
        img.paste(ttd_img, (350, 1140), ttd_img)
        img.paste(ttd_img, (1400, 1140), ttd_img)
    except Exception as e:
        print("⚠️ Gagal pasang tanda tangan:", e)

    # Simpan image ke buffer dan encode base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    

    # QR juga ke base64 untuk disimpan
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode("utf-8")

    return img_bytes, img_base64, qr_base64

@certificate_bp.route("/generate_certificate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        certificate_id = generate_certificate(data)
        return jsonify({
            "message": "Certificate generated successfully",
            "certificate_id": certificate_id,
            "download_url": f"/certificate/download_certificate/{certificate_id}"
        }), 200

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@certificate_bp.route("/download_certificate/<certificate_id>", methods=["GET"])
def download_certificate(certificate_id):
    contract_address = contract.address 
    record = get_certificate_by_id(certificate_id, contract_address)

    if not record:
        return jsonify({"error": "Certificate not found"}), 404

    cert_b64 = record.get("certificate_png")
    if not cert_b64:
        return jsonify({"error": "Certificate image not stored"}), 404

    cert_binary = base64.b64decode(cert_b64)
    return send_file(
        io.BytesIO(cert_binary),
        mimetype="image/png",
        as_attachment=True,
        download_name=f"{certificate_id}.png"
    )