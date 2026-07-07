# routes/chat.py – AI Chat Assistant endpoint
from flask import Blueprint, request, jsonify
import json
from models.assessment import Assessment
from utils.jwt_helper import token_required
from utils.ai_engine import chat_followup
from utils.conversation_memory import (
    store_consultation, get_consultation, is_symptom_update, integrate_new_symptom
)

chat_bp = Blueprint("chat_assistant", __name__)

DISCLAIMER = (
    "\n\n⚠️ This AI assistant provides general health information only. "
    "It is not a medical diagnosis or a substitute for professional medical advice. "
    "Please consult a qualified healthcare professional."
)


@chat_bp.route("/api/assistant", methods=["POST"])
@token_required
def assistant(current_user):
    """
    POST /api/assistant
    Body: { message, assessment_id (optional) }
    Fetches the user's latest assessment as context and returns an AI answer.
    """
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Message cannot be empty."}), 400

    if len(message) > 500:
        return jsonify({"error": "Message too long. Please keep it under 500 characters."}), 400

    # 1. Check if it's a symptom update (conversation memory)
    active = get_consultation()
    if active and is_symptom_update(message):
        updated_active = integrate_new_symptom(message, active)
        
        record = Assessment.query.filter_by(
            id=updated_active["id"], user_id=current_user.id
        ).first()
        if record:
            from utils.clinical_engine import analyze_clinical_case
            result = analyze_clinical_case(updated_active)
            record.symptoms = updated_active["symptoms"]
            record.secondary_symptoms = updated_active["secondary_symptoms"]
            record.possible_condition = result["possible_condition"]
            record.explanation = result["explanation"]
            record.severity = result["severity"]
            record.recommended_doctor = result["recommended_doctor"]
            record.health_advice = result["health_advice"]
            record.confidence_score = result["confidence_score"]
            record.top_conditions = json.dumps(result["top_conditions"])
            record.evidence_sources = json.dumps(result["evidence_sources"])
            record.emergency_flag = result["emergency_flag"]
            record.followup_questions = json.dumps(result.get("followup_questions", []))
            db.session.commit()
            store_consultation(record.to_dict())

            return jsonify({
                "answer": f"I have updated your active consultation with your new symptom: '{message}'. Suspected condition is updated to: {result['possible_condition']}. Please check your dashboard for the detailed analysis." + DISCLAIMER,
                "has_context": True,
                "condition": result["possible_condition"],
                "severity": result["severity"],
                "doctor": result["recommended_doctor"],
                "is_emergency": result["emergency_flag"],
                "updated": True,
                "assessment": record.to_dict()
            }), 200

    # Resolve context: prefer explicit assessment_id, else use latest
    assessment_id = data.get("assessment_id")
    context = {}

    if assessment_id:
        record = Assessment.query.filter_by(
            id=assessment_id, user_id=current_user.id
        ).first()
        if record:
            context = record.to_dict()
    else:
        latest = (
            Assessment.query
            .filter_by(user_id=current_user.id)
            .order_by(Assessment.created_at.desc())
            .first()
        )
        if latest:
            context = latest.to_dict()

    try:
        answer = chat_followup(message, context)
    except Exception:
        answer = (
            "I'm sorry, I couldn't process your question right now. "
            "Please try again or consult a healthcare professional directly."
        )

    # Detect if answer contains emergency warning
    is_emergency = any(kw in answer for kw in ["🚨", "IMMEDIATE", "emergency", "call emergency"])
    
    return jsonify({
        "answer": answer + DISCLAIMER,
        "has_context": bool(context),
        "condition": context.get("possible_condition", ""),
        "severity": context.get("severity", ""),
        "doctor": context.get("recommended_doctor", ""),
        "is_emergency": is_emergency,
        "updated": False
    }), 200
