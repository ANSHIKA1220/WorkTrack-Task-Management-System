import unittest

from app import app


class AuthRoleTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, SECRET_KEY="test-secret")
        self.client = app.test_client()

    def login_session(self, role="Manager"):
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = role.lower()
            sess["role"] = role

    def test_dashboard_requires_login(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_manager_cannot_access_admin_users_api(self):
        self.login_session("Manager")
        response = self.client.get("/api/users")
        self.assertEqual(response.status_code, 403)
        self.assertIn("permission", response.get_json()["error"])

    def test_manager_can_open_tasks_api_before_database_call(self):
        self.login_session("Manager")
        response = self.client.post("/api/tasks", json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn("Employee", response.get_json()["error"])

    def test_admin_only_page_blocks_manager(self):
        self.login_session("Manager")
        response = self.client.get("/admin/users")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard", response.location)


if __name__ == "__main__":
    unittest.main()
