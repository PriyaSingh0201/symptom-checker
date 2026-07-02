# utils/jwt_helper.py – JWT token creation and route protection decorator
import os
from functools import wraps
from datetime import datetime, timezone, timedelta

import jwt
from flask import request, jsonify, current_app

# ── Helpers ───────────────────────────────────────────────────────────────────

def create_token(user_id: int, email: str) -> str:
    """Generate a signed JWT access token valid for 24 hours."""
    payload = {
        "user_id": user_id,
        "email": email,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token; raises jwt.exceptions on failure."""
    return jwt.decode(
        token,
        current_app.config["JWT_SECRET_KEY"],
        algorithms=["HS256"],
    )


# ── Decorator ────────────────────────────────────────────────────────────────

def token_required(f):
    """
    Route decorator that validates the JWT Bearer token.
    Injects *current_user* (User model instance) into the wrapped function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        from models.user import User  # local import to avoid circular deps

        token = None

        # Accept token from Authorization header or cookie
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
        elif "token" in request.cookies:
            token = request.cookies.get("token")

        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401

        try:
            data = decode_token(token)
            current_user = User.query.get(data["user_id"])
            if current_user is None:
                return jsonify({"error": "User not found"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired. Please login again."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token. Please login again."}), 401

        return f(current_user, *args, **kwargs)

    return decorated
