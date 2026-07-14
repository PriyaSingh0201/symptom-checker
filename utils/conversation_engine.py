import os
import json
import re
import logging
from utils.clinical_engine import FALLBACK_KNOWLEDGE, DEFAULT_CONDITION

logger = logging.getLogger(__name__)

def generate_next_question(patient_data: dict, conversation_history: list) -> dict:
    """
    Decides if we need to ask another follow-up question, or if we have enough info.
    Returns:
        dict: {
            "has_enough_info": bool,
            "next_question": str (or None/empty if has_enough_info is True)
        }
    """
    # Rule 1: Limit consultation to maximum of 5 questions
    # Each turn has a user response. We can count the number of assistant questions in history
    questions_asked = [msg["content"] for msg in conversation_history if msg["role"] == "assistant"]
    
    if len(questions_asked) >= 5:
        logger.info("Reached limit of 5 follow-up questions.")
        return {"has_enough_info": True, "next_question": ""}

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key:
        result = _generate_next_question_gemini(patient_data, conversation_history, len(questions_asked))
        if result:
            return result

    return _generate_next_question_fallback(patient_data, conversation_history, questions_asked)


def _generate_next_question_gemini(patient_data: dict, conversation_history: list, questions_count: int) -> dict or None:
    """Uses Gemini to decide if we need more info and generate the next single follow-up question."""
    try:
        import google.generativeai as genai
        
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Build history transcript
        history_str = ""
        for msg in conversation_history:
            role = "Patient" if msg["role"] == "user" else "AI Specialist"
            history_str += f"{role}: {msg['content']}\n"
            
        p_info = f"""
        Age: {patient_data.get('age')}
        Gender: {patient_data.get('gender')}
        Initial Symptoms: {patient_data.get('symptoms')}
        Duration: {patient_data.get('duration')}
        Pain Level: {patient_data.get('pain_level')}/10
        Temp: {patient_data.get('body_temperature')}°F/°C
        Blood Pressure: {patient_data.get('blood_pressure')}
        Conditions: {patient_data.get('medical_conditions')}
        Medications: {patient_data.get('medications')}
        Allergies: {patient_data.get('allergies')}
        """
        
        prompt = f"""You are a clinical decision-support assistant. You are conducting an interactive symptom consultation.
Your goal is to gather enough details to perform a differential diagnosis of the top 5 possible conditions.

Patient Details:
{p_info}

Conversation History:
{history_str if history_str else "No messages yet."}

You have asked {questions_count} questions so far (maximum allowed is 5).

Determine if you have enough information to form a high-confidence assessment (with top 5 differentials, specialist, etc.) or if you need to ask another single follow-up question.
Rule: Ask only ONE question at a time. The question must depend on previous answers. Do not ask unnecessary questions.

Respond ONLY with a valid JSON object in this exact format (no markdown, no other text):
{{
  "has_enough_info": <true or false>,
  "next_question": "<the next follow-up question, or empty if has_enough_info is true>"
}}
"""
        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        
        data = json.loads(raw)
        return {
            "has_enough_info": bool(data.get("has_enough_info", False)),
            "next_question": data.get("next_question", "").strip()
        }
    except Exception as e:
        logger.warning("Gemini next question failed: %s – falling back to rule-based.", e)
        return None


def _generate_next_question_fallback(patient_data: dict, conversation_history: list, questions_asked: list) -> dict:
    """Rule-based question checklist fallback based on the primary suspected condition."""
    symptoms = patient_data.get("symptoms", "").lower()
    conditions = patient_data.get("medical_conditions", "").lower()
    combined = f"{symptoms} {conditions}"
    
    # Identify the best matching condition profile
    scored = []
    for entry in FALLBACK_KNOWLEDGE:
        score = sum(1 for kw in entry["keywords"] if kw in combined)
        if score > 0:
            scored.append((score, entry))
            
    scored.sort(key=lambda x: x[0], reverse=True)
    
    matched_entry = scored[0][1] if scored else DEFAULT_CONDITION
    questions = matched_entry.get("questions", ["Are you experiencing any other symptoms?", "Do you have any known medical conditions?", "Is this the first time you are feeling this way?"])
    
    # Find the first question that hasn't been asked yet
    for q in questions:
        # Check fuzzy matching to see if similar question was asked
        already_asked = False
        for asked_q in questions_asked:
            if q.lower() in asked_q.lower() or asked_q.lower() in q.lower():
                already_asked = True
                break
        if not already_asked:
            return {"has_enough_info": False, "next_question": q}
            
    # All predefined questions asked
    return {"has_enough_info": True, "next_question": ""}
