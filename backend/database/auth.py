from flask import Blueprint, request, jsonify, session
from database.mongo import db
import bcrypt
import hashlib

auth_bp = Blueprint("auth", __name__)

def get_fingerprint():
    user_agent = request.headers.get("User-Agent", "")
    ip = request.remote_addr or "0.0.0.0"
    return hashlib.sha256((ip + user_agent).encode()).hexdigest()

@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = db.users.find_one({"email": email})
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"error": "Invalid credentials"}), 401
    
    session["fingerprint"] = get_fingerprint()
    session.permanent = True
    session["username"] = user["username"]
    session["role"] = user["role"]
    session["email"] = user["email"]

    return jsonify({"message": "Login berhasil"}), 200


@auth_bp.route("/api/check_role", methods=["GET"])
def check_role():
    expected = session.get("fingerprint")
    current = get_fingerprint()

    if expected != current:
        session.clear()
        return jsonify({"error": "Session mismatch"}), 401

    role = session.get("role")
    username = session.get("username")
    if role:
        return jsonify({"role": role, "username": username}), 200
    return jsonify({"error": "Unauthorized"}), 401


@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logout berhasil"}), 200