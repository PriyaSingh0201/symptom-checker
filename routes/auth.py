# routes/auth.py – Registration, Login, Logout
import re
from flask import Blueprint, request, jsonify, render_template
from database import db
from models.user import User
from utils.jwt_helper import create_token

auth_bp = Blueprint("auth", __name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _validate_password(password: str) -> str | None:
    """Return an error string if the password is invalid, else None."""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password):
        return "Password must contain at least one special character."
    return None


def _validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))


# ── Routes ────────────────────────────────────────────────────────────────────

@auth_bp.route("/", methods=["GET"])
@auth_bp.route("/login", methods=["GET"])
def login_page():
    """Serve the login page."""
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET"])
def register_page():
    """Serve the registration page."""
    return render_template("register.html")


@auth_bp.route("/register", methods=["POST"])
@auth_bp.route("/api/register", methods=["POST"])
def register():
    """
    POST /api/register
    Body: { fullname, email, password, confirm_password }
    Returns: { message } on success or { error } on failure.
    """
    data = request.get_json(silent=True) or {}

    fullname = (data.get("fullname") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm = data.get("confirm_password") or ""

    # ── Validation ────────────────────────────────────────────────────────
    if not all([fullname, email, password, confirm]):
        return jsonify({"error": "All fields are required."}), 400

    if not _validate_email(email):
        return jsonify({"error": "Please enter a valid email address."}), 400

    pwd_error = _validate_password(password)
    if pwd_error:
        return jsonify({"error": pwd_error}), 400

    if password != confirm:
        return jsonify({"error": "Passwords do not match."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists."}), 409

    # ── Create user ───────────────────────────────────────────────────────
    user = User(fullname=fullname, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Account created successfully! Please login."}), 201


@auth_bp.route("/login", methods=["POST"])
@auth_bp.route("/api/login", methods=["POST"])
def login():
    """
    POST /api/login
    Body: { email, password }
    Returns: { token, user } on success or { error } on failure.
    """
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password. Please try again."}), 401

    token = create_token(user.id, user.email)

    return jsonify({
        "message": "Login successful!",
        "token": token,
        "user": {
            "id": user.id,
            "fullname": user.fullname,
            "email": user.email,
        },
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    """
    POST /api/logout
    JWT is stateless; logout is handled client-side by deleting the token.
    """
    return jsonify({"message": "Logged out successfully."}), 200
