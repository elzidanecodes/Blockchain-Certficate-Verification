from flask import Blueprint, request, jsonify, send_file
import os
import json
import qrcode
from PIL import Image, ImageDraw, ImageFont
import requests
from security import generate_md5_hash

certificate_bp = Blueprint("certificate", __name__)

CERTIFICATE_FOLDER = "static/generated_certificates/"
QR_FOLDER = "static/qr_codes/"
os.makedirs(CERTIFICATE_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

# Fungsi untuk generate QR Code dari data sertifikat
def generate_qr_code(data, output_file):
    qr = qrcode.make(data)
    qr.save(output_file)

# Fungsi untuk membuat sertifikat dengan QR Code
def generate_certificate(data):
    template_path = os.path.join(os.getcwd(), "static", "certificate_template.png") # Path template sertifikat
    output_path = os.path.join(CERTIFICATE_FOLDER, f"{data['certificate_id']}.png")

    img = Image.open(template_path)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    # Posisi teks dalam sertifikat
    draw.text((200, 300), f"{data['name']}", fill="black", font=font)
    draw.text((200, 400), f"Course: {data['coursename']}", fill="black", font=font)
    draw.text((200, 500), f"Institution: {data['institution']}", fill="black", font=font)
    draw.text((200, 600), f"Date: {data['startdate']} - {data['enddate']}", fill="black", font=font)

    # Generate QR Code
    qr_data = json.dumps(data)
    qr_output = os.path.join(QR_FOLDER, f"{data['certificate_id']}.png")
    generate_qr_code(qr_data, qr_output)

    # Tambahkan QR Code ke sertifikat
    qr_img = Image.open(qr_output).resize((150, 150))
    img.paste(qr_img, (950, 500))

    img.save(output_path)
    return output_path

# Endpoint untuk membuat sertifikat dan menyimpan ke blockchain
@certificate_bp.route("/generate_certificate", methods=["POST"])
def generate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    data['certificate_id'] = generate_md5_hash(data['name'] + data['coursename'])
    certificate_hash = generate_md5_hash(data['certificate_id'])

    # Simpan hash ke blockchain
    blockchain_response = requests.post(
        "http://127.0.0.1:5000/blockchain/add_certificate",
        json={"certificate_hash": certificate_hash}
    )

    if blockchain_response.status_code != 200:
        return jsonify({"error": "Failed to store certificate in blockchain"}), 500

    return jsonify({
        "message": "Certificate generated and stored in blockchain",
        "certificate_id": data['certificate_id'],
        "hash": certificate_hash,
        "download_url": f"/certificate/download/{data['certificate_id']}.png"
    }), 200



# Endpoint untuk mengunduh sertifikat yang telah dibuat
@certificate_bp.route("/download_certificate/<filename>", methods=["GET"])
def download_certificate(filename):
    file_path = os.path.join(CERTIFICATE_FOLDER, filename)
    print(f"Checking file path: {file_path}")  # Debugging
    if os.path.exists(file_path):
        print("Certificate found, sending file.")  # Debugging
        return send_file(file_path, as_attachment=True)
    print("Certificate not found!")  # Debugging
    return jsonify({"error": "Certificate not found"}), 404

