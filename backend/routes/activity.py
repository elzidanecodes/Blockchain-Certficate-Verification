from flask import Blueprint, request, jsonify
from database.mongo import collection_cert, collection_verify_logs
from pymongo import DESCENDING, ASCENDING

activity_bp = Blueprint("activity", __name__)

@activity_bp.route("/api/activity", methods=["GET"])
def get_activity():
    search = request.args.get("search", "").lower()
    sort = request.args.get("sort", "desc")

    query = {}
    if search:
        query["certificate_id"] = {"$regex": search, "$options": "i"}

    sort_dir = DESCENDING if sort == "desc" else ASCENDING

    results = collection_verify_logs.find(query).sort("timestamp", sort_dir).limit(50)

    data = []
    for doc in results:
        data.append({
            "certificate_id": doc.get("certificate_id"),
            "verified_at": doc.get("timestamp"),
            "result": doc.get("result", "-"),
            "note": doc.get("note", "-"),
            "status": "Valid" if doc.get("valid") else "Invalid"
        })

    return jsonify(data)

# Total semua sertifikat terbit
@activity_bp.route("/api/total_terbit", methods=["GET"])
def total_sertifikat_terbit():
    total = collection_cert.count_documents({})
    return jsonify({"total": total})

# Total sertifikat yang sudah diverifikasi dan valid
@activity_bp.route("/api/total_terverifikasi", methods=["GET"])
def total_terverifikasi():
    total_valid = collection_verify_logs.count_documents({"valid": True})
    return jsonify({"total": total_valid})

# Total sertifikat belum diverifikasi sama sekali
@activity_bp.route("/api/total_belum_verifikasi", methods=["GET"])
def total_belum_verifikasi():
    # Ambil semua certificate_id yang sudah diverifikasi
    verified_ids = collection_verify_logs.distinct("certificate_id")
    # Hitung di cert_info yang belum diverifikasi
    total_unverified = collection_cert.count_documents({
        "certificate_id": {"$nin": verified_ids}
    })
    return jsonify({"total": total_unverified})
