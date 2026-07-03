import os
import secrets
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session

from database import db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.history import history_bp
from routes.pdf import pdf_bp
from routes.profile import profile_bp
from routes.symptom import symptom_bp
from routes.chat import chat_bp


BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
UPLOAD_DIR = BASE_DIR / "uploads"
INSTANCE_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)


def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-key"),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "dev-jwt-secret"),
        SQLALCHEMY_DATABASE_URI=(
            lambda url: url.replace("postgres://", "postgresql://", 1)
            if url.startswith("postgres://")
            else url
        )(os.getenv("DATABASE_URL", f"sqlite:///{INSTANCE_DIR / 'database.db'}")),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=str(UPLOAD_DIR),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        JSON_SORT_KEYS=False,
        TEMPLATES_AUTO_RELOAD=True,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        from models.assessment import Assessment  # noqa: F401
        from models.user import User  # noqa: F401

        db.create_all()

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(pdf_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(symptom_bp)
    app.register_blueprint(chat_bp)

    @app.before_request
    def ensure_csrf_token():
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            if request.path.startswith("/static"):
                return None
            if request.path.startswith("/api/"):
                return None
            if request.path in {"/login", "/register"}:
                return None
            session.setdefault("csrf_token", secrets.token_hex(16))
            if request.headers.get("X-CSRF-Token") != session.get("csrf_token"):
                if request.form.get("csrf_token") != session.get("csrf_token"):
                    return jsonify({"error": "Invalid CSRF token."}), 403

    @app.after_request
    def add_security_headers(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.route("/")
    def index():
        return redirect("/login")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()}), 200

    @app.errorhandler(404)
    def page_not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        return render_template("errors/500.html"), 500

    @app.errorhandler(401)
    def unauthorized(_error):
        return render_template("errors/401.html"), 401

    return app


app = create_app()


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_ENV") != "production"
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=debug_mode)