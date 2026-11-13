import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent))

import add_teacher
import app
from teacher_auth import make_password_record, verify_teacher


class AdminModeTests(unittest.TestCase):
    def setUp(self):
        self.teacher_store = {"advisor": make_password_record("test-password")}
        self.teacher_patch = patch.object(app, "teachers", self.teacher_store)
        self.teacher_patch.start()
        for activity in app.activities.values():
            if "new-student@mergington.edu" in activity["participants"]:
                activity["participants"].remove("new-student@mergington.edu")
        self.client = TestClient(app.app)

    def tearDown(self):
        self.client.close()
        self.teacher_patch.stop()

    def test_activity_list_is_public_but_enrollment_requires_teacher(self):
        activities = self.client.get("/activities")
        self.assertEqual(activities.status_code, 200)
        self.assertIn(
            "michael@mergington.edu",
            activities.json()["Chess Club"]["participants"],
        )

        response = self.client.post(
            "/activities/Chess Club/signup",
            params={"email": "new-student@mergington.edu"},
        )
        self.assertEqual(response.status_code, 401)

    def test_teacher_can_log_in_and_manage_enrollment(self):
        login = self.client.post(
            "/auth/login", auth=("advisor", "test-password")
        )
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.json(), {"username": "advisor"})

        auth = ("advisor", "test-password")
        signup = self.client.post(
            "/activities/Chess Club/signup",
            params={"email": "new-student@mergington.edu"},
            auth=auth,
        )
        self.assertEqual(signup.status_code, 200)

        unregister = self.client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "new-student@mergington.edu"},
            auth=auth,
        )
        self.assertEqual(unregister.status_code, 200)

    def test_invalid_teacher_credentials_are_rejected(self):
        response = self.client.post(
            "/auth/login", auth=("advisor", "wrong-password")
        )
        self.assertEqual(response.status_code, 401)

        response = self.client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"},
        )
        self.assertEqual(response.status_code, 401)

    def test_account_tool_stores_a_password_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            credential_file = Path(directory) / "teachers.json"
            with (
                patch.object(add_teacher, "TEACHERS_FILE", credential_file),
                patch.object(add_teacher.sys, "argv", ["add_teacher.py", "new-advisor"]),
                patch(
                    "add_teacher.getpass.getpass",
                    side_effect=["test-password", "test-password"],
                ),
            ):
                add_teacher.main()

            teachers = json.loads(credential_file.read_text(encoding="utf-8"))["teachers"]
            self.assertNotIn("password", teachers["new-advisor"])
            self.assertTrue(
                verify_teacher("new-advisor", "test-password", teachers)
            )


if __name__ == "__main__":
    unittest.main()
