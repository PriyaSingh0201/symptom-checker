# utils/conversation_memory.py – Session-based memory for consultations
from flask import session
import re

SYMPTOM_UPDATE_PATTERNS = [
    r"\balso\b",
    r"\bhave\b",
    r"\bfeel\b",
    r"\bgot\b",
    r"\bdeveloped\b",
    r"\bnow\b",
    r"\bexperiencing\b",
    r"\bsuffering\b",
    r"\bstarted\b",
    r"\btoo\b",
    r"\bwith\b"
]

def store_consultation(assessment_dict: dict) -> None:
    """Stores the active consultation in the user session."""
    session["active_consultation"] = {
        "id": assessment_dict.get("id"),
        "consultation_id": assessment_dict.get("consultation_id"),
        "symptoms": assessment_dict.get("symptoms"),
        "primary_symptom": assessment_dict.get("primary_symptom"),
        "secondary_symptoms": assessment_dict.get("secondary_symptoms"),
        "age": assessment_dict.get("age"),
        "gender": assessment_dict.get("gender"),
        "duration": assessment_dict.get("duration"),
        "weight": assessment_dict.get("weight"),
        "height": assessment_dict.get("height"),
        "pain_level": assessment_dict.get("pain_level"),
        "allergies": assessment_dict.get("allergies"),
        "medications": assessment_dict.get("medications"),
        "smoking_status": assessment_dict.get("smoking_status"),
        "alcohol_consumption": assessment_dict.get("alcohol_consumption"),
        "body_temperature": assessment_dict.get("body_temperature"),
        "blood_pressure": assessment_dict.get("blood_pressure"),
        "pregnancy_status": assessment_dict.get("pregnancy_status"),
        "medical_conditions": assessment_dict.get("medical_conditions"),
        "conversation_history": assessment_dict.get("conversation_history", []),
        "follow_up_questions": assessment_dict.get("follow_up_questions", assessment_dict.get("followup_questions", [])),
        "follow_up_answers": assessment_dict.get("follow_up_answers", assessment_dict.get("followup_responses", {})),
        "top5_conditions": assessment_dict.get("top5_conditions", []),
        "probability_scores": assessment_dict.get("probability_scores", {}),
        "recommended_specialist": assessment_dict.get("recommended_specialist", ""),
        "medical_references": assessment_dict.get("medical_references", []),
        "followup_responses": assessment_dict.get("followup_responses", {}),
        "followup_questions": assessment_dict.get("followup_questions", [])
    }
    session.modified = True

def get_consultation() -> dict | None:
    """Retrieves the active consultation from the user session."""
    return session.get("active_consultation")

def clear_consultation() -> None:
    """Clears the active consultation from the session."""
    session.pop("active_consultation", None)

def is_symptom_update(message: str) -> bool:
    """
    Checks if a chat message looks like a symptom update or symptom addition.
    e.g. "I also have vomiting", "Now I feel dizzy too", "I developed a rash"
    """
    msg_lower = message.lower().strip()
    
    # Check if message is too long (diagnoses or questions, not symptom mentions)
    if len(msg_lower) > 100:
        return False
        
    # Check if user explicitly references symptoms
    symptom_indicators = [
        "pain", "fever", "cough", "vomit", "nausea", "headache", "dizzy", "rash",
        "throat", "ache", "chills", "breath", "blood", "diarrhea", "cramp", "itch",
        "swelling", "weak", "tired", "acidity", "heartburn", "symptom"
    ]
    
    has_symptom_word = any(ind in msg_lower for ind in symptom_indicators)
    has_update_pattern = any(re.search(pat, msg_lower) for pat in SYMPTOM_UPDATE_PATTERNS)
    
    return has_symptom_word and has_update_pattern

def integrate_new_symptom(message: str, active_consultation: dict) -> dict:
    """
    Integrates the new symptom described in the message into the active consultation.
    Returns the updated consultation dict.
    """
    # Clean up the sentence to isolate the symptom (e.g. "I also have vomiting" -> "vomiting")
    clean_msg = message.strip()
    
    # Append the new symptom to raw symptoms description
    curr_symptoms = active_consultation.get("symptoms", "")
    if clean_msg:
        if curr_symptoms:
            # Check if it's already there
            if clean_msg.lower() not in curr_symptoms.lower():
                active_consultation["symptoms"] = f"{curr_symptoms}, {clean_msg}"
        else:
            active_consultation["symptoms"] = clean_msg
            
        # Also append to secondary symptoms
        curr_sec = active_consultation.get("secondary_symptoms", "")
        if curr_sec:
            active_consultation["secondary_symptoms"] = f"{curr_sec}, {clean_msg}"
        else:
            active_consultation["secondary_symptoms"] = clean_msg
            
    return active_consultation
