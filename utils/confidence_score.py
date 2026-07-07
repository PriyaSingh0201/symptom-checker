# utils/confidence_score.py – Clinical confidence scoring engine

def calculate_confidence(
    condition_name: str,
    symptoms: str,
    age: int,
    existing_diseases: str,
    retrieved_evidence: list,
    ai_confidence: float = None
) -> float:
    """
    Calculates clinical confidence score (50% to 99%) based on multiple factors:
    - Symptom match overlap
    - Age risk compatibility
    - Existing disease pre-dispositions
    - Retrieved official medical documentation matching
    - Blended AI engine feedback
    """
    score = 50.0 # Base minimum confidence
    
    cond_lower = condition_name.lower()
    sym_lower = symptoms.lower()
    dis_lower = (existing_diseases or "").lower()
    
    # 1. Symptom similarity (up to 20 points)
    common_terms = {
        "influenza": ["fever", "chills", "cough", "body ache", "fatigue", "throat", "shivering"],
        "cold": ["cough", "runny nose", "sneezing", "throat", "congestion", "stuffy"],
        "migraine": ["headache", "head pain", "throbbing", "light", "nausea", "sound"],
        "cardiac": ["chest pain", "tightness", "palpitation", "heart", "breath", "sweat", "arm pain"],
        "gastroenteritis": ["vomit", "nausea", "diarrhea", "stomach", "cramp", "stool", "food"],
        "reflux": ["acidity", "heartburn", "acid", "bloat", "burning", "reflux", "indigestion"],
        "asthma": ["wheeze", "breath", "cough", "tightness", "asthma", "inhaler"],
        "hypertension": ["dizzy", "headache", "blood pressure", "bp", "vision", "hypertension"],
        "diabetes": ["thirst", "urinate", "fatigue", "sugar", "insulin", "polyuria", "weight loss"],
        "uti": ["burn", "urination", "urine", "uti", "bladder", "frequency"],
        "anemia": ["fatigue", "weakness", "tired", "pale", "lethargy", "iron", "anemia"]
    }
    
    matched_key = None
    for key in common_terms:
        if key in cond_lower:
            matched_key = key
            break
            
    if matched_key:
        matches = sum(1 for term in common_terms[matched_key] if term in sym_lower)
        keyword_matches = min(matches * 4, 20) # 4 pts per matching symptom word, max 20
        score += keyword_matches
    else:
        # General overlap search
        matches = sum(1 for w in cond_lower.split() if w in sym_lower and len(w) > 3)
        score += min(matches * 5, 10)
        
    # 2. Age profile compatibility (up to 10 points)
    age_points = 10
    if "cardiac" in cond_lower or "hypertension" in cond_lower:
        if age < 35:
            age_points = 3
        elif age < 50:
            age_points = 7
    elif "migraine" in cond_lower:
        if age > 65:
            age_points = 5
    score += age_points

    # 3. Existing disease predisposing factors (up to 10 points)
    disease_points = 0
    if dis_lower:
        predispositions = {
            "cardiac": ["heart", "bp", "hypertension", "cholesterol", "diabet", "angina"],
            "hypertension": ["kidney", "diabet", "obese", "weight", "stroke", "bp"],
            "asthma": ["allergy", "asthma", "bronch", "smoke", "copd", "respiratory"],
            "reflux": ["gastritis", "ulcer", "hernia", "stomach", "gerd"],
            "diabetes": ["bp", "hypertension", "obese", "sugar", "pancreas"]
        }
        for cond_key, factors in predispositions.items():
            if cond_key in cond_lower:
                if any(fact in dis_lower for fact in factors):
                    disease_points = 10
                    break
    score += disease_points

    # 4. Retrieved evidence matching (up to 10 points)
    evidence_points = 0
    if retrieved_evidence:
        source_matches = 0
        for ev in retrieved_evidence:
            title = ev.get("title", "").lower()
            summary = ev.get("summary", "").lower()
            words = cond_lower.split()
            # Count how many words of the condition appear in retrieved titles/summaries
            if any(w in title or w in summary for w in words if len(w) > 3):
                source_matches += 1
        evidence_points = min(source_matches * 5, 10)
    score += evidence_points

    # 5. Blend AI self-reported confidence if available
    if ai_confidence is not None:
        # Standardize between 0 and 100
        ai_val = float(ai_confidence)
        if ai_val < 1: # If it's a decimal (e.g. 0.88), convert to percent
            ai_val *= 100
        score = (score * 0.3) + (ai_val * 0.7)
    else:
        # Fallback variance
        score += 5.0

    # Ensure score falls between a realistic clinical range (50% to 98% default)
    return float(round(max(50.0, min(99.0, score)), 1))
