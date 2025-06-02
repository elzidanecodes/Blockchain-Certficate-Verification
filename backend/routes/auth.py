from flask import Blueprint, request, jsonify
from database.mongo import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = db.users.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "username": user["username"],
        "role": user["role"],
        "email": user["email"]
    }), 200
