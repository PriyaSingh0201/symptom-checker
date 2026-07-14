# routes/consultation.py – Phase 3 Smart Consultation & Triage Routes
from flask import Blueprint, request, jsonify, render_template, session
import secrets
import json
from datetime import datetime, timezone
from database import db
from models.assessment import Assessment
from models.user import User
from utils.jwt_helper import token_required
from utils.triage_engine import (
    get_initial_question, generate_next_question, run_triage_analysis
)
from utils.emergency_detector import check_emergency
from utils.conversation_memory import store_consultation

consultation_bp = Blueprint("consultation", __name__)

# ── Pages ─────────────────────────────────────────────────────────────────────

@consultation_bp.route("/consultation")
@token_required
def consultation_page(current_user):
    return render_template("consultation.html")


@consultation_bp.route("/timeline")
@token_required
def timeline_page(current_user):
    return render_template("timeline.html")


@consultation_bp.route("/appointment")
@token_required
def appointment_page(current_user):
    return render_template("appointment.html")


# ── API: Start a new consultation ─────────────────────────────────────────────

@consultation_bp.route("/api/consultation/start", methods=["POST"])
@token_required
def start_consultation(current_user):
    """
    POST /api/consultation/start
    Body: { symptoms, age, gender, duration, medical_conditions, ... }
    Creates a new consultation record and returns the first triage question.
    """
    data = request.get_json(silent=True) or {}

    symptoms = (data.get("symptoms") or data.get("primary_symptom") or "").strip()
    age_raw = data.get("age")
    gender = (data.get("gender") or "").strip()
    duration = (data.get("duration") or "").strip()
    conditions = (data.get("medical_conditions") or "").strip()
    medications = (data.get("medications") or "").strip()
    allergies = (data.get("allergies") or "").strip()

    if not symptoms:
        return jsonify({"error": "Please describe your symptoms."}), 400
    if not age_raw or not gender or not duration:
        return jsonify({"error": "Age, gender, and duration are required."}), 400

    try:
        age = int(age_raw)
        if not (1 <= age <= 120):
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"error": "Please enter a valid age (1–120)."}), 400

    # Emergency check immediately
    emergency_res = check_emergency(symptoms, conditions)
    if emergency_res["emergency_flag"]:
        return jsonify({
            "emergency": True,
            "emergency_message": emergency_res["message"],
            "message": "🚨 MEDICAL EMERGENCY DETECTED. Please seek immediate emergency medical care."
        }), 200

    # Build patient data
    patient_data = {
        "symptoms": symptoms,
        "primary_symptom": symptoms,
        "secondary_symptoms": "",
        "age": age,
        "gender": gender,
        "duration": duration,
        "medical_conditions": conditions,
        "medications": medications,
        "allergies": allergies,
        "pain_level": int(data.get("pain_level", 5)),
        "body_temperature": float(data.get("body_temperature", 98.6)),
        "blood_pressure": (data.get("blood_pressure") or "").strip(),
        "smoking_status": (data.get("smoking_status") or "").strip(),
        "alcohol_consumption": (data.get("alcohol_consumption") or "").strip(),
        "weight": (data.get("weight") or "").strip(),
        "height": (data.get("height") or "").strip(),
        "pregnancy_status": (data.get("pregnancy_status") or "") if gender == "Female" else "",
    }

    # First question
    first_question = get_initial_question(symptoms)
    conversation_history = [{"role": "assistant", "content": first_question, "timestamp": _now()}]
    follow_up_questions = [first_question]

    # Create assessment record (partial — will be completed on finalize)
    consultation_id = secrets.token_hex(8)
    assessment = Assessment(
        user_id=current_user.id,
        symptoms=symptoms,
        age=age,
        gender=gender,
        duration=duration,
        medical_conditions=conditions,
        medications=medications,
        allergies=allergies,
        primary_symptom=symptoms,
        secondary_symptoms="",
        pain_level=patient_data["pain_level"],
        body_temperature=patient_data["body_temperature"],
        blood_pressure=patient_data["blood_pressure"],
        smoking_status=patient_data["smoking_status"],
        alcohol_consumption=patient_data["alcohol_consumption"],
        weight=patient_data["weight"],
        height=patient_data["height"],
        pregnancy_status=patient_data["pregnancy_status"],
        # Placeholder AI fields (updated on finalize)
        possible_condition="Pending",
        explanation="Consultation in progress.",
        severity="Moderate",
        recommended_doctor="General Physician",
        health_advice="Consultation in progress.",
        consultation_id=consultation_id,
        conversation_history=json.dumps(conversation_history),
        follow_up_questions=json.dumps([first_question]),
        follow_up_answers=json.dumps({}),
        consultation_timestamp=datetime.now(timezone.utc),
    )
    assessment.follow_up_questions = json.dumps(follow_up_questions)
    assessment.followup_questions = json.dumps(follow_up_questions)
    assessment.conversation_history = json.dumps(conversation_history)
    assessment.follow_up_answers = json.dumps({})
    assessment.followup_responses = json.dumps({})
    db.session.add(assessment)
    db.session.commit()

    # Store patient_data in session for this consultation
    session[f"consult_{assessment.id}"] = patient_data

    return jsonify({
        "consultation_id": assessment.id,
        "question": first_question,
        "question_number": 1,
        "emergency": False,
    }), 200


# ── API: Reply to a consultation question ─────────────────────────────────────

@consultation_bp.route("/api/consultation/reply", methods=["POST"])
@token_required
def reply_consultation(current_user):
    """
    POST /api/consultation/reply
    Body: { consultation_id, answer }
    Appends answer, generates next question or finalizes.
    """
    data = request.get_json(silent=True) or {}
    consultation_id = data.get("consultation_id")
    answer = (data.get("answer") or "").strip()

    if not consultation_id or not answer:
        return jsonify({"error": "consultation_id and answer are required."}), 400

    assessment = Assessment.query.filter_by(
        id=consultation_id, user_id=current_user.id
    ).first()
    if not assessment:
        return jsonify({"error": "Consultation not found."}), 404

    # Load conversation history
    history = []
    if assessment.conversation_history:
        try:
            history = json.loads(assessment.conversation_history)
        except Exception:
            pass

    # Load follow-up answers
    answers = {}
    if assessment.follow_up_answers:
        try:
            answers = json.loads(assessment.follow_up_answers)
        except Exception:
            pass

    # Find the last question asked
    last_question = ""
    for msg in reversed(history):
        if msg["role"] == "assistant":
            last_question = msg["content"]
            break

    # Append user answer
    history.append({"role": "user", "content": answer, "timestamp": _now()})
    if last_question:
        answers[last_question] = answer
    questions_asked = [m["content"] for m in history if m["role"] == "assistant"]

    # Emergency check on answer
    emergency_res = check_emergency(answer, assessment.medical_conditions or "")
    if emergency_res["emergency_flag"]:
        assessment.conversation_history = json.dumps(history)
        assessment.follow_up_answers = json.dumps(answers)
        assessment.follow_up_questions = json.dumps(questions_asked)
        assessment.followup_questions = json.dumps(questions_asked)
        assessment.followup_responses = json.dumps(answers)
        assessment.emergency_flag = True
        db.session.commit()
        return jsonify({
            "emergency": True,
            "emergency_message": emergency_res["message"],
            "done": True,
        }), 200

    # Get patient data from session or reconstruct
    patient_data = session.get(f"consult_{consultation_id}") or _reconstruct_patient_data(assessment)

    # Decide next question or finalize
    decision = generate_next_question(patient_data, history)

    if decision["has_enough_info"]:
        # Save history and finalize
        assessment.conversation_history = json.dumps(history)
        assessment.follow_up_answers = json.dumps(answers)
        assessment.follow_up_questions = json.dumps(questions_asked)
        assessment.followup_questions = json.dumps(questions_asked)
        assessment.followup_responses = json.dumps(answers)
        db.session.commit()
        return jsonify({
            "done": True,
            "emergency": False,
            "consultation_id": consultation_id,
        }), 200
    else:
        next_q = decision["next_question"]
        history.append({"role": "assistant", "content": next_q, "timestamp": _now()})
        assessment.conversation_history = json.dumps(history)
        assessment.follow_up_answers = json.dumps(answers)
        assessment.follow_up_questions = json.dumps(questions_asked)
        assessment.followup_questions = json.dumps(questions_asked)
        assessment.followup_responses = json.dumps(answers)
        db.session.commit()

        questions_asked = [m for m in history if m["role"] == "assistant"]
        return jsonify({
            "done": False,
            "emergency": False,
            "question": next_q,
            "question_number": len(questions_asked),
        }), 200


# ── API: Finalize consultation and run triage analysis ────────────────────────

@consultation_bp.route("/api/consultation/finalize", methods=["POST"])
@token_required
def finalize_consultation(current_user):
    """
    POST /api/consultation/finalize
    Body: { consultation_id }
    Runs full triage analysis and saves results.
    """
    data = request.get_json(silent=True) or {}
    consultation_id = data.get("consultation_id")

    if not consultation_id:
        return jsonify({"error": "consultation_id is required."}), 400

    assessment = Assessment.query.filter_by(
        id=consultation_id, user_id=current_user.id
    ).first()
    if not assessment:
        return jsonify({"error": "Consultation not found."}), 404

    history = []
    if assessment.conversation_history:
        try:
            history = json.loads(assessment.conversation_history)
        except Exception:
            pass

    patient_data = session.get(f"consult_{consultation_id}") or _reconstruct_patient_data(assessment)

    # Run full triage analysis
    result = run_triage_analysis(patient_data, history)

    # Save all results
    assessment.possible_condition = result.get("possible_condition", "General Malaise")
    assessment.explanation = result.get("explanation", "")
    assessment.severity = result.get("severity", "Moderate")
    assessment.recommended_doctor = result.get("recommended_doctor", "General Physician")
    assessment.health_advice = result.get("health_advice", "")
    assessment.confidence_score = result.get("confidence_score", 0)
    assessment.emergency_flag = result.get("emergency_flag", False)
    assessment.top5_conditions = json.dumps(result.get("top5_conditions", []))
    assessment.recommended_specialist = result.get("recommended_specialist", "General Physician")
    assessment.medical_references = json.dumps(result.get("evidence_sources", []))
    assessment.top_conditions = json.dumps(result.get("top5_conditions", [])[:3])
    assessment.evidence_sources = json.dumps(result.get("evidence_sources", []))
    assessment.followup_questions = json.dumps(result.get("followup_questions", []))
    assessment.follow_up_questions = json.dumps(result.get("followup_questions", []))
    assessment.probability_scores = json.dumps({item.get("condition", "Unknown"): item.get("probability", 0) for item in result.get("top5_conditions", [])})
    assessment.consultation_timestamp = datetime.now(timezone.utc)

    db.session.commit()
    store_consultation(assessment.to_dict())

    return jsonify({
        "message": "Consultation complete!",
        "assessment_id": assessment.id,
        **result,
    }), 200


# ── API: Health Timeline ───────────────────────────────────────────────────────

@consultation_bp.route("/api/timeline", methods=["GET"])
@token_required
def get_timeline(current_user):
    """GET /api/timeline — Returns all consultations for the health timeline."""
    assessments = Assessment.query.filter_by(
        user_id=current_user.id
    ).order_by(Assessment.created_at.desc()).limit(50).all()

    timeline = []
    for a in assessments:
        timeline.append({
            "id": a.id,
            "date": a.created_at.strftime("%d %b %Y"),
            "time": a.created_at.strftime("%I:%M %p"),
            "condition": a.possible_condition,
            "severity": a.severity,
            "specialist": a.recommended_specialist or a.recommended_doctor,
            "symptoms": a.symptoms[:80] + "..." if a.symptoms and len(a.symptoms) > 80 else (a.symptoms or ""),
            "confidence": a.confidence_score or 0,
            "emergency": bool(a.emergency_flag),
            "consultation_id": a.consultation_id or "",
        })

    return jsonify({"timeline": timeline, "total": len(timeline)}), 200


# ── API: Book Appointment (placeholder) ───────────────────────────────────────

@consultation_bp.route("/api/appointment/book", methods=["POST"])
@token_required
def book_appointment(current_user):
    """POST /api/appointment/book — Placeholder appointment booking."""
    data = request.get_json(silent=True) or {}
    specialist = (data.get("specialist") or "General Physician").strip()
    date = (data.get("date") or "").strip()
    time_slot = (data.get("time") or "").strip()
    hospital = (data.get("hospital") or "Nearest Hospital").strip()

    if not date or not time_slot:
        return jsonify({"error": "Date and time are required."}), 400

    # Placeholder — in production, integrate with a booking API
    booking_ref = secrets.token_hex(4).upper()
    return jsonify({
        "success": True,
        "booking_ref": booking_ref,
        "specialist": specialist,
        "date": date,
        "time": time_slot,
        "hospital": hospital,
        "message": f"Appointment booked with {specialist} on {date} at {time_slot}. Reference: {booking_ref}",
    }), 200


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M")


def _reconstruct_patient_data(assessment: Assessment) -> dict:
    """Reconstruct patient_data dict from Assessment model when session is lost."""
    return {
        "symptoms": assessment.symptoms or "",
        "primary_symptom": assessment.primary_symptom or assessment.symptoms or "",
        "secondary_symptoms": assessment.secondary_symptoms or "",
        "age": assessment.age,
        "gender": assessment.gender,
        "duration": assessment.duration,
        "medical_conditions": assessment.medical_conditions or "",
        "medications": assessment.medications or "",
        "allergies": assessment.allergies or "",
        "pain_level": assessment.pain_level or 5,
        "body_temperature": assessment.body_temperature or 98.6,
        "blood_pressure": assessment.blood_pressure or "",
        "smoking_status": assessment.smoking_status or "",
        "alcohol_consumption": assessment.alcohol_consumption or "",
        "weight": assessment.weight or "",
        "height": assessment.height or "",
        "pregnancy_status": assessment.pregnancy_status or "",
    }
