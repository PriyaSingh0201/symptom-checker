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
    
    # Phase 2 Upgraded Patient Fields
    weight = db.Column(db.String(50), nullable=True)
    height = db.Column(db.String(50), nullable=True)
    pain_level = db.Column(db.Integer, nullable=True)
    allergies = db.Column(db.Text, default="")
    medications = db.Column(db.Text, default="")
    primary_symptom = db.Column(db.String(255), nullable=True)
    secondary_symptoms = db.Column(db.Text, default="")
    smoking_status = db.Column(db.String(50), nullable=True)
    alcohol_consumption = db.Column(db.String(50), nullable=True)
    body_temperature = db.Column(db.Float, nullable=True)
    blood_pressure = db.Column(db.String(50), nullable=True)
    pregnancy_status = db.Column(db.String(50), nullable=True)

    # ── AI output ─────────────────────────────────────────────────────────────
    possible_condition = db.Column(db.String(150), nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False)          # Mild | Moderate | Severe
    recommended_doctor = db.Column(db.String(100), nullable=False)
    health_advice = db.Column(db.Text, nullable=False)

    # Phase 2 Upgraded AI Output Fields
    confidence_score = db.Column(db.Float, nullable=True)
    top_conditions = db.Column(db.Text, nullable=True)           # JSON string
    evidence_sources = db.Column(db.Text, nullable=True)         # JSON string
    emergency_flag = db.Column(db.Boolean, default=False)
    consultation_id = db.Column(db.String(100), nullable=True)
    followup_responses = db.Column(db.Text, nullable=True)       # JSON string
    followup_questions = db.Column(db.Text, nullable=True)       # JSON string

    # ── Metadata ─────────────────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # ── Serialisation ─────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        import json
        
        # Helper to parse stored JSON or default to list/dict
        def safe_json_loads(data, default_val):
            if not data:
                return default_val
            try:
                return json.loads(data)
            except Exception:
                return default_val

        return {
            "id": self.id,
            "user_id": self.user_id,
            "symptoms": self.symptoms,
            "age": self.age,
            "gender": self.gender,
            "duration": self.duration,
            "medical_conditions": self.medical_conditions,
            
            # Upgraded Patient Info
            "weight": self.weight or "",
            "height": self.height or "",
            "pain_level": self.pain_level or 0,
            "allergies": self.allergies or "",
            "medications": self.medications or "",
            "primary_symptom": self.primary_symptom or "",
            "secondary_symptoms": self.secondary_symptoms or "",
            "smoking_status": self.smoking_status or "",
            "alcohol_consumption": self.alcohol_consumption or "",
            "body_temperature": self.body_temperature or 98.6,
            "blood_pressure": self.blood_pressure or "",
            "pregnancy_status": self.pregnancy_status or "",
            
            # AI outputs
            "possible_condition": self.possible_condition,
            "explanation": self.explanation,
            "severity": self.severity,
            "recommended_doctor": self.recommended_doctor,
            "health_advice": self.health_advice,
            
            # Upgraded AI Outputs
            "confidence_score": self.confidence_score or 0.0,
            "top_conditions": safe_json_loads(self.top_conditions, []),
            "evidence_sources": safe_json_loads(self.evidence_sources, []),
            "emergency_flag": bool(self.emergency_flag),
            "consultation_id": self.consultation_id or "",
            "followup_responses": safe_json_loads(self.followup_responses, {}),
            "followup_questions": safe_json_loads(self.followup_questions, []),
            
            # Metadata
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "created_date": self.created_at.strftime("%d %b %Y"),
            "created_time": self.created_at.strftime("%I:%M %p"),
        }

    def __repr__(self) -> str:
        return f"<Assessment {self.id} – {self.possible_condition}>"
