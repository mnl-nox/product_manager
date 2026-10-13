from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from api import app


class SessionSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_db_path = app.DB_PATH
        cls.temp_dir = tempfile.TemporaryDirectory(prefix="product-manager-sessions-")
        app.DB_PATH = Path(cls.temp_dir.name) / "sessions.db"
        app.ensure_database()
        with app.get_db() as conn:
            conn.execute(
                "INSERT INTO app_users(username,password_hash,role) VALUES(?,?,?)",
                ("session-security-admin", app.hash_password("test-only-password"), "admin"),
            )
            cls.user_id = conn.execute(
                "SELECT id FROM app_users WHERE username=?", ("session-security-admin",)
            ).fetchone()[0]

    @classmethod
    def tearDownClass(cls):
        app.DB_PATH = cls.previous_db_path
        cls.temp_dir.cleanup()

    def setUp(self):
        with app.get_db() as conn:
            conn.execute("DELETE FROM app_sessions")
            conn.execute("UPDATE app_users SET active=1 WHERE id=?", (self.user_id,))

    def handler(self, token):
        handler = app.AppHandler.__new__(app.AppHandler)
        handler.headers = {"Cookie": f"pm_session={token}"}
        return handler

    def test_session_token_is_random_hashed_at_rest_and_resolves_to_active_user(self):
        token, csrf = app.issue_session(self.user_id)
        with app.get_db() as conn:
            row = conn.execute(
                "SELECT token_hash, csrf_token FROM app_sessions WHERE user_id=?",
                (self.user_id,),
            ).fetchone()
        self.assertNotEqual(token, row["token_hash"])
        self.assertEqual(app.token_digest(token), row["token_hash"])
        self.assertEqual(csrf, row["csrf_token"])
        self.assertEqual(self.handler(token).current_session()["id"], self.user_id)

    def test_expired_and_deactivated_user_sessions_are_rejected(self):
        token, _ = app.issue_session(self.user_id)
        with app.get_db() as conn:
            conn.execute(
                "UPDATE app_sessions SET expires_at=? WHERE token_hash=?",
                (int(time.time()) - 1, app.token_digest(token)),
            )
        self.assertIsNone(self.handler(token).current_session())
        with app.get_db() as conn:
            self.assertIsNone(conn.execute(
                "SELECT 1 FROM app_sessions WHERE token_hash=?", (app.token_digest(token),)
            ).fetchone())

        token, _ = app.issue_session(self.user_id)
        with app.get_db() as conn:
            conn.execute("UPDATE app_users SET active=0 WHERE id=?", (self.user_id,))
        self.assertIsNone(self.handler(token).current_session())

    def test_auth_cookie_is_http_only_same_site_and_secure_when_configured(self):
        handler = app.AppHandler.__new__(app.AppHandler)
        sent = []
        handler.send_header = lambda name, value: sent.append((name, value))
        with patch.dict(os.environ, {"PRODUCT_MANAGER_COOKIE_SECURE": "1"}):
            handler.send_auth_cookie("synthetic-token")
        cookie = next(value for name, value in sent if name == "Set-Cookie")
        for attribute in ("HttpOnly", "SameSite=Strict", "Secure", "Path=/"):
            self.assertIn(attribute, cookie)
        self.assertIn(f"Max-Age={app.SESSION_TTL_SECONDS}", cookie)

    def test_logout_cookie_clears_session_with_expiration(self):
        handler = app.AppHandler.__new__(app.AppHandler)
        sent = []
        handler.send_header = lambda name, value: sent.append((name, value))
        with patch.dict(os.environ, {"PRODUCT_MANAGER_COOKIE_SECURE": "1"}):
            handler.send_auth_cookie(None, clear=True)
        cookie = next(value for name, value in sent if name == "Set-Cookie")
        self.assertIn("Max-Age=0", cookie)
        self.assertIn("Secure", cookie)


if __name__ == "__main__":
    unittest.main()
