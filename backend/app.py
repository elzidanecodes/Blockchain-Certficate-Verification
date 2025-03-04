from flask import Flask, render_template
from routes.certificate import certificate_bp
from routes.verification import verification_bp

app = Flask(__name__)



@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
