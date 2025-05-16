from flask import Flask, render_template
from routes.certificate import certificate_bp
from routes.blockchain import blockchain_bp
from routes.verification import verification_bp
from flask_cors import CORS
import os
from crypto.rsa_utils import generate_rsa_keys
from routes.frontend import frontend_bp



app = Flask(__name__)
CORS(app)

# Generate RSA key otomatis jika belum ada
generate_rsa_keys()

# Debugging untuk melihat working directory Flask
print(f"Current working directory in Flask: {os.getcwd()}")

# Register Blueprints
app.register_blueprint(certificate_bp, url_prefix="/certificate")
app.register_blueprint(blockchain_bp, url_prefix="/blockchain")
app.register_blueprint(verification_bp, url_prefix="/verification")
app.register_blueprint(frontend_bp, url_prefix="/frontend")

@app.route("/")
def index():
    return render_template("verify.html")

if __name__ == "__main__":
    app.run(debug=True)