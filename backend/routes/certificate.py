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
    """Fungsi untuk mengubah format tanggal ke '12 Agustus 2025'"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")  # Ubah sesuai format input
        return date_obj.strftime("%d %B %Y")  # Format: "12 Agustus 2025"
    except ValueError:
        return date_str  # Jika error, gunakan format asli

# Fungsi untuk membuat sertifikat dengan QR Code
def generate_certificate(data):
    template_path = os.path.join(BACKEND_DIR, "static", "certificate_template.png")  # Path absolut
    output_path = os.path.join(CERTIFICATE_FOLDER, f"{data['certificate_id']}.png")

    print(f"Current working directory: {os.getcwd()}")  # Debugging
    print(f"Template path: {template_path}")  # Debugging
    print(f"Saving certificate at: {output_path}")  # Debugging

    # Cek apakah file template sertifikat ada
    if not os.path.exists(template_path):
        print("Error: Template certificate file not found!")
        return None

    img = Image.open(template_path)
    img = img.resize((2500, 1768))  # Pastikan ukuran sertifikat sesuai 2500x1768 px
    draw = ImageDraw.Draw(img)

    try:
        font_course_id = ImageFont.truetype("Montserrat-SemiBold.ttf", 75)  # Font untuk Course ID
        font_name = ImageFont.truetype("Lucian_Schoenschrift.ttf", 120)  # Font untuk Nama
        font_date = ImageFont.truetype("Montserrat-Bold.ttf", 55)  # Font untuk Tanggal
        font_verification = ImageFont.truetype("Montserrat-Regular.ttf", 45)  # Font untuk Verifikasi
    except IOError:
        font_course_id = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_date = ImageFont.load_default()
        font_verification = ImageFont.load_default()

    # **Course ID** → Font Montserrat Semi Bold (Diletakkan di dalam kotak ungu)
    course_id_x, course_id_y = 460, 620  # Posisi sesuai gambar
    draw.rectangle([(course_id_x - 20, course_id_y - 15), (course_id_x + 300, course_id_y + 70)], fill="purple")  
    draw.text((course_id_x, course_id_y), f"{data['courseid']}", fill="white", font=font_course_id)

    # **Nama** → Font Lucian Schoenschrift (Diletakkan di tengah lebih besar)
    name_x, name_y = 700, 730
    name_color = (31, 142, 126)  # #1f8e7e
    draw.text((name_x, name_y), f"{data['name']}", fill=name_color, font=font_name)

    # **Format tanggal startdate dan enddate**
    formatted_startdate = format_date(data['startdate'])
    formatted_enddate = format_date(data['enddate'])

    # **Tanggal Pelaksanaan** → Font Montserrat Bold (Diletakkan di bawah nama)
    date_x, date_y = 720, 920
    draw.text((date_x, date_y), f"{formatted_startdate} - {formatted_enddate}", fill="black", font=font_date)

    # **Hitung masa berlaku sertifikat (3 tahun setelah enddate)**
    try:
        end_date_obj = datetime.strptime(data['enddate'], "%Y-%m-%d")  # Format input
        expiry_date = end_date_obj + timedelta(days=3*365)  # Tambah 3 tahun
        expiry_text = f"Berlaku hingga {expiry_date.strftime('%d %B %Y')}"
    except ValueError:
        expiry_text = "Berlaku hingga: - (format tanggal salah)"

    # Generate QR Code
    qr_data = json.dumps(data)
    qr_output = os.path.join(QR_FOLDER, f"{data['certificate_id']}.png")
    generate_qr_code(qr_data, qr_output)

    # **Tambahkan QR Code ke sertifikat (diletakkan di kanan bawah)**
    qr_img = Image.open(qr_output).resize((200, 200))  # Ukuran QR Code lebih besar
    qr_x, qr_y = 2100, 1400  # Posisi QR Code sesuai gambar
    img.paste(qr_img, (qr_x, qr_y))

    # **Tambahkan teks "Verifikasi Sertifikat" di atas QR Code**
    verification_x, verification_y = qr_x, qr_y - 50
    draw.text((verification_x, verification_y), "Verifikasi Sertifikat", fill="black", font=font_verification)

    # **Tambahkan teks "Berlaku hingga ..." di bawah QR Code**
    expiry_x, expiry_y = qr_x, qr_y + 220
    draw.text((expiry_x, expiry_y), expiry_text, fill="black", font=font_verification)

    img.save(output_path)
    return output_path

# Endpoint untuk membuat sertifikat
@certificate_bp.route("/generate_certificate", methods=["POST"])
def generate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    data['certificate_id'] = generate_md5_hash(data['name'] + data['coursename'])
    certificate_path = generate_certificate(data)

    if not certificate_path:
        return jsonify({"error": "Failed to generate certificate"}), 500

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