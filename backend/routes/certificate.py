from flask import Blueprint, request, jsonify, send_file
import io
import base64
import os
import qrcode
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from config import web3, contract, AES_SECRET_KEY
from database.mongo import save_certificate_data, get_certificate_by_id
from crypto.hash_utils import generate_md5_hash
from crypto.rsa_utils import load_private_key, sign_data
from crypto.aes_utils import encrypt_data
from routes.blockchain import store_signature

certificate_bp = Blueprint("certificate", __name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FONT_DIR = os.path.join(os.path.dirname(BASE_DIR), "static", "font")
TEMPLATE_PATH = os.path.join(os.path.dirname(BASE_DIR), "static", "certificate_template.png")

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
    required_fields = ["name", "coursename", "courseid", "startdate", "enddate"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"Missing required field: {field}")
    
    contract_address = contract.address
    # Hash + Signature + Encrypt
    start = format_date(data['startdate'])  # "31 January 2025"
    end = format_date(data['enddate'])      # "27 April 2025"
    hash_input = f"{data['name']}|{data['courseid']}|{start}|{end}"
    print("📄 Hash input:", hash_input)
    md5_hash = generate_md5_hash(hash_input)
    print("📄 MD5 Hash:", md5_hash)
    private_key = load_private_key()
    signature = sign_data(md5_hash, private_key)

    user_info = {
        "name": data["name"],
        "email": data.get("email", "-"),
        "phone": data.get("phone", "-"),
        "institution": data.get("institution", "-"),
        "course": data["coursename"],
        "course_id": data["courseid"],
        "start_date": data["startdate"],
        "end_date": data["enddate"]
    }
    encrypted_info = encrypt_data(user_info, AES_SECRET_KEY)

    # Transaksi Blockchain
    certificate_id = store_signature(signature)

    # QR Code base64
    qr_data = f"http://127.0.0.1:5000/verify?certificate_id={certificate_id}"
    qr = qrcode.make(qr_data)
    qr_buffer = io.BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_base64 = base64.b64encode(qr_buffer.getvalue()).decode("utf-8")
    qr_img = Image.open(io.BytesIO(qr_buffer.getvalue())).resize((200, 200))

    # Generate sertifikat dari template
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError("Certificate template not found.")

    img = Image.open(TEMPLATE_PATH)
    draw = ImageDraw.Draw(img)

    try:
        font_course_id = ImageFont.truetype(os.path.join(FONT_DIR, "Montserrat-SemiBold.ttf"), 35)
        font_name = ImageFont.truetype(os.path.join(FONT_DIR, "Montserrat-Bold.ttf"), 130)
        font_date = ImageFont.truetype(os.path.join(FONT_DIR, "Montserrat-Medium.ttf"), 26)
        font_date_implement = ImageFont.truetype(os.path.join(FONT_DIR, "Montserrat-Bold.ttf"), 45)
    except IOError:
        font_course_id = font_name = font_date = font_date_implement = ImageFont.load_default()

    draw.text((542, 678), f"{data['courseid']}", fill="white", font=font_course_id)
    draw.text((513, 835), f"{data['name']}", fill=(31, 142, 126), font=font_name)
    draw.text((513, 1255), f"{format_date(data['startdate'])} - {format_date(data['enddate'])}", fill="black", font=font_date_implement)

    try:
        expiry = datetime.strptime(data['enddate'], "%Y-%m-%d") + timedelta(days=3*365)
        expiry_text = f"Berlaku hingga {expiry.strftime('%d %B %Y')}"
    except ValueError:
        expiry_text = "Berlaku hingga: -"

    draw.text((1875, 1550), expiry_text, fill="black", font=font_date)
    img.paste(qr_img, (1990, 1270))

    # Simpan ke buffer dan encode base64
    cert_buffer = io.BytesIO()
    img.save(cert_buffer, format="PNG")
    cert_base64 = base64.b64encode(cert_buffer.getvalue()).decode("utf-8")

    # Simpan ke database
    save_certificate_data(
        certificate_id=certificate_id,
        contract_address = contract.address,
        encrypted_info=encrypted_info,
        qr_base64=qr_base64,
        cert_base64=cert_base64
    )

    return certificate_id

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