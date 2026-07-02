# routes/chat.py – AI Chat Assistant endpoint
from flask import Blueprint, request, jsonify
from models.assessment import Assessment
from utils.jwt_helper import token_required
from utils.ai_engine import chat_followup

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
    }), 200
