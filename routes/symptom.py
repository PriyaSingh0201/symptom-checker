# routes/symptom.py – Symptom analysis endpoints
from flask import Blueprint, request, jsonify, render_template, session
import secrets
import json
from database import db
from models.assessment import Assessment
from utils.jwt_helper import token_required
from utils.clinical_engine import analyze_clinical_case
from utils.conversation_memory import (
    store_consultation, get_consultation, is_symptom_update, integrate_new_symptom
)
from utils.ai_engine import chat_followup

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
    Body: { primary_symptom, secondary_symptoms, age, gender, duration, medical_conditions, ... }
    Returns: Upgraded AI clinical assessment.
    """
    data = request.get_json(silent=True) or {}

    primary_symptom = (data.get("primary_symptom") or "").strip()
    sec_raw = data.get("secondary_symptoms") or []
    if isinstance(sec_raw, list):
        secondary_symptoms = ", ".join(sec_raw)
    else:
        secondary_symptoms = str(sec_raw).strip()

    symptoms = primary_symptom
    if secondary_symptoms:
        symptoms += f", {secondary_symptoms}"

    age_raw = data.get("age")
    gender = (data.get("gender") or "").strip()
    duration = (data.get("duration") or "").strip()
    conditions = (data.get("medical_conditions") or "").strip()

    # Upgraded inputs
    weight = (data.get("weight") or "").strip()
    height = (data.get("height") or "").strip()
    pain_level_raw = data.get("pain_level")
    allergies = (data.get("allergies") or "").strip()
    medications = (data.get("medications") or "").strip()
    smoking_status = (data.get("smoking_status") or "").strip()
    alcohol_consumption = (data.get("alcohol_consumption") or "").strip()
    temp_raw = data.get("body_temperature")
    blood_pressure = (data.get("blood_pressure") or "").strip()
    pregnancy_status = (data.get("pregnancy_status") or "").strip()

    # ── Validation ────────────────────────────────────────────────────────
    if not primary_symptom:
        return jsonify({"error": "Primary symptom is required."}), 400
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

    try:
        pain_level = int(pain_level_raw) if pain_level_raw else 5
        if not (1 <= pain_level <= 10):
            pain_level = 5
    except (ValueError, TypeError):
        pain_level = 5

    try:
        body_temperature = float(temp_raw) if temp_raw else 98.6
    except (ValueError, TypeError):
        body_temperature = 98.6

    # Generate Consultation ID
    consultation_id = secrets.token_hex(8)

    patient_data = {
        "symptoms": symptoms,
        "age": age,
        "gender": gender,
        "duration": duration,
        "medical_conditions": conditions,
        "weight": weight,
        "height": height,
        "pain_level": pain_level,
        "allergies": allergies,
        "medications": medications,
        "primary_symptom": primary_symptom,
        "secondary_symptoms": secondary_symptoms,
        "smoking_status": smoking_status,
        "alcohol_consumption": alcohol_consumption,
        "body_temperature": body_temperature,
        "blood_pressure": blood_pressure,
        "pregnancy_status": pregnancy_status if gender == "Female" else ""
    }

    # ── AI / Fallback Analysis ─────────────────────────────────────────────
    result = analyze_clinical_case(patient_data)

    # ── Save to database ───────────────────────────────────────────────────
    assessment = Assessment(
        user_id=current_user.id,
        symptoms=symptoms,
        age=age,
        gender=gender,
        duration=duration,
        medical_conditions=conditions,

        weight=weight,
        height=height,
        pain_level=pain_level,
        allergies=allergies,
        medications=medications,
        primary_symptom=primary_symptom,
        secondary_symptoms=secondary_symptoms,
        smoking_status=smoking_status,
        alcohol_consumption=alcohol_consumption,
        body_temperature=body_temperature,
        blood_pressure=blood_pressure,
        pregnancy_status=pregnancy_status if gender == "Female" else "",

        possible_condition=result["possible_condition"],
        explanation=result["explanation"],
        severity=result["severity"],
        recommended_doctor=result["recommended_doctor"],
        health_advice=result["health_advice"],

        confidence_score=result["confidence_score"],
        top_conditions=json.dumps(result["top_conditions"]),
        evidence_sources=json.dumps(result["evidence_sources"]),
        emergency_flag=result["emergency_flag"],
        consultation_id=consultation_id,
        followup_responses=json.dumps({}),
        followup_questions=json.dumps(result.get("followup_questions", []))
    )
    db.session.add(assessment)
    db.session.commit()

    # Store in memory
    store_consultation(assessment.to_dict())

    return jsonify({
        "message": "Analysis complete!",
        "assessment_id": assessment.id,
        **result,
        "matched_keywords": result.get("matched_keywords", [])
    }), 200


@symptom_bp.route("/api/followup", methods=["POST"])
@token_required
def followup(current_user):
    """
    POST /api/followup
    Updates assessment when follow-up answers are submitted.
    """
    data = request.get_json(silent=True) or {}
    answer = (data.get("answer") or "").strip()
    question = (data.get("question") or "").strip()
    assessment_id = data.get("assessment_id")

    if not answer or not question or not assessment_id:
        return jsonify({"error": "Missing answer, question, or assessment_id."}), 400

    assessment = Assessment.query.filter_by(
        id=assessment_id, user_id=current_user.id
    ).first()

    if not assessment:
        return jsonify({"error": "Assessment not found."}), 404

    # 1. Parse follow-up responses
    responses = {}
    if assessment.followup_responses:
        try:
            responses = json.loads(assessment.followup_responses)
        except Exception:
            pass
    responses[question] = answer

    # 2. If 'Yes', incorporate into secondary symptoms
    updated_secondary = assessment.secondary_symptoms or ""
    if answer.lower() in ("yes", "y", "yeah", "true"):
        clean_sym = question.replace("Do you have", "").replace("Are you experiencing", "").replace("?", "").strip()
        if clean_sym:
            if updated_secondary:
                updated_secondary += f", {clean_sym}"
            else:
                updated_secondary = clean_sym

    updated_symptoms = assessment.symptoms
    if updated_secondary and updated_secondary not in updated_symptoms:
        updated_symptoms += f", {updated_secondary}"

    # 3. Assemble and re-run clinical analysis
    patient_data = {
        "symptoms": updated_symptoms,
        "age": assessment.age,
        "gender": assessment.gender,
        "duration": assessment.duration,
        "medical_conditions": assessment.medical_conditions,
        "weight": assessment.weight,
        "height": assessment.height,
        "pain_level": assessment.pain_level,
        "allergies": assessment.allergies,
        "medications": assessment.medications,
        "primary_symptom": assessment.primary_symptom,
        "secondary_symptoms": updated_secondary,
        "smoking_status": assessment.smoking_status,
        "alcohol_consumption": assessment.alcohol_consumption,
        "body_temperature": assessment.body_temperature,
        "blood_pressure": assessment.blood_pressure,
        "pregnancy_status": assessment.pregnancy_status,
        "possible_condition": assessment.possible_condition
    }

    result = analyze_clinical_case(patient_data)

    # 4. Save updates
    assessment.symptoms = updated_symptoms
    assessment.secondary_symptoms = updated_secondary
    assessment.possible_condition = result["possible_condition"]
    assessment.explanation = result["explanation"]
    assessment.severity = result["severity"]
    assessment.recommended_doctor = result["recommended_doctor"]
    assessment.health_advice = result["health_advice"]
    assessment.confidence_score = result["confidence_score"]
    assessment.top_conditions = json.dumps(result["top_conditions"])
    assessment.evidence_sources = json.dumps(result["evidence_sources"])
    assessment.emergency_flag = result["emergency_flag"]
    assessment.followup_responses = json.dumps(responses)

    # Remove the answered question from list
    q_list = []
    if assessment.followup_questions:
        try:
            q_list = json.loads(assessment.followup_questions)
        except Exception:
            pass
    if question in q_list:
        q_list.remove(question)
    assessment.followup_questions = json.dumps(q_list)

    db.session.commit()
    store_consultation(assessment.to_dict())

    return jsonify({
        "message": "Assessment updated!",
        "assessment_id": assessment.id,
        **result
    }), 200


@symptom_bp.route("/api/chat", methods=["POST"])
@token_required
def chat(current_user):
    """
    POST /api/chat
    Updates current consultation or answers general follow-up questions.
    """
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    assessment_id = data.get("assessment_id")

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    # 1. Check if it's a symptom update (conversation memory)
    active = get_consultation()
    if active and is_symptom_update(question):
        # Update current consultation
        updated_active = integrate_new_symptom(question, active)
        
        # Save to database
        record = Assessment.query.filter_by(
            id=updated_active["id"], user_id=current_user.id
        ).first()
        if record:
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
                "answer": f"I have updated your active consultation with your new symptom details: '{question}'. Suspected condition updated to: {result['possible_condition']}.",
                "updated": True,
                "assessment": record.to_dict()
            }), 200

    # 2. General Follow-up Q&A
    context = {}
    if assessment_id:
        assessment = Assessment.query.filter_by(
            id=assessment_id, user_id=current_user.id
        ).first()
        if assessment:
            context = assessment.to_dict()

    answer = chat_followup(question, context)
    return jsonify({"answer": answer, "updated": False}), 200

