# utils/clinical_engine.py – AI Clinical Reasoning & Decision Support
import os
import json
import re
import logging
from utils.knowledge_base import retrieve_medical_evidence
from utils.emergency_detector import check_emergency
from utils.confidence_score import calculate_confidence

logger = logging.getLogger(__name__)

# Fallback Clinical Knowledge Base (Top Suspected Conditions)
FALLBACK_KNOWLEDGE = [
    {
        "keywords": ["fever", "high temperature", "chills", "sweating", "hot", "temperature", "shivering"],
        "condition": "Viral Fever",
        "explanation": "Viral fever is an elevated body temperature caused by a viral infection. It is typical for immune systems fighting rhinovirus or influenza, and usually self-resolves with rest.",
        "doctor": "General Medicine",
        "severity": "Moderate",
        "advice": "• Drink at least 8-10 glasses of water daily.\n• Get plenty of rest and sleep.\n• Sponge forehead with cool, damp cloth.\n• Monitor body temperature every 4 hours.",
        "warning": "Seek immediate help if temperature exceeds 103°F (39.4°C) or is accompanied by confusion.",
        "questions": [
            "Are you experiencing shivering or chills?",
            "Do you have body aches or joint pain?",
            "Is there a sore throat or runny nose?",
            "Have you traveled or been exposed to sick contacts recently?"
        ]
    },
    {
        "keywords": ["cough", "cold", "runny nose", "sneezing", "sore throat", "nasal congestion", "stuffy nose"],
        "condition": "Common Cold",
        "explanation": "The common cold is a viral upper respiratory infection affecting the nose and throat. It is usually self-limiting and clears within 7 to 10 days.",
        "doctor": "General Medicine",
        "severity": "Mild",
        "advice": "• Stay hydrated with warm teas or water.\n• Gargle warm salt water for throat irritation.\n• Use saline nasal drops for congestion.\n• Rest to support immune function.",
        "warning": "Consult a doctor if symptoms persist beyond 10 days or if breathing becomes labored.",
        "questions": [
            "Is the cough dry or productive (producing phlegm)?",
            "Do you have a mild headache or sinus pressure?",
            "Are you experiencing a loss of taste or smell?",
            "Do you have a low-grade fever?"
        ]
    },
    {
        "keywords": ["headache", "migraine", "head pain", "throbbing", "pulsating", "nausea", "light sensitivity"],
        "condition": "Migraine",
        "explanation": "Migraine is a neurological condition causing throbbing headache pain, typically on one side of the head, often accompanied by sensory sensitivities.",
        "doctor": "Neurology",
        "severity": "Moderate",
        "advice": "• Rest in a quiet, dark room.\n• Apply a cold compress to the forehead or neck.\n• Avoid bright screens and loud noises.\n• Stay hydrated.",
        "warning": "Seek emergency care if it is the 'worst headache of your life' or matches stroke indicators.",
        "questions": [
            "Is the pain throbbing/pulsating and on one side of your head?",
            "Are you sensitive to bright lights or loud sounds?",
            "Does physical activity make the headache worse?",
            "Do you see flashing lights or patterns (aura) before the pain?"
        ]
    },
    {
        "keywords": ["chest pain", "chest tightness", "palpitations", "heart", "shortness of breath", "sweating"],
        "condition": "Cardiac Concern",
        "explanation": "Chest discomfort or pressure coupled with shortness of breath can indicate a serious cardiovascular concern (angina or coronary insufficiency) requiring immediate assessment.",
        "doctor": "Cardiology",
        "severity": "Severe",
        "advice": "", # No home care advice for severe conditions
        "warning": "Call emergency services immediately if pain radiates to the arm, neck, or jaw, or is accompanied by cold sweats.",
        "questions": [
            "Does the chest pain feel like pressure, tightness, or squeezing?",
            "Does the pain radiate to your left arm, shoulder, neck, or jaw?",
            "Are you experiencing sudden cold sweats or lightheadedness?",
            "Does the pain worsen with physical exertion?"
        ]
    },
    {
        "keywords": ["stomach pain", "abdominal pain", "nausea", "vomiting", "diarrhea", "food poisoning", "cramps"],
        "condition": "Gastroenteritis (Food Poisoning)",
        "explanation": "Gastroenteritis is inflammation of the stomach and intestines, commonly caused by consuming contaminated food or water, leading to nausea and fluid loss.",
        "doctor": "Gastroenterology",
        "severity": "Moderate",
        "advice": "• Sip Oral Rehydration Solutions (ORS) frequently.\n• Eat bland foods (bananas, rice, applesauce, toast).\n• Avoid dairy, caffeine, and fatty foods.\n• Wash hands thoroughly.",
        "warning": "Seek medical help if you cannot keep fluids down for 24 hours or see blood in stool.",
        "questions": [
            "How many times have you vomited or had loose stools today?",
            "Are you able to keep clear liquids down?",
            "Have you eaten any questionable or restaurant food in the last 24 hours?",
            "Do you feel dizzy when standing up?"
        ]
    },
    {
        "keywords": ["acidity", "heartburn", "acid reflux", "burning stomach", "bloating", "indigestion"],
        "condition": "Acid Reflux / Gastritis",
        "explanation": "Acid reflux occurs when stomach acid flows back into the esophagus, causing burning irritation. Gastritis is inflammation of the stomach lining.",
        "doctor": "Gastroenterology",
        "severity": "Mild",
        "advice": "• Avoid spicy, greasy, or highly acidic foods.\n• Eat smaller, more frequent meals.\n• Do not lie down within 2-3 hours after eating.\n• Elevate your head during sleep.",
        "warning": "Consult a doctor if you experience difficulty swallowing or severe chest burning.",
        "questions": [
            "Do you get a burning feeling in your chest after eating?",
            "Does the burning get worse when you lie down or bend over?",
            "Do you experience a sour or bitter taste in your throat?",
            "Are you experiencing abdominal bloating or frequent burping?"
        ]
    },
    {
        "keywords": ["breathlessness", "wheezing", "asthma", "difficulty breathing", "chest tightness"],
        "condition": "Asthma / Bronchial Spasm",
        "explanation": "Asthma causes airways to swell, narrow, and produce extra mucus, causing wheezing and shortness of breath, often triggered by allergens.",
        "doctor": "Pulmonology",
        "severity": "Moderate",
        "advice": "• Stay calm and sit upright.\n• Avoid known allergens, dust, and smoke.\n• Use your rescue inhaler if prescribed.\n• Monitor breathing closely.",
        "warning": "Seek emergency care if inhaler fails to relieve breathlessness, or if lips turn blue.",
        "questions": [
            "Do you hear a high-pitched whistling or wheezing sound when breathing?",
            "Has this breathing issue occurred in response to dust, pollen, or exercise?",
            "Do you have a personal or family history of asthma or allergies?",
            "Do you have a persistent cough that worsens at night?"
        ]
    },
    {
        "keywords": ["high blood pressure", "hypertension", "bp", "dizziness", "blurred vision", "headache"],
        "condition": "Hypertension (High Blood Pressure)",
        "explanation": "Hypertension is persistently high arterial blood pressure. Often asymptomatic, severe elevations can cause headaches, dizziness, or vision changes.",
        "doctor": "Cardiology",
        "severity": "Moderate",
        "advice": "• Limit sodium (salt) intake.\n• Practice deep breathing and relaxation.\n• Monitor BP at home.\n• Avoid alcohol and stimulants.",
        "warning": "Seek urgent care if blood pressure exceeds 180/120 mmHg or causes severe headaches.",
        "questions": [
            "Have you measured your blood pressure today? What was the reading?",
            "Are you experiencing a severe headache, dizziness, or ringing ears?",
            "Do you have a family history of high blood pressure or heart disease?",
            "Are you currently taking any blood pressure medications?"
        ]
    },
    {
        "keywords": ["urinary infection", "burning urination", "uti", "cloudy urine", "frequent urination"],
        "condition": "Urinary Tract Infection (UTI)",
        "explanation": "A UTI is a bacterial infection of the urinary system. It causes mucosal irritation leading to painful, frequent, and urgent urination.",
        "doctor": "General Medicine",
        "severity": "Moderate",
        "advice": "• Drink plenty of water to flush out bacteria.\n• Avoid caffeine, alcohol, and sugary drinks.\n• Apply a warm heating pad to lower abdomen.\n• Do not hold urine.",
        "warning": "Seek treatment immediately if you experience fever, chills, or lower back/kidney pain.",
        "questions": [
            "Do you feel a sharp burning sensation when urinating?",
            "Do you feel a strong, sudden urge to urinate frequently?",
            "Is your urine cloudy, dark, or strong-smelling?",
            "Are you experiencing any pain in your lower back or side?"
        ]
    }
]

DEFAULT_CONDITION = {
    "condition": "General Malaise",
    "explanation": "Your symptoms are non-specific and do not match a single classic profile. This could indicate a minor viral infection, stress, or exhaustion.",
    "doctor": "General Medicine",
    "severity": "Mild",
    "advice": "• Get 8 hours of sleep.\n• Eat light, nutritious meals.\n• Stay hydrated with water and electrolyte solutions.\n• Avoid heavy physical work.",
    "warning": "Consult a physician if you develop new symptoms or if existing ones worsen.",
    "questions": [
        "Do you have a fever or chills?",
        "Are you experiencing body aches, joint stiffness, or fatigue?",
        "Have you been under excessive stress or lacking sleep recently?",
        "Are you experiencing any nausea, vomiting, or changes in digestion?"
    ]
}

def analyze_clinical_case(patient_data: dict) -> dict:
    """
    Runs the clinical symptom checking pipeline:
    Patient Data -> Emergency Detection -> Knowledge Base Retrieval -> AI Analysis -> Confidence Score -> Result.
    """
    symptoms = patient_data.get("symptoms", "")
    meds = patient_data.get("medications", "")
    allergies = patient_data.get("allergies", "")
    conditions = patient_data.get("medical_conditions", "")
    
    # 1. Run Emergency Detection
    emergency_res = check_emergency(symptoms, conditions)
    
    # 2. Extract primary term to retrieve evidence
    primary_symptom = patient_data.get("primary_symptom", "").strip()
    if not primary_symptom:
        primary_symptom = symptoms.split(",")[0].strip()
        
    # Query medical knowledge base (Live APIs + Curated catalog)
    evidence = retrieve_medical_evidence(
        primary_symptom=primary_symptom,
        secondary_symptoms=patient_data.get("secondary_symptoms", ""),
        suspected_condition=patient_data.get("possible_condition", "")
    )
    
    # 3. Choose engine: Gemini AI or Rule-Based Fallback
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    result = None
    if api_key:
        result = _run_gemini_clinical(patient_data, evidence, emergency_res)
        
    if not result:
        result = _run_fallback_clinical(patient_data, evidence, emergency_res)
        
    # 4. Overwrite/Verify Emergency Flags
    if emergency_res["emergency_flag"]:
        result["emergency_flag"] = True
        result["severity"] = "Severe"
        result["recommended_doctor"] = "Emergency Medicine"
        result["health_advice"] = (
            "🚨 IMMEDIATE MEDICAL ATTENTION RECOMMENDED.\n"
            "Your symptoms indicate a medical emergency. Do not wait for home care. "
            "Call emergency services (e.g. 911 or local emergency lines) or proceed "
            "immediately to the nearest emergency department."
        )
        if "top_conditions" in result:
            for cond in result["top_conditions"]:
                cond["severity"] = "Severe"
                cond["home_care_advice"] = ""
                
    # 5. Compute and blend Confidence Scores
    for idx, cond in enumerate(result.get("top_conditions", [])):
        ai_conf = cond.get("confidence", 70)
        final_conf = calculate_confidence(
            condition_name=cond["condition"],
            symptoms=symptoms,
            age=int(patient_data.get("age", 30)),
            existing_diseases=conditions,
            retrieved_evidence=evidence,
            ai_confidence=ai_conf
        )
        cond["confidence"] = final_conf
        
        # Populate root level response fields with the primary (top) condition
        if idx == 0:
            result["confidence_score"] = final_conf
            result["possible_condition"] = cond["condition"]
            result["explanation"] = cond["explanation"]
            if not emergency_res["emergency_flag"]:
                result["severity"] = cond["severity"]
                result["recommended_doctor"] = cond["recommended_department"]
                result["health_advice"] = cond.get("home_care_advice", "") or "Please consult a healthcare professional."
            
    # Include metadata and references
    result["evidence_sources"] = evidence
    result["emergency_flag"] = emergency_res["emergency_flag"]
    result["emergency_message"] = emergency_res["message"]
    
    # 6. Safety Disclaimer
    disclaimer = (
        "\n\n⚠ DISCLAIMER: This assessment is AI-generated and is NOT a medical diagnosis. "
        "Please consult a qualified doctor for professional medical advice."
    )
    result["health_advice"] = result["health_advice"].strip() + disclaimer
    
    return result

def _run_gemini_clinical(patient_data: dict, evidence: list, emergency_res: dict) -> dict or None:
    """Calls the Gemini LLM with structured clinical templates."""
    try:
        import google.generativeai as genai
        
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        p_info = f"""
        Age: {patient_data.get('age')}
        Gender: {patient_data.get('gender')}
        Weight: {patient_data.get('weight')}
        Height: {patient_data.get('height')}
        Pain Level: {patient_data.get('pain_level')}/10
        Duration: {patient_data.get('duration')}
        Primary Symptom: {patient_data.get('primary_symptom')}
        Secondary Symptoms: {patient_data.get('secondary_symptoms')}
        Allergies: {patient_data.get('allergies', 'None')}
        Current Medications: {patient_data.get('medications', 'None')}
        Pregnancy Status: {patient_data.get('pregnancy_status', 'N/A')}
        Smoking Status: {patient_data.get('smoking_status', 'N/A')}
        Alcohol Consumption: {patient_data.get('alcohol_consumption', 'N/A')}
        Body Temperature: {patient_data.get('body_temperature')}°F/°C
        Blood Pressure: {patient_data.get('blood_pressure')}
        Existing Diseases: {patient_data.get('medical_conditions', 'None')}
        """
        
        ev_str = ""
        for i, ev in enumerate(evidence):
            ev_str += f"[{i+1}] Source: {ev['source']} - {ev['title']}\nSnippet: {ev['summary']}\n\n"
            
        prompt = f"""You are a clinical decision-support assistant. Analyze the patient data and retrieved medical evidence to perform clinical reasoning.
        
Patient Information:
{p_info}

Retrieved Medical Evidence:
{ev_str if ev_str else "No evidence retrieved."}

Generate the assessment in JSON format. Do not return any markdown code blocks (such as ```json), introductory text, or explanatory footnotes.
The JSON must have this exact structure:
{{
  "top_conditions": [
    {{
      "condition": "<suspected condition name>",
      "confidence": <integer representing percentage, e.g. 85>,
      "supporting_symptoms": "<comma-separated list of patient symptoms supporting this>",
      "explanation": "<2-3 sentence clinical explanation grounding it in retrieved medical evidence>",
      "severity": "<Mild, Moderate, or Severe>",
      "recommended_department": "<exactly one medical specialist department>",
      "home_care_advice": "<3-4 bullet-pointed guidelines for home care, starting with •, only for Mild severity; otherwise empty string>",
      "safety_warning": "<immediate alert instructions if condition worsens>"
    }},
    {{
      "condition": "<second condition>",
      "confidence": <integer percentage>,
      "supporting_symptoms": "<symptoms>",
      "explanation": "<explanation>",
      "severity": "<Mild, Moderate, or Severe>",
      "recommended_department": "<department>",
      "home_care_advice": "",
      "safety_warning": "<warning>"
    }},
    {{
      "condition": "<third condition>",
      "confidence": <integer percentage>,
      "supporting_symptoms": "<symptoms>",
      "explanation": "<explanation>",
      "severity": "<Mild, Moderate, or Severe>",
      "recommended_department": "<department>",
      "home_care_advice": "",
      "safety_warning": "<warning>"
    }}
  ],
  "followup_questions": [
    "<clinical question 1>",
    "<clinical question 2>",
    "<clinical question 3>",
    "<clinical question 4>"
  ]
}}

Rules:
- Suspected conditions must be ordered by confidence score (highest first).
- Ground explanations in the retrieved medical evidence. Reference sources like MedlinePlus or openFDA.
- Recommended departments: General Medicine, Cardiology, Neurology, Orthopedics, Gastroenterology, Pulmonology, Gynecology, ENT, Dermatology, Ophthalmology, Psychiatry, Emergency Medicine.
- Home care advice: bullet-pointed, each line starting with •. Return empty string if condition is Moderate or Severe.
- Generate 3-5 clinical follow-up questions targeting potential differentials or symptom details.
"""
        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        
        # Parse JSON
        data = json.loads(raw)
        
        # Quick validation
        if "top_conditions" in data and len(data["top_conditions"]) >= 3:
            return data
        return None
    except Exception as e:
        logger.error("Gemini clinical engine failed: %s", e)
        return None

def _run_fallback_clinical(patient_data: dict, evidence: list, emergency_res: dict) -> dict:
    """Rule-based clinical decision fallback when AI fails or key is missing."""
    symptoms = patient_data.get("symptoms", "").lower()
    conditions = patient_data.get("medical_conditions", "").lower()
    combined = f"{symptoms} {conditions}"
    
    # Calculate match scores
    scored = []
    for entry in FALLBACK_KNOWLEDGE:
        score = sum(1 for kw in entry["keywords"] if kw in combined)
        if score > 0:
            scored.append((score, entry))
            
    # Sort descending
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # Pick top 3 or pad with default
    matched_entries = [item[1] for item in scored[:3]]
    while len(matched_entries) < 3:
        # Avoid duplicate defaults
        default_item = DEFAULT_CONDITION.copy()
        if not any(e["condition"] == default_item["condition"] for e in matched_entries):
            matched_entries.append(default_item)
        else:
            # Fall back to a randomized index from catalog if already exists
            for fallback in FALLBACK_KNOWLEDGE:
                if not any(e["condition"] == fallback["condition"] for e in matched_entries):
                    matched_entries.append(fallback)
                    break
            else:
                matched_entries.append(default_item)
                
    top_conditions = []
    followup_questions = []
    
    # Build results
    for idx, entry in enumerate(matched_entries):
        # Calculate dummy base confidence for the engine to refine
        base_confidence = 80 - (idx * 10)
        
        # Compile advice: only show if mild
        advice = entry["advice"] if entry["severity"] == "Mild" else ""
        
        top_conditions.append({
            "condition": entry["condition"],
            "confidence": base_confidence,
            "supporting_symptoms": ", ".join(kw for kw in entry["keywords"] if kw in combined) or "general symptoms",
            "explanation": entry["explanation"],
            "severity": entry["severity"],
            "recommended_department": entry["doctor"],
            "home_care_advice": advice,
            "safety_warning": entry["warning"]
        })
        
        # Populate questions from the primary condition
        if idx == 0:
            followup_questions = entry.get("questions", ["Do you have fever?", "Are you feeling nauseous?", "How long have you felt like this?"])
            
    return {
        "top_conditions": top_conditions,
        "followup_questions": followup_questions
    }
