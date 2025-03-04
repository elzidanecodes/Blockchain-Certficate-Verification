from flask import Flask, render_template
from routes.certificate import certificate_bp
from routes.blockchain import blockchain_bp
from routes.verification import verification_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(certificate_bp, url_prefix="/certificate")
app.register_blueprint(blockchain_bp, url_prefix="/blockchain")
app.register_blueprint(verification_bp, url_prefix="/verification")

@app.route("/")
def index():
    return render_template("generate.html")

if __name__ == "__main__":
    app.run(debug=True)
