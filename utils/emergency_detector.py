# utils/emergency_detector.py – Scans for life-threatening medical conditions
import re

EMERGENCY_CRITERIA = [
    {
        "name": "Chest Pain + Sweating (Potential Cardiac Event)",
        "keywords": [r"chest\s*(pain|tightness|pressure|squeeze|ache)"],
        "co_keywords": [r"(sweat|diaphoresis|cold\s*sweat|perspir)"],
        "message": "Chest pain combined with sweating is a critical indicator of a potential cardiac emergency (such as a heart attack)."
    },
    {
        "name": "Severe Difficulty Breathing (Respiratory Distress)",
        "keywords": [
            r"(difficulty|unable\s*to|struggling\s*to)\s*breath", 
            r"shortness\s*of\s*breath", 
            r"severe\s*breathless", 
            r"gasping\s*for\s*air",
            r"suffocat",
            r"dyspnea"
        ],
        "co_keywords": [],
        "message": "Severe difficulty breathing or gasping for air requires immediate emergency oxygen and respiratory assessment."
    },
    {
        "name": "Stroke Symptoms (F.A.S.T. Signs)",
        "keywords": [
            r"slurred\s*speech", 
            r"facial\s*droop", 
            r"drooping\s*face", 
            r"(weakness|numbness)\s*on\s*one\s*side", 
            r"stroke\s*symptom",
            r"sudden\s*paralysis",
                        r"loss\s*of\s*speech",
            r"aphasia"
        ],
        "co_keywords": [],
        "message": "Symptoms of facial drooping, slurred speech, or sudden weakness on one side of the body indicate a potential stroke. Immediate intervention is critical."
    },
    {
        "name": "Loss of Consciousness or Syncope",
        "keywords": [
            r"faint", 
            r"pass(ed)?\s*out", 
            r"loss\s*of\s*consciousness", 
            r"unconscious", 
            r"black(ed)?\s*out",
            r"syncope"
        ],
        "co_keywords": [],
        "message": "Loss of consciousness, fainting, or sudden collapse indicates a serious cardiovascular or neurological interruption."
    },
    {
        "name": "Severe Allergic Reaction (Anaphylaxis)",
        "keywords": [
            r"anaphylaxis", 
            r"throat\s*(swell|tight|closing)", 
            r"tongue\s*swell", 
            r"severe\s*allergic\s*reaction",
            r"difficulty\s*(swallow|breath).*(allergic|rash|hive)"
        ],
        "co_keywords": [],
        "message": "Anaphylaxis (severe allergic reaction with throat/tongue swelling or breathing difficulty) is a medical emergency that can block the airway."
    },
    {
        "name": "High Fever with Seizures",
        "keywords": [r"fever", r"temperature", r"high\s*temp", r"hyperthermia"],
        "co_keywords": [r"seizure", r"convulsion", r"fit", r"spasm", r"shak(ing|e)"],
        "message": "High fever combined with seizures or convulsions indicates a neurological emergency requiring immediate medical intervention."
    },
    {
        "name": "Uncontrolled Bleeding",
        "keywords": [r"bleed", r"blood", r"hemorrhage"],
        "co_keywords": [r"uncontrolled", r"heavy", r"cannot\s*stop", r"severe", r"gush", r"pour"],
        "message": "Uncontrolled or severe bleeding requires immediate emergency pressure and surgical/medical intervention."
    }
]

def check_emergency(symptoms_text: str, conditions_text: str = "") -> dict:
    """
    Scans symptom description and existing conditions for emergency red flags.
    Returns:
        dict: {
            "emergency_flag": bool,
            "matched_condition": str or None,
            "message": str or None
        }
    """
    combined = f"{symptoms_text} {conditions_text}".lower()
    
    for criteria in EMERGENCY_CRITERIA:
        # Check if primary keywords match
        matched_primary = False
        for kw in criteria["keywords"]:
            if re.search(kw, combined):
                matched_primary = True
                break
                
        if matched_primary:
            # If co-keywords exist, check them
            if criteria["co_keywords"]:
                matched_co = False
                for co_kw in criteria["co_keywords"]:
                    if re.search(co_kw, combined):
                        matched_co = True
                        break
                if matched_co:
                    return {
                        "emergency_flag": True,
                        "matched_condition": criteria["name"],
                        "message": criteria["message"]
                    }
            else:
                return {
                    "emergency_flag": True,
                    "matched_condition": criteria["name"],
                    "message": criteria["message"]
                }
                
    return {
        "emergency_flag": False,
        "matched_condition": None,
        "message": None
    }
