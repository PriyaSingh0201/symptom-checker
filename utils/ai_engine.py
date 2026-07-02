# utils/ai_engine.py – AI-powered symptom analysis
# Primary  : Google Gemini API (if GEMINI_API_KEY is set)
# Fallback : Comprehensive rule-based engine (20+ conditions)
# Never returns random results.

import os
import json
import re
import logging

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Rule-based Knowledge Base
# ─────────────────────────────────────────────────────────────────────────────

KNOWLEDGE_BASE = [
    {
        "keywords": ["fever", "high temperature", "chills", "sweating", "hot", "temperature"],
        "condition": "Viral Fever",
        "explanation": (
            "Viral fever is a common condition caused by a viral infection, "
            "leading to elevated body temperature. It is usually self-limiting "
            "and resolves within 3–7 days with proper rest and hydration."
        ),
        "doctor": "General Physician",
        "advice": [
            "Stay hydrated — drink at least 8–10 glasses of water daily.",
            "Rest adequately and avoid physical exertion.",
            "Take paracetamol (as directed) to manage fever.",
            "Use a cool damp cloth on the forehead for comfort.",
            "Monitor temperature every 4 hours and consult a doctor if fever exceeds 103°F.",
        ],
        "severity_rules": {
            "mild": ["mild fever", "low grade", "slight temperature"],
            "severe": ["very high", "above 103", "persistent fever", "more than 1 week"],
        },
        "default_severity": "Moderate",
    },
    {
        "keywords": ["headache", "migraine", "head pain", "throbbing", "pulsating", "nausea with headache", "light sensitivity"],
        "condition": "Migraine",
        "explanation": (
            "Migraine is a neurological condition characterized by intense, "
            "throbbing headaches often accompanied by nausea, vomiting, and "
            "sensitivity to light and sound. Attacks can last 4–72 hours."
        ),
        "doctor": "Neurologist",
        "advice": [
            "Rest in a quiet, dark room during an attack.",
            "Apply a cold or warm compress to your head or neck.",
            "Stay hydrated and avoid known triggers (bright lights, strong smells, caffeine).",
            "Keep a headache diary to identify and avoid triggers.",
            "Consult a neurologist for prescription migraine medications if frequent.",
        ],
        "severity_rules": {
            "mild": ["mild headache", "slight headache", "dull ache"],
            "severe": ["severe migraine", "worst headache", "vision changes", "more than 1 week"],
        },
        "default_severity": "Moderate",
    },
    {
        "keywords": ["cough", "cold", "runny nose", "sneezing", "sore throat", "nasal congestion", "stuffy nose"],
        "condition": "Common Cold",
        "explanation": (
            "The common cold is a viral upper respiratory infection. "
            "It typically presents with runny nose, sneezing, sore throat, "
            "and mild cough. Most colds resolve within 7–10 days."
        ),
        "doctor": "General Physician",
        "advice": [
            "Drink warm fluids like herbal tea, warm water with honey and lemon.",
            "Gargle with warm salt water to soothe sore throat.",
            "Use saline nasal drops or steam inhalation for congestion.",
            "Get adequate rest to allow your immune system to fight the infection.",
            "Avoid sharing utensils and wash hands frequently to prevent spread.",
        ],
        "severity_rules": {
            "mild": ["mild cold", "runny nose only", "slight cough"],
            "severe": ["high fever with cold", "difficulty breathing", "more than 1 week"],
        },
        "default_severity": "Mild",
    },
    {
        "keywords": ["chest pain", "chest tightness", "palpitations", "heart", "shortness of breath", "irregular heartbeat", "rapid heartbeat"],
        "condition": "Cardiac Concern",
        "explanation": (
            "Chest pain or tightness combined with shortness of breath and "
            "palpitations may indicate a cardiac issue. This requires prompt "
            "medical evaluation to rule out conditions like angina or arrhythmia."
        ),
        "doctor": "Cardiologist",
        "advice": [
            "SEEK IMMEDIATE MEDICAL ATTENTION if chest pain is severe or radiating to the arm/jaw.",
            "Avoid strenuous physical activity until evaluated by a doctor.",
            "Monitor and record when symptoms occur (at rest or during activity).",
            "Avoid smoking, alcohol, and high-sodium foods.",
            "Do not ignore chest symptoms — consult a cardiologist promptly.",
        ],
        "severity_rules": {
            "mild": ["mild palpitations", "occasional"],
            "severe": ["severe chest pain", "radiating pain", "cannot breathe"],
        },
        "default_severity": "Severe",
    },
    {
        "keywords": ["stomach pain", "abdominal pain", "nausea", "vomiting", "diarrhea", "food poisoning", "stomach cramps", "loose stools"],
        "condition": "Gastroenteritis (Food Poisoning)",
        "explanation": (
            "Gastroenteritis is inflammation of the stomach and intestines, "
            "commonly caused by contaminated food or water. Symptoms include "
            "nausea, vomiting, diarrhea, and abdominal cramps, usually lasting 1–3 days."
        ),
        "doctor": "Gastroenterologist",
        "advice": [
            "Stay hydrated — drink ORS (Oral Rehydration Solution) to replace lost electrolytes.",
            "Eat bland foods like plain rice, bananas, toast, and boiled vegetables (BRAT diet).",
            "Avoid dairy, fatty foods, caffeine, and alcohol until recovered.",
            "Wash hands thoroughly before eating and after using the toilet.",
            "Consult a doctor if symptoms persist beyond 3 days or blood appears in stools.",
        ],
        "severity_rules": {
            "mild": ["mild nausea", "once or twice"],
            "severe": ["severe vomiting", "blood in stool", "dehydration", "more than 1 week"],
        },
        "default_severity": "Moderate",
    },
    {
        "keywords": ["acidity", "heartburn", "acid reflux", "burning stomach", "burping", "bloating", "indigestion"],
        "condition": "Acid Reflux / Gastritis",
        "explanation": (
            "Acid reflux or gastritis occurs when stomach acid irritates the "
            "lining of the esophagus or stomach. It causes a burning sensation "
            "in the chest (heartburn), bloating, and sour taste in the mouth."
        ),
        "doctor": "Gastroenterologist",
        "advice": [
            "Avoid spicy, oily, and acidic foods (tomatoes, citrus, coffee).",
            "Eat smaller, more frequent meals instead of large portions.",
            "Do not lie down immediately after eating — wait at least 2–3 hours.",
            "Elevate the head of your bed by 6–8 inches if symptoms worsen at night.",
            "Antacids may provide temporary relief; consult a doctor for long-term management.",
        ],
        "severity_rules": {
            "mild": ["occasional heartburn", "mild bloating"],
            "severe": ["severe burning", "difficulty swallowing", "blood in vomit"],
        },
        "default_severity": "Mild",
    },
    {
        "keywords": ["joint pain", "knee pain", "back pain", "muscle pain", "bone pain", "arthritis", "stiffness", "swollen joint"],
        "condition": "Musculoskeletal Pain",
        "explanation": (
            "Musculoskeletal pain refers to pain affecting muscles, bones, "
            "ligaments, tendons, or joints. It can result from injury, "
            "overuse, arthritis, or inflammatory conditions."
        ),
        "doctor": "Orthopedic",
        "advice": [
            "Rest the affected area and avoid activities that worsen the pain.",
            "Apply ice packs (first 48 hours) then warm compress for relief.",
            "Gentle stretching and low-impact exercises can help over time.",
            "Maintain a healthy weight to reduce pressure on joints.",
            "Consult an orthopedic specialist if pain is persistent or worsening.",
        ],
        "severity_rules": {
            "mild": ["mild stiffness", "occasional pain"],
            "severe": ["cannot move", "severe swelling", "fracture", "more than 1 week"],
        },
        "default_severity": "Moderate",
    },
    {
        "keywords": ["skin rash", "itching", "hives", "eczema", "acne", "skin irritation", "redness", "dry skin", "psoriasis"],
        "condition": "Dermatological Condition",
        "explanation": (
            "Skin conditions like rashes, hives, and eczema are often caused "
            "by allergic reactions, infections, or immune responses. They can "
            "cause itching, redness, and discomfort."
        ),
        "doctor": "Dermatologist",
        "advice": [
            "Avoid scratching the affected area to prevent secondary infection.",
            "Use mild, fragrance-free soap and moisturizers.",
            "Apply cool compresses to reduce itching and inflammation.",
            "Identify and avoid potential allergens (certain foods, fabrics, detergents).",
            "Consult a dermatologist for prescription creams or antihistamines if needed.",
        ],
        "severity_rules": {
            "mild": ["mild rash", "small area", "no swelling"],
            "severe": ["spreading rash", "fever with rash", "blisters", "anaphylaxis"],
        },
        "default_severity": "Mild",
    },
    {
        "keywords": ["anxiety", "stress", "panic attack", "worry", "nervousness", "depression", "mood", "mental health", "insomnia", "sleep"],
        "condition": "Anxiety / Stress Disorder",
        "explanation": (
            "Anxiety and stress disorders involve excessive worry, fear, and "
            "tension that interfere with daily activities. Physical symptoms "
            "include rapid heartbeat, sweating, and difficulty sleeping."
        ),
        "doctor": "Psychiatrist",
        "advice": [
            "Practice deep breathing exercises and mindfulness meditation daily.",
            "Maintain a regular sleep schedule — aim for 7–9 hours per night.",
            "Engage in regular physical exercise, which naturally reduces stress hormones.",
            "Limit caffeine, alcohol, and screen time before bed.",
            "Consider speaking to a therapist or psychiatrist for professional support.",
        ],
        "severity_rules": {
            "mild": ["mild stress", "occasional worry"],
            "severe": ["panic attacks", "suicidal thoughts", "cannot function"],
        },
        "default_severity": "Moderate",
    },
    {
        "keywords": ["breathlessness", "wheezing", "asthma", "shortness of breath", "difficulty breathing", "chest tightness breathing"],
        "condition": "Asthma / Respiratory Issue",
        "explanation": (
            "Asthma is a chronic respiratory condition where airways become "
            "inflamed and narrow, causing wheezing, breathlessness, and chest "
            "tightness. Triggers include allergens, exercise, and cold air."
        ),
        "doctor": "Pulmonologist",
        "advice": [
            "Always carry your prescribed inhaler and use it as directed.",
            "Identify and avoid personal asthma triggers (dust, pollen, pets, smoke).",
            "Use an air purifier in your home and keep windows closed during high pollen seasons.",
            "Practice breathing exercises to strengthen respiratory muscles.",
            "Have regular check-ups with a pulmonologist to monitor lung function.",
        ],
        "severity_rules": {
            "mild": ["mild wheezing", "exercise-induced"],
            "severe": ["cannot breathe", "lips turning blue", "emergency"],
        },
        "default_severity": "Moderate",
    },
    {
        "keywords": ["high blood pressure", "hypertension", "bp", "dizziness", "blurred vision", "heavy head"],
        "condition": "Hypertension (High Blood Pressure)",
        "explanation": (
            "Hypertension is a condition where blood pressure is persistently "
            "elevated. Often called the 'silent killer', it can cause "
            "headaches, dizziness, and blurred vision, and leads to heart "
            "disease if unmanaged."
        ),
        "doctor": "Cardiologist",
        "advice": [
            "Reduce salt (sodium) intake to less than 2,300 mg per day.",
            "Exercise regularly — at least 30 minutes of moderate activity 5 days a week.",
            "Maintain a healthy weight and quit smoking if applicable.",
            "Monitor your blood pressure at home regularly.",
            "Take prescribed antihypertensive medication consistently.",
        ],
        "severity_rules": {
            "mild": ["slightly elevated", "borderline"],
            "severe": ["very high bp", "severe headache", "vision loss"],
        },
        "default_severity": "Moderate",
    },
    {
        "keywords": ["frequent urination", "excessive thirst", "fatigue", "weight loss unexplained", "blurred vision diabetes", "high sugar", "diabetes"],
        "condition": "Diabetes Risk",
        "explanation": (
            "Symptoms like excessive thirst, frequent urination, unexplained "
            "fatigue, and blurred vision may indicate high blood sugar levels "
            "associated with diabetes. Early detection and management are crucial."
        ),
        "doctor": "General Physician",
        "advice": [
            "Get a fasting blood glucose and HbA1c test done immediately.",
            "Reduce intake of sugar, refined carbohydrates, and sweetened beverages.",
            "Increase dietary fiber through vegetables, whole grains, and legumes.",
            "Exercise regularly — even 30-minute daily walks significantly improve insulin sensitivity.",
            "Consult an endocrinologist for proper diagnosis and management plan.",
        ],
        "severity_rules": {
            "mild": ["occasional thirst", "mild fatigue"],
            "severe": ["extreme thirst", "rapid weight loss", "confusion"],
        },
        "default_severity": "Moderate",
    },
    {
        "keywords": ["ear pain", "hearing loss", "tinnitus", "ringing ear", "earache", "ear infection", "throat pain", "tonsil"],
        "condition": "ENT (Ear, Nose & Throat) Issue",
        "explanation": (
            "Ear, nose, and throat conditions include ear infections, tinnitus, "
            "tonsillitis, and hearing problems. They can be caused by bacterial "
            "or viral infections, allergies, or structural issues."
        ),
        "doctor": "ENT Specialist",
        "advice": [
            "Do not insert any objects into your ear canal.",
            "Keep the ear dry; use earplugs during bathing if you have an infection.",
            "Gargle with warm salt water for throat pain relief.",
            "Avoid exposure to loud noises to protect hearing.",
            "Consult an ENT specialist promptly, especially for ear pain or hearing changes.",
        ],
        "severity_rules": {
            "mild": ["mild ear pain", "slight ringing"],
            "severe": ["sudden hearing loss", "severe pain", "discharge"],
        },
        "default_severity": "Mild",
    },
    {
        "keywords": ["menstrual pain", "irregular periods", "vaginal discharge", "pelvic pain", "pregnancy", "ovarian", "gynecology"],
        "condition": "Gynecological Issue",
        "explanation": (
            "Gynecological conditions affect the female reproductive system "
            "and include menstrual irregularities, pelvic pain, and hormonal "
            "imbalances. These require evaluation by a specialist."
        ),
        "doctor": "Gynecologist",
        "advice": [
            "Track your menstrual cycle using a period-tracking app.",
            "Use a heat pad for menstrual cramps; avoid cold beverages during periods.",
            "Maintain good personal hygiene to prevent infections.",
            "Eat iron-rich foods to compensate for blood loss during menstruation.",
            "Schedule regular gynecological check-ups (annually recommended).",
        ],
        "severity_rules": {
            "mild": ["mild cramps", "slight irregularity"],
            "severe": ["severe pelvic pain", "heavy bleeding", "suspected pregnancy complication"],
        },
        "default_severity": "Moderate",
    },
    {
        "keywords": ["eye pain", "blurred vision", "red eye", "watery eyes", "itchy eyes", "conjunctivitis", "eye infection"],
        "condition": "Ophthalmic Issue",
        "explanation": (
            "Eye conditions such as conjunctivitis, eye strain, or infections "
            "cause redness, pain, watering, or blurred vision. Prompt "
            "evaluation is important to prevent complications."
        ),
        "doctor": "Ophthalmologist",
        "advice": [
            "Avoid rubbing your eyes, which can worsen irritation and spread infection.",
            "If wearing contact lenses, switch to glasses until the condition resolves.",
            "Apply a clean, cold compress to reduce swelling and discomfort.",
            "Follow the 20-20-20 rule to reduce digital eye strain.",
            "Consult an ophthalmologist if vision changes or pain persists.",
        ],
        "severity_rules": {
            "mild": ["mild redness", "eye strain", "watering"],
            "severe": ["sudden vision loss", "severe pain", "trauma to eye"],
        },
        "default_severity": "Mild",
    },
    {
        "keywords": ["urinary infection", "burning urination", "uti", "frequent urination pain", "cloudy urine", "kidney pain"],
        "condition": "Urinary Tract Infection (UTI)",
        "explanation": (
            "A UTI is a bacterial infection affecting the urinary system. "
            "Common symptoms include a burning sensation during urination, "
            "frequent urgency, and cloudy or strong-smelling urine."
        ),
        "doctor": "General Physician",
        "advice": [
            "Drink at least 2–3 litres of water daily to flush bacteria from the urinary tract.",
            "Do not hold in urine — urinate as soon as you feel the urge.",
            "Urinate before and after sexual activity.",
            "Avoid irritants like perfumed soaps, bubble bath, and synthetic underwear.",
            "See a doctor promptly — UTIs require antibiotic treatment.",
        ],
        "severity_rules": {
            "mild": ["mild burning", "slight urgency"],
            "severe": ["blood in urine", "high fever with urinary symptoms", "back pain"],
        },
        "default_severity": "Moderate",
    },
    {
        "keywords": ["weakness", "fatigue", "tiredness", "lethargy", "no energy", "exhaustion", "anemia"],
        "condition": "Fatigue / Anemia",
        "explanation": (
            "Persistent fatigue and weakness can result from anemia, "
            "nutritional deficiencies (iron, B12), thyroid issues, or "
            "chronic conditions. A blood test can help identify the cause."
        ),
        "doctor": "General Physician",
        "advice": [
            "Get a complete blood count (CBC) test to check for anemia.",
            "Eat iron-rich foods: leafy greens, lentils, red meat, fortified cereals.",
            "Consume vitamin C-rich foods alongside iron-rich foods for better absorption.",
            "Maintain a consistent sleep schedule and avoid screen use before bed.",
            "Limit caffeine and alcohol intake, which can worsen fatigue.",
        ],
        "severity_rules": {
            "mild": ["mild tiredness", "end of day fatigue"],
            "severe": ["extreme weakness", "cannot get out of bed", "fainting"],
        },
        "default_severity": "Mild",
    },
]

# Default fallback when no keywords match
DEFAULT_RESULT = {
    "possible_condition": "General Malaise",
    "explanation": (
        "Your symptoms do not clearly match a specific condition in our database. "
        "This could indicate a minor viral illness, stress, or nutritional deficiency. "
        "A healthcare professional should evaluate your symptoms for an accurate diagnosis."
    ),
    "severity": "Mild",
    "recommended_doctor": "General Physician",
    "health_advice": [
        "Rest adequately and stay well hydrated.",
        "Eat balanced, nutritious meals.",
        "Monitor your symptoms over the next 24–48 hours.",
        "Avoid self-medication without medical advice.",
        "Consult a General Physician for a thorough examination.",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
#  Rule-Based Engine
# ─────────────────────────────────────────────────────────────────────────────

def _get_severity(entry: dict, text: str, duration: str, age: int) -> str:
    """Determine severity for a matched entry."""
    severity = entry["default_severity"]
    sev_rules = entry.get("severity_rules", {})
    if "more than 1 week" in duration.lower() or "1 week" in duration.lower():
        severity = "Severe"
    elif any(kw in text for kw in sev_rules.get("severe", [])):
        severity = "Severe"
    elif any(kw in text for kw in sev_rules.get("mild", [])):
        severity = "Mild"
    if age < 5 or age > 70:
        if severity == "Mild":
            severity = "Moderate"
        elif severity == "Moderate":
            severity = "Severe"
    return severity


def _rule_based_analysis(symptoms: str, age: int, gender: str,
                          duration: str, conditions: str) -> dict:
    """
    Match symptoms against the knowledge base using keyword scoring.
    Returns the best-matching condition + all other matched conditions.
    """
    text = f"{symptoms} {conditions}".lower()

    scored = []
    for entry in KNOWLEDGE_BASE:
        score = sum(1 for kw in entry["keywords"] if kw in text)
        if score > 0:
            scored.append((score, entry))

    if not scored:
        result = DEFAULT_RESULT.copy()
        result["health_advice"] = "\n".join(f"• {a}" for a in DEFAULT_RESULT["health_advice"])
        result["all_conditions"] = []
        return result

    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_match = scored[0]

    severity = _get_severity(best_match, text, duration, age)
    advice_text = "\n".join(f"• {a}" for a in best_match["advice"])

    # Build additional matched conditions (excluding the primary)
    all_conditions = []
    for score, entry in scored[1:]:
        sev = _get_severity(entry, text, duration, age)
        matched_kws = [kw for kw in entry["keywords"] if kw in text]
        all_conditions.append({
            "condition": entry["condition"],
            "severity": sev,
            "doctor": entry["doctor"],
            "matched_keywords": matched_kws,
            "explanation": entry["explanation"],
            "advice": "\n".join(f"• {a}" for a in entry["advice"]),
        })

    return {
        "possible_condition": best_match["condition"],
        "explanation": best_match["explanation"],
        "severity": severity,
        "recommended_doctor": best_match["doctor"],
        "health_advice": advice_text,
        "all_conditions": all_conditions,
        "matched_keywords": [kw for kw in best_match["keywords"] if kw in text],
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Gemini AI Engine
# ─────────────────────────────────────────────────────────────────────────────

def _gemini_analysis(symptoms: str, age: int, gender: str,
                     duration: str, conditions: str) -> dict | None:
    """
    Call Google Gemini API with a structured medical prompt.
    Returns parsed dict on success, None on failure.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        import google.generativeai as genai  # type: ignore

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""You are a medical AI assistant. Analyze the following patient symptoms and provide a structured health assessment.

Patient Information:
- Age: {age}
- Gender: {gender}
- Symptom Duration: {duration}
- Primary Symptoms: {symptoms}
- Existing Medical Conditions: {conditions if conditions else "None"}

Respond ONLY with a valid JSON object in this exact format (no markdown, no extra text):
{{
  "possible_condition": "<specific medical condition name>",
  "explanation": "<2-3 sentence explanation of the condition and why these symptoms suggest it>",
  "severity": "<exactly one of: Mild, Moderate, Severe>",
  "recommended_doctor": "<exactly one specialist type>",
  "health_advice": "<bullet-pointed advice, each point on a new line starting with •>"
}}

Rules:
- possible_condition: be specific (e.g., "Viral Fever", "Migraine", "Acid Reflux")
- severity: MUST be exactly "Mild", "Moderate", or "Severe"
- recommended_doctor: choose from General Physician, Cardiologist, Neurologist, Orthopedic, Dermatologist, Gynecologist, Pulmonologist, ENT Specialist, Gastroenterologist, Psychiatrist, Ophthalmologist, Endocrinologist
- health_advice: provide 5 practical, actionable points
- Always be medically responsible and recommend professional consultation"""

        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Strip markdown code fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        data = json.loads(raw)

        # Validate required fields
        required = ["possible_condition", "explanation", "severity",
                    "recommended_doctor", "health_advice"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing field: {field}")

        # Normalise severity
        sev = data["severity"].strip().capitalize()
        if sev not in ("Mild", "Moderate", "Severe"):
            sev = "Moderate"
        data["severity"] = sev
        data.setdefault("all_conditions", [])
        data.setdefault("matched_keywords", [])

        return data

    except Exception as exc:
        logger.warning("Gemini API failed: %s – falling back to rule-based engine.", exc)
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  Public Interface
# ─────────────────────────────────────────────────────────────────────────────

def analyze_symptoms(symptoms: str, age: int, gender: str,
                     duration: str, conditions: str) -> dict:
    """
    Analyze patient symptoms and return a structured assessment.

    Tries Gemini API first; if unavailable or erroring, falls back to
    the comprehensive rule-based knowledge engine.

    Returns:
        dict with keys:
            possible_condition, explanation, severity,
            recommended_doctor, health_advice
    """
    # 1. Try Gemini
    result = _gemini_analysis(symptoms, age, gender, duration, conditions)

    # 2. Fall back to rule-based
    if result is None:
        result = _rule_based_analysis(symptoms, age, gender, duration, conditions)

    # 3. Always append disclaimer
    disclaimer = (
        "\n\n⚠ DISCLAIMER: This assessment is AI-generated and is NOT a medical diagnosis. "
        "Please consult a qualified doctor for professional medical advice."
    )
    result["health_advice"] = result.get("health_advice", "") + disclaimer

    return result


# ─────────────────────────────────────────────────────────────────────────────
#  Chat Follow-up
# ─────────────────────────────────────────────────────────────────────────────

def chat_followup(question: str, assessment_context: dict) -> str:
    """
    Answer a follow-up question in the context of a previous assessment.
    Uses Gemini if available; otherwise returns an enhanced rule-based contextual answer.
    """
    condition = assessment_context.get("possible_condition", "your condition")
    doctor = assessment_context.get("recommended_doctor", "your doctor")
    severity = assessment_context.get("severity", "Moderate")
    explanation = assessment_context.get("explanation", "")

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key:
        try:
            import google.generativeai as genai  # type: ignore

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = f"""You are a helpful, empathetic AI health assistant. The patient was previously assessed with:
- Condition: {condition}
- Severity: {severity}
- Recommended Doctor: {doctor}
- Condition Details: {explanation}

The patient is now asking: "{question}"

Provide a concise, helpful, and medically responsible answer (2-4 sentences). 
Always recommend consulting a {doctor} for professional advice.
Never diagnose or prescribe medications directly.
Use empathetic language and be supportive."""

            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as exc:
            logger.warning("Gemini chat failed: %s", exc)

    # Enhanced rule-based chat fallback with better patterns
    q = question.lower()
    
    # Emergency detection
    if any(kw in q for kw in ["emergency", "urgent", "dying", "severe", "critical", "911", "ambulance"]):
        return f"🚨 If this is a medical emergency, PLEASE SEEK IMMEDIATE MEDICAL ATTENTION or call emergency services (911 in the US). Do not wait. Your health and safety are the priority!"
    
    # Medication questions
    if any(kw in q for kw in ["medicine", "medication", "drug", "paracetamol", "acetaminophen", "ibuprofen", "aspirin", "antibiotic"]):
        return (
            f"For {condition}, over-the-counter pain relievers like paracetamol or ibuprofen may help manage symptoms. "
            f"However, ALWAYS consult your {doctor} before taking any medication, as it depends on your medical history, "
            "age, and other medications you're taking. Never self-prescribe without professional guidance."
        )
    
    # When to see doctor
    if any(kw in q for kw in ["when", "doctor", "visit", "hospital", "appointment", "urgent", "see", "consult"]):
        urgency = "immediately" if severity == "Severe" else "within 2-3 days" if severity == "Moderate" else "within a week"
        return (
            f"Given the {severity.lower()} severity of your {condition}, you should visit a {doctor} {urgency}. "
            f"Seek immediate care if symptoms worsen or you experience difficulty breathing, severe pain, or loss of consciousness."
        )
    
    # Diet and food questions
    if any(kw in q for kw in ["food", "eat", "diet", "drink", "nutrition", "breakfast", "lunch", "dinner", "water"]):
        return (
            f"For {condition}, maintain a balanced diet with adequate hydration (8-10 glasses of water daily). "
            "Avoid processed, spicy, and fried foods. Focus on fresh fruits, vegetables, whole grains, and lean proteins. "
            f"Your {doctor} can provide a personalized dietary plan based on your specific condition."
        )
    
    # Exercise and activity questions
    if any(kw in q for kw in ["exercise", "workout", "activity", "rest", "sleep", "activity", "sport", "walk", "run"]):
        return (
            f"Rest is crucial while recovering from {condition}. Avoid strenuous physical activity until symptoms improve significantly. "
            "Once you feel better, start with light activities like short walks. "
            f"Always consult your {doctor} before resuming your normal exercise routine to ensure it's safe."
        )
    
    # Recovery timeline
    if any(kw in q for kw in ["how long", "recover", "timeline", "duration", "better", "improve", "days", "weeks"]):
        return (
            f"Recovery time for {condition} varies by individual. Most people recover within 1-2 weeks with proper self-care. "
            "However, if symptoms persist beyond this period or worsen, consult your doctor immediately. "
            "Consistent adherence to medical advice speeds up recovery."
        )
    
    # Contagious questions
    if any(kw in q for kw in ["contagious", "spread", "transmit", "others", "family", "contact"]):
        return (
            f"Whether {condition} is contagious depends on the specific cause. "
            "To be safe, practice good hygiene: wash hands frequently, avoid sharing utensils, and stay home if you have fever. "
            f"Your {doctor} can advise on specific precautions for your condition."
        )
    
    # Home remedies
    if any(kw in q for kw in ["home remedy", "natural", "remedy", "treatment", "heal", "at home"]):
        return (
            f"Common home care for {condition} includes: rest, hydration, and maintaining comfortable room temperature. "
            "Use warm or cold compresses as needed. However, home remedies alone may not be sufficient for all cases. "
            f"Consult your {doctor} for proper medical guidance, especially for moderate to severe conditions."
        )
    
    # Complications
    if any(kw in q for kw in ["complication", "dangerous", "serious", "worse", "get worse", "risk", "harm"]):
        return (
            f"Left untreated, {condition} can develop complications. Early intervention and proper care reduce these risks significantly. "
            f"Seek immediate medical attention if you experience new symptoms, persistent fever, severe pain, or breathing difficulties. "
            f"Trust your doctor's advice and follow treatment recommendations closely."
        )
    
    # Default helpful response
    return (
        f"Based on your assessment of {condition} (Severity: {severity}), I recommend consulting a {doctor} "
        "for detailed guidance on your specific question. They can provide personalized medical advice. "
        "In the meantime, follow general health practices: rest, hydration, and avoid stress. "
        "Always prioritize professional medical consultation for your healthcare decisions."
    )
