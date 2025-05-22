from flask import Blueprint, request, jsonify
from config import web3, contract

blockchain_bp = Blueprint("blockchain", __name__)

@blockchain_bp.route("/add_certificate", methods=["POST"])
def add_certificate():
    try:
        data = request.json
        hash_md5 = data.get("hash_md5")

        if not hash_md5:
            return jsonify({"error": "hash_md5 is required"}), 400

        sender_address = web3.eth.accounts[0]

        # 🔹 Kirim transaksi ke Blockchain → kontrak akan generate ID CERT-001 dst
        tx_hash = contract.functions.addCertificate(hash_md5).transact({'from': sender_address, 'gas': 2000000})
        web3.eth.wait_for_transaction_receipt(tx_hash)
        
         # 🔹 Ambil certificate ID terakhir dari blockchain
        certificate_counter = contract.functions.certificateCounter().call()
        certificate_id = f"CERT-{certificate_counter:03d}"

        print(f"✅ Blockchain Certificate ID: {certificate_id}")

        return jsonify({
            "message": "Certificate stored in blockchain",
            "certificate_id": certificate_id,
            "tx_hash": web3.to_hex(tx_hash)
        }), 200

    except Exception as e:
        print(f"❌ Blockchain Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
def store_signature(signature: str) -> str:
    sender_address = web3.eth.accounts[0]
    tx_hash = contract.functions.addCertificate(signature).transact({'from': sender_address, 'gas': 2000000})
    print(f"📤 TX Hash: {tx_hash.hex()} - waiting confirmation...")
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    print(f"✅ Confirmed in block: {receipt.blockNumber}")
    
    certificate_counter = contract.functions.certificateCounter().call()
    certificate_id = f"CERT-{certificate_counter:03d}"
    return certificate_id

@blockchain_bp.route("/verify_certificate", methods=["POST"])
def verify_certificate():
    try:
        data = request.json
        certificate_id = data.get("certificate_id")

        if not certificate_id:
            return jsonify({"error": "certificate_id is required"}), 400

        # 🔍 Panggil smart contract untuk ambil data
        is_valid, returned_id, returned_hash = contract.functions.getCertificate(certificate_id).call()

        if not is_valid:
            return jsonify({"is_verified": False, "message": "Certificate not found in blockchain"}), 404

        return jsonify({
            "is_verified": True,
            "certificate_id": returned_id,
            "hash_md5": returned_hash
        }), 200

    except Exception as e:
        print(f"❌ Verification Error: {str(e)}")
        return jsonify({"error": str(e)}), 500