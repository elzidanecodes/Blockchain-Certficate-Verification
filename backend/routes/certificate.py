import datetime
import json
import hashlib
import qrcode
from flask import Blueprint, request, jsonify
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from config import contract, web3
from database import save_to_sqlite
from security import encrypt_data

certificate_bp = Blueprint("certificate", __name__)

# Fungsi untuk hashing MD5
def generate_md5_hash(data):
    return hashlib.md5(data.encode()).hexdigest()

# Fungsi untuk membuat QR Code
def generate_qr_code(data, output_file):
    qr = qrcode.make(data)
    qr.save(output_file)

@certificate_bp.route("/add_block", methods=["POST"])
def add_block():
    try:
        data = {
            "certificate_id": request.form['courseid'],
            "name": request.form['name'],
            "email": request.form['email'],
            "phnumber": request.form['phnumber'],
            "coursename": request.form['coursename'],
            "instname": request.form['instname'],
            "startdate": request.form['startdate'],
            "enddate": request.form['enddate'],
            "tanggal_terbit": datetime.datetime.now().strftime("%Y-%m-%d")
        }

        encrypted_data = encrypt_data(data)
        document_hash = generate_md5_hash(encrypted_data)
        sender_address = web3.eth.accounts[0]
        tx_hash = contract.functions.addCertificate(document_hash).transact({'from': sender_address, 'gas': 2000000})
        web3.eth.wait_for_transaction_receipt(tx_hash)
        
        save_to_sqlite(data)
        qr_filename = f"static/qr_codes/qr_{document_hash}.png"
        generate_qr_code(document_hash, qr_filename)

        return jsonify({
            "qr_code": f"qr_{document_hash}.png",
            "tx_hash": web3.to_hex(tx_hash)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
