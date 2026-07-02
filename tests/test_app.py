import unittest

from app import create_app
from database import db


class SymptomCheckerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test-secret",
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def test_login_page_renders(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Login", response.get_data(as_text=True))

    def test_app_branding_uses_symptom_checker_name(self):
        response = self.client.get("/login")
        html = response.get_data(as_text=True)
        self.assertIn("Symptom Checker", html)
        self.assertNotIn("AI Symptom Checker", html)

    def test_register_and_login_flow(self):
        register_response = self.client.post(
            "/api/register",
            json={
                "fullname": "Test User",
                "email": "test@example.com",
                "password": "Test@1234",
                "confirm_password": "Test@1234",
            },
        )
        self.assertEqual(register_response.status_code, 201)

        login_response = self.client.post(
            "/api/login",
            json={"email": "test@example.com", "password": "Test@1234"},
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("token", login_response.get_json())

    def test_standard_auth_route_aliases(self):
        register_response = self.client.post(
            "/register",
            json={
                "fullname": "Alias User",
                "email": "alias@example.com",
                "password": "Alias@1234",
                "confirm_password": "Alias@1234",
            },
        )
        self.assertEqual(register_response.status_code, 201)

        login_response = self.client.post(
            "/login",
            json={"email": "alias@example.com", "password": "Alias@1234"},
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("token", login_response.get_json())


if __name__ == "__main__":
    unittest.main()
