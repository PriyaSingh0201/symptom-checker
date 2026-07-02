# models/user.py – User database model
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from database import db


class User(db.Model):
    """Represents a registered user in the system."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship: one user → many assessments
    assessments = db.relationship(
        "Assessment",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # ── Password helpers ──────────────────────────────────────────────────────
    def set_password(self, password: str) -> None:
        """Hash and store the password using Werkzeug's pbkdf2."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Return True if *password* matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    # ── Serialisation ─────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email": self.email,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "total_assessments": self.assessments.count(),
        }

    def __repr__(self) -> str:
        return f"<User {self.email}>"
