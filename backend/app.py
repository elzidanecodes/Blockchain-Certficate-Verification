from flask import Flask, render_template
from routes.certificate import certificate_bp
from routes.verification import verification_bp

app = Flask(__name__)

# Register blueprint routes
app.register_blueprint(certificate_bp)
app.register_blueprint(verification_bp)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
