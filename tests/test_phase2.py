# tests/test_phase2.py – Automated tests for Phase 2 clinical logic
import unittest
import json
from app import create_app
from database import db
from models.assessment import Assessment
from utils.emergency_detector import check_emergency
from utils.confidence_score import calculate_confidence

class Phase2TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test-secret-key-phase2",
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def test_emergency_detector(self):
        # Heart attack signs (Chest pain + sweating)
        res = check_emergency("I am experiencing chest pain and cold sweat", "")
        self.assertTrue(res["emergency_flag"])
        self.assertIn("Potential Cardiac Event", res["matched_condition"])

        # Non-emergency symptoms
        res_non = check_emergency("I have a slight headache and stuffy nose", "")
        self.assertFalse(res_non["emergency_flag"])

    def test_confidence_score(self):
        # General confidence scoring range
        conf = calculate_confidence("Viral Fever", "I have fever and body aches", 25, "None", [])
        self.assertTrue(50.0 <= conf <= 99.0)

    def test_analyze_flow_and_followup(self):
        # 1. Register User
        reg_response = self.client.post(
            "/api/register",
            json={
                "fullname": "Clinical Test User",
                "email": "clinical@example.com",
                "password": "Clinical@1234",
                "confirm_password": "Clinical@1234",
            },
        )
        self.assertEqual(reg_response.status_code, 201)

        # 2. Login User
        login_response = self.client.post(
            "/api/login",
            json={"email": "clinical@example.com", "password": "Clinical@1234"},
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.get_json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Submit upgraded assessment
        payload = {
            "primary_symptom": "High fever",
            "secondary_symptoms": ["Cough", "Headache"],
            "age": 30,
            "gender": "Female",
            "pregnancy_status": "Not Pregnant",
            "duration": "1–3 Days",
            "weight": "60 kg",
            "height": "165 cm",
            "pain_level": 6,
            "body_temperature": 101.2,
            "blood_pressure": "120/80",
            "medical_conditions": "None",
            "medications": "None",
            "allergies": "None",
            "smoking_status": "Non-smoker",
            "alcohol_consumption": "Occasional / Social"
        }

        response = self.client.post("/api/analyze", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn("assessment_id", data)
        self.assertIn("possible_condition", data)
        self.assertIn("confidence_score", data)
        self.assertIn("top_conditions", data)
        self.assertIn("followup_questions", data)
        
        # Verify database insertion
        with self.app.app_context():
            db_record = Assessment.query.get(data["assessment_id"])
            self.assertIsNotNone(db_record)
            self.assertEqual(db_record.weight, "60 kg")
            self.assertEqual(db_record.pain_level, 6)

        # 4. Test Follow-up Questions API
        followup_payload = {
            "answer": "Yes",
            "question": data["followup_questions"][0],
            "assessment_id": data["assessment_id"]
        }
        followup_res = self.client.post("/api/followup", json=followup_payload, headers=headers)
        self.assertEqual(followup_res.status_code, 200)
        
        followup_data = followup_res.get_json()
        self.assertIn("possible_condition", followup_data)

        # 5. Test Conversation Memory Symptom Update via Chat
        chat_payload = {
            "question": "I also have vomiting.",
            "assessment_id": data["assessment_id"]
        }
        chat_res = self.client.post("/api/chat", json=chat_payload, headers=headers)
        self.assertEqual(chat_res.status_code, 200)
        
        chat_data = chat_res.get_json()
        self.assertTrue(chat_data["updated"])
        self.assertIn("vomiting", chat_data["assessment"]["symptoms"])

if __name__ == "__main__":
    unittest.main()
