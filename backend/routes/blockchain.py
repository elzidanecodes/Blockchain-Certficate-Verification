from flask import Blueprint, request, jsonify
from config import web3, contract

blockchain_bp = Blueprint("blockchain", __name__)

# Fungsi untuk menambahkan sertifikat ke blockchain
@blockchain_bp.route("/add_certificate", methods=["POST"])
def add_certificate():
    try:
        data = request.json
        certificate_hash = data.get("certificate_hash")

        if not certificate_hash:
            return jsonify({"error": "Certificate hash is required"}), 400

        sender_address = web3.eth.accounts[0]
        tx_hash = contract.functions.addCertificate(certificate_hash).transact({'from': sender_address, 'gas': 2000000})
        web3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            "message": "Certificate stored in blockchain",
            "tx_hash": web3.to_hex(tx_hash)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Fungsi untuk verifikasi sertifikat di blockchain
@blockchain_bp.route("/verify_certificate", methods=["POST"])
def verify_certificate():
    try:
        data = request.json
        certificate_hash = data.get("certificate_hash")

        if not certificate_hash:
            return jsonify({"error": "Certificate hash is required"}), 400

        # Cek apakah sertifikat ada di blockchain
        is_verified = contract.functions.verifyCertificate(certificate_hash).call()

        if is_verified:
            # Ambil detail sertifikat dari blockchain
            certificate_data = contract.functions.certificates(certificate_hash).call()
            owner_address = certificate_data[1]
            timestamp = certificate_data[2]

            return jsonify({
                "is_verified": True,
                "owner": owner_address,
                "timestamp": timestamp
            }), 200
        else:
            return jsonify({"is_verified": False, "message": "Certificate not found in blockchain"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
