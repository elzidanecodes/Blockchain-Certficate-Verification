from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.activity import activity_bp
from routes.certificate import certificate_bp
from routes.blockchain import blockchain_bp
from routes.verification import verification_bp
from routes.frontend import frontend_bp
from crypto.rsa_utils import generate_rsa_keys

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="/")
CORS(app)

# Generate RSA key otomatis jika belum ada
generate_rsa_keys()

# Register Blueprints
app.register_blueprint(certificate_bp, url_prefix="/certificate")
app.register_blueprint(blockchain_bp, url_prefix="/blockchain")
app.register_blueprint(verification_bp, url_prefix="/verification")
app.register_blueprint(frontend_bp, url_prefix="/frontend")
app.register_blueprint(activity_bp) 

if __name__ == "__main__":
    app.run(debug=True)
