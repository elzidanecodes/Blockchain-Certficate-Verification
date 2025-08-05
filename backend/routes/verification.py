import zipfile
from flask import Blueprint, request, jsonify, send_file, after_this_request
from PIL import Image, ImageOps
import numpy as np
import os
import shutil
import tempfile
from zipfile import ZipFile
from PIL import Image 
import uuid
from flask import session
from celery_worker import run_verifikasi
from database.mongo import get_certificate_by_id, collection_verify_logs
from database.auth import get_fingerprint
from utils.verification_utils import process_single_certificate
from config import contract


verification_bp = Blueprint("verification", __name__)


@verification_bp.route("/verify_certificate", methods=["POST"])
def verify():
    expected_fingerprint = session.get("fingerprint")
    current_fingerprint = get_fingerprint()

    if expected_fingerprint != current_fingerprint:
        session.clear()
        return jsonify({"error": "Session mismatch"}), 401

    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        temp_path = os.path.join(tempfile.gettempdir(), file.filename)
        file.save(temp_path)

        result = process_single_certificate(
            file_path=temp_path,
            filename=file.filename,
            username=session.get("username", "admin")
        )

        # Hapus file sementara
        if os.path.exists(temp_path):
            os.remove(temp_path)

        # Jika error, respon sesuai status
        if result.get("status") not in ["success", "invalid"]:
            return
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@verification_bp.route("/verify_certificate_zip", methods=["POST"])
def verify_certificate_zip():
    expected_fingerprint = session.get("fingerprint")
    current_fingerprint = get_fingerprint()

    if expected_fingerprint != current_fingerprint:
        session.clear()
        return jsonify({"error": "Session mismatch"}), 401

    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    username = session.get("username", "admin")
    uploaded_zip = request.files['file']
    task_ids = []

    try:
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(uploaded_zip, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        for filename in os.listdir(temp_dir):
            print("🔍 Memproses file:", filename)
            if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            full_path = os.path.join(temp_dir, filename)
            npy_path = os.path.join(temp_dir, f"{filename}.npy")

            img = Image.open(full_path).convert("RGB")
            img_resize = img.resize((img.width // 2, img.height // 2))
            gray = ImageOps.grayscale(img_resize)
            img_np = np.array(gray).astype("uint8")
            np.save(npy_path, img_np)

            task = run_verifikasi.delay(npy_path, filename, username)
            task_ids.append({"filename": filename, "task_id": task.id})

        return jsonify({
            "message": "Verifikasi dikirim ke background",
            "tasks": task_ids
        }), 202

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



# Endpoint untuk API verifikasi sertifikat 
@verification_bp.route("/api/verify/<certificate_id>")
def api_verify_certificate(certificate_id):
    print("🔍 incoming certificate_id:", certificate_id)
    log = collection_verify_logs.find_one({
        "certificate_id": {"$regex": f"^{certificate_id}$", "$options": "i"}
    })
    if not log or not log.get("valid", False):
        return jsonify({"valid": False, "message": "Sertifikat belum diverifikasi"}), 404

    contract_address = log.get("contract_address") or contract.address

    return jsonify({
        "valid": True,
        "certificate_id": certificate_id,
        "name": log.get("name"),
        "student_id": log.get("student_id"),
        "department": log.get("department"),
        "no_sertifikat": log.get("no_sertifikat"),
        "test_date": log.get("test_date"),
        "hash": log.get("hash"),
        "ipfs_cid": log.get("ipfs_cid"),
        "ipfs_url": log.get("ipfs_url"),
        "verified_at": log.get("timestamp").strftime("%Y-%m-%d"),
        "note": log.get("note", "")
    })

@verification_bp.route("/download_zip", methods=["GET"])
def download_verified_zip():
    zip_path = session.get("last_verified_zip")
    if not zip_path or not os.path.exists(zip_path):
        return jsonify({"error": "File ZIP tidak ditemukan"}), 404

    @after_this_request
    def cleanup(response):
        try:
            os.remove(zip_path)
            shutil.rmtree(os.path.dirname(zip_path), ignore_errors=True)
        except Exception as e:
            print(f"❌ Gagal hapus sementara: {e}")
        return response

    return send_file(zip_path, as_attachment=True, download_name="hasil_verifikasi.zip")
    
@verification_bp.route("/get_verified_image/<certificate_id>", methods=["GET"])
def get_verified_image(certificate_id):
    
    
    contract_address = contract.address
    record = get_certificate_by_id(certificate_id, contract_address)

    if not record or "verification_result" not in record:
        return jsonify({"error": "Data tidak ditemukan"}), 404

    image_base64 = record["verification_result"].get("image_base64", "")
    return jsonify({"image_base64": image_base64})