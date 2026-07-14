from utils.pdf_generator import generate_pdf


def test_generate_pdf_handles_missing_fields():
    assessment = {
        "id": 42,
        "symptoms": "Headache and nausea",
        "age": 30,
        "gender": "Female",
        "duration": "2 days",
        "medical_conditions": "",
        "top_conditions": "not-a-list",
        "evidence_sources": None,
        "health_advice": None,
        "explanation": None,
        "recommended_doctor": None,
        "emergency_flag": False,
        "created_date": "01 Jan 2024",
    }
    user = {"fullname": "", "email": "demo@example.com"}

    pdf_bytes = generate_pdf(assessment, user)

    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")
