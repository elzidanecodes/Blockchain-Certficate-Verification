from flask import Flask, send_from_directory, session
from flask_cors import CORS
from flask_session import Session 
from config import SECRET_KEY
from routes.activity import activity_bp
from routes.certificate import certificate_bp
from routes.blockchain import blockchain_bp
from routes.verification import verification_bp
from database.auth import auth_bp
from crypto.rsa_utils import generate_rsa_keys
from datetime import timedelta
import os
from routes.ocr_async import ocr_async_bp

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")

# ======== Konfigurasi Session Server-side ========
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SESSION_FOLDER = os.path.join(BASE_DIR, "session")

app.secret_key = SECRET_KEY
app.permanent_session_lifetime = timedelta(hours=2)

app.config.update(
    SESSION_TYPE="filesystem",
    SESSION_FILE_DIR=SESSION_FOLDER,
    SESSION_PERMANENT=True,
    SESSION_USE_SIGNER=True,
    SESSION_COOKIE_NAME="session",
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="None"
)

if not os.path.exists(SESSION_FOLDER):
    os.makedirs(SESSION_FOLDER)


# Inisialisasi session server-side
Session(app)
# ============================================================

# Konfigurasi CORS
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "https://localhost:5173"}})

# sertifikat SSL
KEYS_PATH = os.path.join(os.path.dirname(BASE_DIR), "backend", "keys")
CERT_PATH = os.path.join(KEYS_PATH, "cert.pem")
KEY_PATH = os.path.join(KEYS_PATH, "key.pem")

# Generate RSA jika belum ada
generate_rsa_keys()

# Register blueprint
app.register_blueprint(certificate_bp, url_prefix="/certificate")
app.register_blueprint(blockchain_bp, url_prefix="/blockchain")
app.register_blueprint(verification_bp)
app.register_blueprint(activity_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(ocr_async_bp)

if __name__ == "__main__":
    app.run(ssl_context=(CERT_PATH, KEY_PATH))