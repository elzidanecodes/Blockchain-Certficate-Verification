from flask import Blueprint, request, jsonify, send_file
import os
import json
import cv2
from pyzbar.pyzbar import decode
from config import contract
from security import load_private_key, generate_md5_hash
from PIL import Image, ImageDraw, ImageFont

verification_bp = Blueprint("verification", __name__)

UPLOAD_FOLDER = "static/uploads/"
VERIFIED_CERT_FOLDER = "static/verified_certificates/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VERIFIED_CERT_FOLDER, exist_ok=True)

private_key = load_private_key()

# Fungsi untuk membaca QR Code dari gambar
def read_qr_code(image_path):
    image = cv2.imread(image_path)
    decoded_objects = decode(image)
    return decoded_objects[0].data.decode('utf-8') if decoded_objects else None

# Endpoint untuk verifikasi sertifikat
@verification_bp.route("/verify_certificate", methods=["POST"])
def verify_certificate():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    encrypted_data = read_qr_code(file_path)
    if not encrypted_data:
        return jsonify({"error": "QR Code not found in certificate"}), 400

    # Cek di blockchain apakah hash ini terdaftar
    is_verified = contract.functions.verifyCertificate(encrypted_data).call()

    if is_verified:
        stored_hash = generate_md5_hash(encrypted_data)

        # Tambahkan signature ke sertifikat
        output_cert_path = os.path.join(VERIFIED_CERT_FOLDER, f"verified_{file.filename}")
        add_signature_to_certificate(file_path, stored_hash, output_cert_path)

        return jsonify({
            "is_verified": True,
            "message": "Certificate is valid",
            "signature": stored_hash,
            "download_url": f"/verification/download_certificate/{file.filename}"
        }), 200
    else:
        return jsonify({"is_verified": False, "message": "Certificate is not valid"}), 400

# Endpoint untuk mengunduh sertifikat terverifikasi
@verification_bp.route("/download_certificate/<filename>", methods=["GET"])
def download_certificate(filename):
    file_path = os.path.join(VERIFIED_CERT_FOLDER, f"verified_{filename}")
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "Certificate not found"}), 404

# Fungsi untuk menambahkan tanda tangan digital pada sertifikat
def add_signature_to_certificate(certificate_path, signature_text, output_path):
    img = Image.open(certificate_path)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    draw.text((100, img.height - 100), f"Signature: {signature_text}", fill="white", font=font)
    img.save(output_path)
