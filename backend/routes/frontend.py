from flask import Blueprint, request, render_template

frontend_bp = Blueprint("frontend", __name__)

@frontend_bp.route("/verify", methods=["GET"])
def verify_page():
    certificate_id = request.args.get("certificate_id", "")
    return render_template("verify.html", certificate_id=certificate_id)
