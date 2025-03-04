from flask import Blueprint, request, jsonify
from config import contract

verification_bp = Blueprint("verification", __name__)

@verification_bp.route("/verify_document", methods=["POST"])
def verify_document():
    document_hash = request.json['document_hash']
    is_verified = contract.functions.verifyCertificate(document_hash).call()
    return jsonify({"is_verified": is_verified})
