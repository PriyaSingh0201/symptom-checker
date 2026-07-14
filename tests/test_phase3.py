import unittest
from flask import session
from app import create_app
from utils.conversation_memory import store_consultation


class Phase3ConsultationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test-secret-key-phase3",
        })
        self.client = self.app.test_client()

    def test_store_consultation_keeps_phase3_context(self):
        with self.app.test_request_context("/", method="GET"):
            store_consultation({
                "id": 42,
                "consultation_id": "abc123",
                "symptoms": "fever and cough",
                "conversation_history": [{"role": "assistant", "content": "When did it start?"}],
                "follow_up_answers": {"When did it start?": "Yesterday"},
                "follow_up_questions": ["When did it start?"],
                "top5_conditions": [{"condition": "Influenza", "probability": 70}],
            })
            self.assertEqual(session["active_consultation"]["conversation_history"][0]["content"], "When did it start?")
            self.assertEqual(session["active_consultation"]["follow_up_answers"]["When did it start?"], "Yesterday")
            self.assertEqual(session["active_consultation"]["top5_conditions"][0]["condition"], "Influenza")


if __name__ == "__main__":
    unittest.main()
