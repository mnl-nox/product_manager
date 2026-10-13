from __future__ import annotations

import unittest

from api import app


class SecurityControlTests(unittest.TestCase):
    def handler(self, *, headers=None):
        handler = app.AppHandler.__new__(app.AppHandler)
        handler.headers = headers or {}
        handler.result = None
        handler.send_json = lambda payload, status=200: setattr(handler, "result", (status, payload))
        return handler

    def test_admin_can_pass_all_permission_checks(self):
        handler = self.handler()
        for permission in ("read", "catalog:write", "finance:read", "finance:write", "alerts:write"):
            with self.subTest(permission=permission):
                self.assertTrue(handler.require_permission({"role": "admin"}, permission))
        self.assertIsNone(handler.result)

    def test_operator_can_write_catalog_but_not_finance(self):
        handler = self.handler()
        self.assertTrue(handler.require_permission({"role": "operator"}, "catalog:write"))
        self.assertTrue(handler.require_permission({"role": "operator"}, "alerts:write"))
        self.assertFalse(handler.require_permission({"role": "operator"}, "finance:write"))
        self.assertEqual(handler.result[0], 403)

    def test_finance_role_is_limited_to_finance_and_read_permissions(self):
        handler = self.handler()
        self.assertTrue(handler.require_permission({"role": "finance"}, "read"))
        self.assertTrue(handler.require_permission({"role": "finance"}, "finance:read"))
        self.assertTrue(handler.require_permission({"role": "finance"}, "finance:write"))
        self.assertFalse(handler.require_permission({"role": "finance"}, "catalog:write"))
        self.assertEqual(handler.result[0], 403)

    def test_viewer_has_read_only_permission(self):
        handler = self.handler()
        self.assertTrue(handler.require_permission({"role": "viewer"}, "read"))
        self.assertFalse(handler.require_permission({"role": "viewer"}, "catalog:write"))
        self.assertEqual(handler.result[0], 403)

    def test_unknown_role_is_denied(self):
        handler = self.handler()
        self.assertFalse(handler.require_permission({"role": "unknown"}, "read"))
        self.assertEqual(handler.result[0], 403)

    def test_csrf_rejects_missing_token(self):
        handler = self.handler(headers={"Host": "erp.example.test"})
        self.assertFalse(handler.validate_csrf({"csrf_token": "expected"}))
        self.assertEqual(handler.result[0], 403)

    def test_csrf_rejects_wrong_token(self):
        handler = self.handler(headers={"Host": "erp.example.test", "X-CSRF-Token": "wrong"})
        self.assertFalse(handler.validate_csrf({"csrf_token": "expected"}))
        self.assertEqual(handler.result[0], 403)

    def test_csrf_rejects_foreign_origin_even_with_valid_token(self):
        handler = self.handler(headers={
            "Host": "erp.example.test",
            "Origin": "https://attacker.example.test",
            "X-CSRF-Token": "expected",
        })
        self.assertFalse(handler.validate_csrf({"csrf_token": "expected"}))
        self.assertEqual(handler.result[0], 403)

    def test_csrf_accepts_matching_origin_and_token(self):
        handler = self.handler(headers={
            "Host": "erp.example.test",
            "Origin": "https://erp.example.test",
            "X-CSRF-Token": "expected",
        })
        self.assertTrue(handler.validate_csrf({"csrf_token": "expected"}))
        self.assertIsNone(handler.result)


if __name__ == "__main__":
    unittest.main()
