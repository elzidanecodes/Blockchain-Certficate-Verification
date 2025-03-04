from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import hashlib
import cv2
from pyzbar.pyzbar import decode
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
import sqlite3
import requests
import time
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
UPLOAD_FOLDER = './static/uploads'
VERIFIED_CERT_FOLDER = './static/verified_certificates'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VERIFIED_CERT_FOLDER, exist_ok=True)

INSTITUTION_NAME = "Politeknik Negeri Malang"  # Nama institusi yang akan dimasukkan ke dalam hash


# Load private key for decryption
def load_private_key():
    if os.path.isfile("private_key.pem"):
        with open("private_key.pem", "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    return None

private_key = load_private_key()
if private_key is None:
    raise Exception("Private key is not found!!")


# Function to read QR Code from uploaded certificate
def read_qr_code(image_path):
    image = cv2.imread(image_path)
    decoded_objects = decode(image)
    return decoded_objects[0].data.decode('utf-8') if decoded_objects else None


# Function to check if data exists in blockchain (mocked via SQLite)
def is_data_present(data_to_check):
    query = f"SELECT COUNT(*) FROM blocks WHERE encrypted_data = '{data_to_check}'"
    response = requests.post('http://localhost:5000/api/query', json={'query': query})
    result = response.json()
    return result[0][0] > 0 if result else False


# Function to decrypt QR data
def decrypt_data(encrypted_data_hex, private_key):
    try:
        encrypted_data = bytes.fromhex(encrypted_data_hex)
        decrypted_data = private_key.decrypt(
            encrypted_data,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        return decrypted_data.decode()
    except Exception as e:
        print("Decryption Error:", e)
        return None


# Function to retrieve the blockchain-stored hash
def get_current_hash(encrypted_data):
    query = f"SELECT current_hash FROM blocks WHERE encrypted_data = '{encrypted_data}'"
    response = requests.post('http://localhost:5000/api/query', json={'query': query})
    result = response.json()
    return result[0][0] if result else None


# Function to generate a more secure MD5 hash with institution and timestamp
def generate_md5_hash(data, institution_name):
    timestamp = str(int(time.time()))  # Generate current timestamp
    combined_data = data + institution_name + timestamp
    return hashlib.md5(combined_data.encode()).hexdigest()


# Function to add verified signature to certificate
def add_signature_to_certificate(certificate_path, signature_text, output_path):
    img = Image.open(certificate_path)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    text_position = (100, img.height - 100)
    draw.text(text_position, f"Signature: {signature_text}", fill="white", font=font)
    img.save(output_path)


# Endpoint to upload and verify certificate
@app.route('/verify_certificate', methods=['POST'])
def verify_certificate():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    encrypted_data = read_qr_code(file_path)
    if not encrypted_data:
        return jsonify({"error": "QR Code not found in certificate"}), 400

    if is_data_present(encrypted_data):
        decrypted_data = decrypt_data(encrypted_data, private_key)
        stored_hash = get_current_hash(encrypted_data)

        if decrypted_data:
            # Generate the verified signature
            verified_signature = generate_md5_hash(decrypted_data, INSTITUTION_NAME)

            # Add signature to the certificate
            output_cert_path = os.path.join(VERIFIED_CERT_FOLDER, f"verified_{file.filename}")
            add_signature_to_certificate(file_path, verified_signature, output_cert_path)

            return jsonify({
                "is_verified": True,
                "message": "Certificate is valid",
                "signature": verified_signature,
                "download_url": f"/download_certificate/{file.filename}"
            }), 200
        else:
            return jsonify({"is_verified": False, "message": "Decryption failed"}), 400
    else:
        return jsonify({"is_verified": False, "message": "Certificate is not valid"}), 400


@app.route("/download_certificate/<filename>", methods=["GET"])
def download_certificate(filename):
    file_path = os.path.join(VERIFIED_CERT_FOLDER, f"verified_{filename}")
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "Certificate not found"}), 404


if __name__ == '__main__':
    app.run(port=5050, debug=True)
