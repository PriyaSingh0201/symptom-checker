# routes/symptom.py – Symptom analysis endpoints
from flask import Blueprint, request, jsonify, render_template
from database import db
from models.assessment import Assessment
from utils.jwt_helper import token_required
from utils.ai_engine import analyze_symptoms, chat_followup

symptom_bp = Blueprint("symptom", __name__)


@symptom_bp.route("/assessment")
@token_required
def assessment_page(current_user):
    """Serve the symptom checker page."""
    return render_template("assessment.html")


@symptom_bp.route("/api/analyze", methods=["POST"])
@token_required
def analyze(current_user):
    """
    POST /api/analyze
    Headers: Authorization: Bearer <token>
    Body: { symptoms, age, gender, duration, medical_conditions }
    Returns: AI assessment result + saved assessment ID.
    """
    data = request.get_json(silent=True) or {}

    symptoms = (data.get("symptoms") or "").strip()
    age_raw = data.get("age")
    gender = (data.get("gender") or "").strip()
    duration = (data.get("duration") or "").strip()
    conditions = (data.get("medical_conditions") or "").strip()

    # ── Validation ────────────────────────────────────────────────────────
    if not symptoms:
        return jsonify({"error": "Please describe your symptoms."}), 400
    if not age_raw:
        return jsonify({"error": "Age is required."}), 400
    if not gender:
        return jsonify({"error": "Gender is required."}), 400
    if not duration:
        return jsonify({"error": "Symptom duration is required."}), 400

    try:
        age = int(age_raw)
        if not (1 <= age <= 120):
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Please enter a valid age (1–120)."}), 400

    # ── AI Analysis ────────────────────────────────────────────────────────
    result = analyze_symptoms(symptoms, age, gender, duration, conditions)

    # ── Save to database ───────────────────────────────────────────────────
    assessment = Assessment(
        user_id=current_user.id,
        symptoms=symptoms,
        age=age,
        gender=gender,
        duration=duration,
        medical_conditions=conditions,
        possible_condition=result["possible_condition"],
        explanation=result["explanation"],
        severity=result["severity"],
        recommended_doctor=result["recommended_doctor"],
        health_advice=result["health_advice"],
    )
    db.session.add(assessment)
    db.session.commit()

    return jsonify({
        "message": "Analysis complete!",
        "assessment_id": assessment.id,
        **result,
        "all_conditions": result.get("all_conditions", []),
        "matched_keywords": result.get("matched_keywords", []),
    }), 200


@symptom_bp.route("/api/chat", methods=["POST"])
@token_required
def chat(current_user):
    """
    POST /api/chat
    Body: { question, assessment_id }
    Returns: { answer } based on the referenced assessment context.
    """
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    assessment_id = data.get("assessment_id")

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    context = {}
    if assessment_id:
        assessment = Assessment.query.filter_by(
            id=assessment_id, user_id=current_user.id
        ).first()
        if assessment:
            context = assessment.to_dict()

    answer = chat_followup(question, context)
    return jsonify({"answer": answer}), 200
