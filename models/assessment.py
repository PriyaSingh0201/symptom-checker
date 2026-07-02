# models/assessment.py – Assessment database model
from datetime import datetime, timezone
from database import db


class Assessment(db.Model):
    """Stores a single symptom assessment for a user."""

    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # ── Patient input ─────────────────────────────────────────────────────────
    symptoms = db.Column(db.Text, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    medical_conditions = db.Column(db.Text, default="")

    # ── AI output ─────────────────────────────────────────────────────────────
    possible_condition = db.Column(db.String(150), nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False)          # Mild | Moderate | Severe
    recommended_doctor = db.Column(db.String(100), nullable=False)
    health_advice = db.Column(db.Text, nullable=False)

    # ── Metadata ─────────────────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # ── Serialisation ─────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "symptoms": self.symptoms,
            "age": self.age,
            "gender": self.gender,
            "duration": self.duration,
            "medical_conditions": self.medical_conditions,
            "possible_condition": self.possible_condition,
            "explanation": self.explanation,
            "severity": self.severity,
            "recommended_doctor": self.recommended_doctor,
            "health_advice": self.health_advice,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "created_date": self.created_at.strftime("%d %b %Y"),
            "created_time": self.created_at.strftime("%I:%M %p"),
        }

    def __repr__(self) -> str:
        return f"<Assessment {self.id} – {self.possible_condition}>"
