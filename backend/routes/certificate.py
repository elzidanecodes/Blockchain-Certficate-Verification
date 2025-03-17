from flask import Blueprint, request, jsonify, send_file
import os
import json
import qrcode
from PIL import Image, ImageDraw, ImageFont
import requests
from security import generate_md5_hash
from datetime import datetime, timedelta

certificate_bp = Blueprint("certificate", __name__)

# Pastikan folder penyimpanan ada dan gunakan path absolut
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Direktori `backend/routes/`
BACKEND_DIR = os.path.dirname(BASE_DIR)  # Direktori `backend/`

CERTIFICATE_FOLDER = os.path.join(BACKEND_DIR, "static", "generated_certificates")

QR_FOLDER = os.path.join(BACKEND_DIR, "static", "qr_codes")

os.makedirs(CERTIFICATE_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

# Fungsi untuk generate QR Code
def generate_qr_code(data, output_file):
    qr = qrcode.make(data)
    qr.save(output_file)

def format_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")  # Ubah sesuai format input
        return date_obj.strftime("%d %B %Y")  # Format: "dd mm yyyy"
    except ValueError:
        return date_str  # Jika error, gunakan format asli

# Fungsi untuk membuat sertifikat dengan QR Code
def generate_certificate(data):
    template_path = os.path.join(BACKEND_DIR, "static", "certificate_template.png")  # Path absolut
    output_path = os.path.join(CERTIFICATE_FOLDER, f"{data['certificate_id']}.png")

    print(f"📂 Current working directory: {os.getcwd()}")  # Debugging
    print(f"🖼️ Template path: {template_path}")  # Debugging
    print(f"💾 Saving certificate at: {output_path}")  # Debugging

    # Cek apakah file template sertifikat ada
    if not os.path.exists(template_path):
        print("❌ Error: Template certificate file not found!")
        return None

    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)

    # Load font
    FONT_DIR = os.path.join(BACKEND_DIR, "static", "font")
    try:
        font_course_id = ImageFont.truetype(os.path.join(FONT_DIR, "Montserrat-SemiBold.ttf"), 35)
        font_name = ImageFont.truetype(os.path.join(FONT_DIR, "lucien-schoenschriftv-regular.ttf"), 150)
        font_date = ImageFont.truetype(os.path.join(FONT_DIR, "Montserrat-Medium.ttf"), 26)
        font_date_implement = ImageFont.truetype(os.path.join(FONT_DIR, "Montserrat-Bold.ttf"), 30)
    except IOError:
        print("⚠️ Font tidak ditemukan, menggunakan default!")
        font_course_id = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_date = ImageFont.load_default()
    
    # **Posisi Elemen Sertifikat**
    course_id_x, course_id_y = 542, 678
    name_x, name_y = 513, 835
    date_x, date_y = 513, 1275
    qr_x, qr_y = 1990, 1270
    expiry_x, expiry_y = 1875, 1550

    # **Course ID** 
    draw.text((course_id_x, course_id_y), f"{data['courseid']}", fill="white", font=font_course_id)
    

    # **Nama** 
    draw.text((name_x, name_y), f"{data['name']}", fill=(31, 142, 126), font=font_name)

    # **Format tanggal startdate dan enddate**
    formatted_startdate = format_date(data['startdate'])
    formatted_enddate = format_date(data['enddate'])

    # **Tanggal Pelaksanaan**
    draw.text((date_x, date_y), f"{formatted_startdate} - {formatted_enddate}", fill="black", font=font_date_implement)

    # ** Masa berlaku sertifikat (3 tahun setelah enddate)**
    try:
        end_date_obj = datetime.strptime(data['enddate'], "%Y-%m-%d")
        expiry_date = end_date_obj + timedelta(days=3*365)
        expiry_text = f"Berlaku hingga {expiry_date.strftime('%d %B %Y')}"
    except ValueError:
        expiry_text = "Berlaku hingga: - (format tanggal salah)"
    
    draw.text((expiry_x, expiry_y), expiry_text, fill="black", font=font_date)


    # **Tambahkan QR Code ke sertifikat**
    qr_data = json.dumps(data)
    qr_output = os.path.join(QR_FOLDER, f"{data['certificate_id']}.png")
    generate_qr_code(qr_data, qr_output)

    qr_img = Image.open(qr_output).resize((200, 200))
    img.paste(qr_img, (qr_x, qr_y))

    img.save(output_path)
    return output_path


# **Tambahkan Sertifikat ke Blockchain Setelah Generate**
def add_certificate_to_blockchain(certificate_id):
    blockchain_url = "http://127.0.0.1:5000/blockchain/add_certificate"

    certificate_hash = generate_md5_hash(certificate_id)
    response = requests.post(blockchain_url, json={"certificate_hash": certificate_hash})

    if response.status_code == 200:
        print(f"✅ Sertifikat berhasil ditambahkan ke blockchain! TX Hash: {response.json().get('tx_hash')}")
    else:
        print(f"❌ Gagal menyimpan ke blockchain! Error: {response.text}")

# **Endpoint Generate Sertifikat**
@certificate_bp.route("/generate_certificate", methods=["POST"])
def generate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    required_fields = ["name", "coursename", "courseid", "startdate", "enddate"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    data['certificate_id'] = generate_md5_hash(data['name'] + data['coursename'])
    certificate_path = generate_certificate(data)

    if not certificate_path:
        return jsonify({"error": "Failed to generate certificate"}), 500

    # **Tambahkan ke Blockchain**
    add_certificate_to_blockchain(data['certificate_id'])

    return jsonify({
        "message": "Certificate generated successfully",
        "certificate_id": data['certificate_id'],
        "download_url": f"/certificate/download_certificate/{data['certificate_id']}.png"
    }), 200

# Endpoint untuk mengunduh sertifikat
@certificate_bp.route("/download_certificate/<filename>", methods=["GET"])
def download_certificate(filename):
    file_path = os.path.join(CERTIFICATE_FOLDER, filename)
    
    print(f"Trying to download file: {file_path}")  # Debugging

    if os.path.exists(file_path):
        print("Certificate found, sending file.")  # Debugging
        return send_file(file_path, as_attachment=True)

    print("Certificate not found!")  # Debugging
    return jsonify({"error": "Certificate not found"}), 404