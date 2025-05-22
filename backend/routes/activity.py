# backend/routes/activity.py
from flask import Blueprint, request, jsonify
from database.mongo import collection
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

    results = collection.find(query).sort("verification_result.verified_at", sort_dir).limit(50)

    data = []
    for doc in results:
        vr = doc.get("verification_result", {})
        data.append({
            "certificate_id": doc.get("certificate_id"),
            "verified_at": vr.get("verified_at"),
            "status": "Valid" if vr.get("valid") else "Invalid"
        })

    return jsonify(data)