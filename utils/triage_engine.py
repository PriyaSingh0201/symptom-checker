# utils/triage_engine.py – Phase 3 Smart Consultation & Triage Engine
import os
import json
import re
import logging
from utils.knowledge_base import retrieve_medical_evidence
from utils.emergency_detector import check_emergency

logger = logging.getLogger(__name__)

# ── Specialist mapping ────────────────────────────────────────────────────────
SPECIALIST_MAP = {
    "cardiac": "Cardiologist",
    "heart": "Cardiologist",
    "chest": "Cardiologist",
    "neuro": "Neurologist",
    "headache": "Neurologist",
    "migraine": "Neurologist",
    "stroke": "Neurologist",
    "skin": "Dermatologist",
    "rash": "Dermatologist",
    "eczema": "Dermatologist",
    "lung": "Pulmonologist",
    "asthma": "Pulmonologist",
    "breath": "Pulmonologist",
    "bone": "Orthopedic",
    "joint": "Orthopedic",
    "back pain": "Orthopedic",
    "ear": "ENT Specialist",
    "throat": "ENT Specialist",
    "nose": "ENT Specialist",
    "gynec": "Gynecologist",
    "period": "Gynecologist",
    "pregnancy": "Gynecologist",
    "stomach": "Gastroenterologist",
    "gastro": "Gastroenterologist",
    "liver": "Gastroenterologist",
    "eye": "Ophthalmologist",
    "vision": "Ophthalmologist",
    "mental": "Psychiatrist",
    "anxiety": "Psychiatrist",
    "depression": "Psychiatrist",
    "diabetes": "Endocrinologist",
    "thyroid": "Endocrinologist",
}

# ── Initial triage questions per symptom cluster ─────────────────────────────
TRIAGE_QUESTION_SETS = {
    "headache": [
        "When did the headache start?",
        "On a scale of 1–10, how severe is the pain?",
        "Is the pain on one side or the whole head?",
        "Do you have nausea, vomiting, or sensitivity to light?",
        "Have you taken any pain medication? Did it help?",
    ],
    "fever": [
        "When did the fever start?",
        "What is your current temperature reading?",
        "Do you have chills, sweating, or body aches?",
        "Have you traveled recently or been in contact with a sick person?",
        "Do you have any other symptoms like cough or sore throat?",
    ],
    "chest": [
        "When did the chest pain start?",
        "Does the pain radiate to your arm, jaw, or back?",
        "Are you experiencing shortness of breath or sweating?",
        "Is the pain constant or does it come and go?",
        "Do you have a history of heart disease or high blood pressure?",
    ],
    "stomach": [
        "Where exactly is the abdominal pain located?",
        "When did it start and how long has it lasted?",
        "Do you have nausea, vomiting, or diarrhea?",
        "Have you eaten anything unusual in the last 24 hours?",
        "Do you have a fever along with the stomach pain?",
    ],
    "cough": [
        "How long have you had the cough?",
        "Is the cough dry or are you producing phlegm?",
        "Do you have a fever or sore throat along with the cough?",
        "Are you experiencing shortness of breath or wheezing?",
        "Have you been exposed to dust, smoke, or allergens recently?",
    ],
    "default": [
        "When did these symptoms first start?",
        "On a scale of 1–10, how severe are your symptoms?",
        "Have you experienced these symptoms before?",
        "Are you currently taking any medications?",
        "Do you have any known medical conditions or allergies?",
    ],
}


def get_initial_question(symptoms: str) -> str:
    """Returns the first triage question based on primary symptom."""
    s = symptoms.lower()
    for key in TRIAGE_QUESTION_SETS:
        if key in s:
            return TRIAGE_QUESTION_SETS[key][0]
    return TRIAGE_QUESTION_SETS["default"][0]


def generate_next_question(patient_data: dict, conversation_history: list) -> dict:
    """
    Decides whether to ask another question or finalize the assessment.
    Returns: { "has_enough_info": bool, "next_question": str }
    """
    questions_asked = [m["content"] for m in conversation_history if m["role"] == "assistant"]

    # Max 6 questions before finalizing
    if len(questions_asked) >= 6:
        return {"has_enough_info": True, "next_question": ""}

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key:
        result = _gemini_next_question(patient_data, conversation_history, len(questions_asked))
        if result:
            return result

    return _fallback_next_question(patient_data, conversation_history, questions_asked)


def _gemini_next_question(patient_data: dict, conversation_history: list, q_count: int) -> dict | None:
    """Uses Gemini to generate the next contextual question."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
        model = genai.GenerativeModel("gemini-1.5-flash")

        history_str = "\n".join(
            f"{'Patient' if m['role'] == 'user' else 'Doctor'}: {m['content']}"
            for m in conversation_history
        )

        prompt = f"""You are a clinical triage AI conducting a medical consultation.

Patient Info:
- Age: {patient_data.get('age')}
- Gender: {patient_data.get('gender')}
- Initial Symptoms: {patient_data.get('symptoms')}
- Duration: {patient_data.get('duration')}
- Existing Conditions: {patient_data.get('medical_conditions', 'None')}
- Medications: {patient_data.get('medications', 'None')}

Conversation so far ({q_count} questions asked, max 6):
{history_str or 'No conversation yet.'}

Decide: do you have enough clinical information to generate a top-5 differential diagnosis?
If yes, set has_enough_info to true.
If no, ask ONE focused follow-up question that depends on previous answers.

Respond ONLY with valid JSON (no markdown):
{{"has_enough_info": <true|false>, "next_question": "<question or empty string>"}}"""

        raw = model.generate_content(prompt).text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        data = json.loads(raw)
        return {
            "has_enough_info": bool(data.get("has_enough_info", False)),
            "next_question": data.get("next_question", "").strip()
        }
    except Exception as e:
        logger.warning("Gemini next question failed: %s", e)
        return None


def _fallback_next_question(patient_data: dict, conversation_history: list, questions_asked: list) -> dict:
    """Rule-based fallback: picks next unanswered question from the relevant set."""
    symptoms = patient_data.get("symptoms", "").lower()
    q_set = TRIAGE_QUESTION_SETS["default"]
    for key in TRIAGE_QUESTION_SETS:
        if key in symptoms:
            q_set = TRIAGE_QUESTION_SETS[key]
            break

    for q in q_set:
        if not any(q.lower()[:20] in asked.lower() for asked in questions_asked):
            return {"has_enough_info": False, "next_question": q}

    return {"has_enough_info": True, "next_question": ""}


def run_triage_analysis(patient_data: dict, conversation_history: list) -> dict:
    """
    Final analysis after consultation is complete.
    Returns top-5 conditions with probability, severity, specialist, reasoning, evidence.
    """
    symptoms = patient_data.get("symptoms", "")
    primary = patient_data.get("primary_symptom") or symptoms.split(",")[0].strip()

    # Build Q&A context string
    qa_context = "\n".join(
        f"{'Patient' if m['role'] == 'user' else 'Doctor'}: {m['content']}"
        for m in conversation_history
    )

    # Emergency check first
    emergency_res = check_emergency(symptoms, patient_data.get("medical_conditions", ""))

    # Retrieve medical evidence
    evidence = retrieve_medical_evidence(
        primary_symptom=primary,
        secondary_symptoms=patient_data.get("secondary_symptoms", ""),
        suspected_condition=""
    )

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    result = None
    if api_key:
        result = _gemini_triage_analysis(patient_data, qa_context, evidence, emergency_res)

    if not result:
        result = _fallback_triage_analysis(patient_data, evidence, emergency_res)

    # Emergency override
    if emergency_res["emergency_flag"]:
        result["emergency_flag"] = True
        result["emergency_message"] = emergency_res["message"]
        result["severity"] = "Severe"
        result["recommended_specialist"] = "Emergency Medicine"
        result["specialist_reason"] = "Your symptoms indicate a life-threatening emergency requiring immediate care."
        for c in result.get("top5_conditions", []):
            c["severity"] = "Severe"
            c["home_care"] = ""

    result["evidence_sources"] = evidence
    result["emergency_flag"] = emergency_res["emergency_flag"]
    result["emergency_message"] = emergency_res.get("message", "")
    return result


def _gemini_triage_analysis(patient_data: dict, qa_context: str, evidence: list, emergency_res: dict) -> dict | None:
    """Gemini-powered top-5 differential diagnosis with full clinical reasoning."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
        model = genai.GenerativeModel("gemini-1.5-flash")

        ev_str = "\n".join(
            f"[{i+1}] {e['source']} — {e['title']}: {e['summary']}"
            for i, e in enumerate(evidence) if e.get("source") != "System"
        ) or "No external evidence retrieved."

        prompt = f"""You are a senior clinical AI performing a differential diagnosis after a full consultation.

Patient Profile:
- Age: {patient_data.get('age')} | Gender: {patient_data.get('gender')}
- Symptoms: {patient_data.get('symptoms')}
- Duration: {patient_data.get('duration')}
- Pain Level: {patient_data.get('pain_level', 5)}/10
- Temperature: {patient_data.get('body_temperature', 98.6)}°F
- Blood Pressure: {patient_data.get('blood_pressure', 'N/A')}
- Existing Conditions: {patient_data.get('medical_conditions', 'None')}
- Medications: {patient_data.get('medications', 'None')}
- Allergies: {patient_data.get('allergies', 'None')}
- Smoking: {patient_data.get('smoking_status', 'N/A')}
- Alcohol: {patient_data.get('alcohol_consumption', 'N/A')}

Consultation Q&A:
{qa_context or 'No Q&A recorded.'}

Retrieved Medical Evidence:
{ev_str}

Generate a comprehensive clinical assessment. Respond ONLY with valid JSON (no markdown):
{{
  "top5_conditions": [
    {{
      "condition": "<name>",
      "probability": <integer 0-100>,
      "severity": "<Mild|Moderate|Severe>",
      "matching_symptoms": "<comma-separated symptoms that match>",
      "missing_symptoms": "<symptoms typically expected but not reported>",
      "reasoning": "<2-3 sentence clinical reasoning grounded in evidence>",
      "home_care": "<bullet-pointed advice starting with •, only if Mild; else empty string>"
    }}
  ],
  "recommended_specialist": "<one specialist type>",
  "specialist_reason": "<one sentence why this specialist>",
  "confidence_score": <integer 0-100>,
  "summary": "<2-3 sentence overall clinical summary>",
  "followup_questions": ["<q1>", "<q2>", "<q3>"]
}}

Rules:
- List exactly 5 conditions ordered by probability (highest first)
- Specialist options: General Physician, Cardiologist, Neurologist, Dermatologist, Pulmonologist, Orthopedic, ENT Specialist, Gynecologist, Gastroenterologist, Ophthalmologist, Psychiatrist, Endocrinologist, Emergency Medicine
- home_care: only for Mild severity, else empty string
- Ground reasoning in the retrieved medical evidence where possible"""

        raw = model.generate_content(prompt).text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        data = json.loads(raw)

        if "top5_conditions" in data and len(data["top5_conditions"]) >= 3:
            # Ensure exactly 5
            while len(data["top5_conditions"]) < 5:
                data["top5_conditions"].append({
                    "condition": "General Malaise",
                    "probability": 10,
                    "severity": "Mild",
                    "matching_symptoms": "fatigue",
                    "missing_symptoms": "",
                    "reasoning": "Non-specific symptoms that do not fit a clear pattern.",
                    "home_care": "• Rest and stay hydrated.\n• Monitor symptoms."
                })
            data.setdefault("recommended_specialist", "General Physician")
            data.setdefault("specialist_reason", "A general physician can evaluate and refer appropriately.")
            data.setdefault("confidence_score", 70)
            data.setdefault("summary", "Assessment based on reported symptoms and consultation.")
            data.setdefault("followup_questions", [])
            # Map top condition to root fields
            top = data["top5_conditions"][0]
            data["possible_condition"] = top["condition"]
            data["explanation"] = top["reasoning"]
            data["severity"] = top["severity"]
            data["recommended_doctor"] = data["recommended_specialist"]
            data["health_advice"] = top.get("home_care") or "Please consult a healthcare professional."
            return data
        return None
    except Exception as e:
        logger.error("Gemini triage analysis failed: %s", e)
        return None


def _fallback_triage_analysis(patient_data: dict, evidence: list, emergency_res: dict) -> dict:
    """Rule-based fallback triage analysis producing top-5 conditions."""
    from utils.clinical_engine import FALLBACK_KNOWLEDGE, DEFAULT_CONDITION

    symptoms = patient_data.get("symptoms", "").lower()
    conditions = patient_data.get("medical_conditions", "").lower()
    combined = f"{symptoms} {conditions}"

    scored = []
    for entry in FALLBACK_KNOWLEDGE:
        score = sum(1 for kw in entry["keywords"] if kw in combined)
        if score > 0:
            scored.append((score, entry))
    scored.sort(key=lambda x: x[0], reverse=True)

    entries = [e for _, e in scored[:5]]
    while len(entries) < 5:
        for fb in FALLBACK_KNOWLEDGE:
            if not any(e["condition"] == fb["condition"] for e in entries):
                entries.append(fb)
                break
        else:
            entries.append(DEFAULT_CONDITION)

    top5 = []
    for i, entry in enumerate(entries):
        prob = max(85 - i * 12, 10)
        top5.append({
            "condition": entry["condition"],
            "probability": prob,
            "severity": entry["severity"],
            "matching_symptoms": ", ".join(kw for kw in entry["keywords"] if kw in combined) or "general symptoms",
            "missing_symptoms": "",
            "reasoning": entry["explanation"],
            "home_care": entry["advice"] if entry["severity"] == "Mild" else ""
        })

    # Determine specialist
    specialist = "General Physician"
    for kw, spec in SPECIALIST_MAP.items():
        if kw in combined:
            specialist = spec
            break

    top = top5[0]
    return {
        "top5_conditions": top5,
        "recommended_specialist": specialist,
        "specialist_reason": f"Based on your symptoms, a {specialist} is best equipped to evaluate and treat this condition.",
        "confidence_score": top5[0]["probability"],
        "summary": top["reasoning"],
        "followup_questions": [],
        "possible_condition": top["condition"],
        "explanation": top["reasoning"],
        "severity": top["severity"],
        "recommended_doctor": specialist,
        "health_advice": top.get("home_care") or "Please consult a healthcare professional.",
    }
