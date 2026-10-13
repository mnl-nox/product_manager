from __future__ import annotations

import io
import json
import unittest

from api import app


class SecurityControlTests(unittest.TestCase):
    def handler(self, *, headers=None):
        handler = app.AppHandler.__new__(app.AppHandler)
        handler.headers = headers or {}
        handler.result = None
        handler.send_json = lambda payload, status=200: setattr(handler, "result", (status, payload))
        handler.current_session = lambda: None
        return handler

    def post_as(self, path, role):
        handler = self.handler()
        payload = json.dumps({}).encode()
        handler.path = path
        handler.headers = {"Content-Length": str(len(payload))}
        handler.rfile = io.BytesIO(payload)
        handler.require_authenticated_request = lambda request_path: {
            "id": 1, "username": "permission-test", "role": role,
            "csrf_token": "csrf", "token_hash": "session-hash",
        }
        handler.validate_csrf = lambda user: True
        handler.do_POST()
        return handler.result

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

    def test_every_registered_get_api_route_requires_a_session(self):
        routes = (
            "/api/dashboard/export.csv", "/api/dashboard/export.xlsx", "/api/dashboard",
            "/api/categories", "/api/clients", "/api/inventory/movements", "/api/products",
            "/api/summary", "/api/hr/payroll-export.csv", "/api/purchasing/suppliers",
            "/api/purchasing/requests", "/api/purchasing/orders", "/api/purchasing/orders/1",
            "/api/purchasing/requests/1", "/api/hr/departments", "/api/hr/employees",
            "/api/hr/absences", "/api/hr/documents", "/api/hr/work-time",
            "/api/reports/dimensions", "/api/reports/summary", "/api/reports/sales",
            "/api/health", "/api/telemetry/status", "/api/integrations/google-sheets/status",
            "/api/auth/me", "/api/auth/users", "/api/work-items", "/api/finance/summary",
            "/api/finance/entries", "/api/alerts/stock", "/api/alerts/config",
        )
        for route in routes:
            with self.subTest(route=route):
                handler = self.handler()
                handler.current_session = lambda: None
                handler.path = route
                handler.do_GET()
                self.assertEqual(handler.result[0], 401)

    def test_every_registered_write_api_route_requires_a_session(self):
        routes = (
            "/api/auth/logout", "/api/auth/users", "/api/org-units", "/api/reports/sales",
            "/api/hr/departments", "/api/hr/employees", "/api/hr/absences",
            "/api/hr/documents", "/api/hr/work-time", "/api/purchasing/suppliers",
            "/api/purchasing/requests", "/api/purchasing/quotes",
            "/api/purchasing/requests/1/approve", "/api/purchasing/requests/1/order",
            "/api/purchasing/orders/1/receive", "/api/finance/entries",
            "/api/finance/entries/1/delete", "/api/work-items", "/api/telemetry",
            "/api/integrations/google-sheets/export", "/api/clients", "/api/products",
            "/api/products/1", "/api/products/1/deactivate", "/api/products/1/activate",
            "/api/products/1/delete", "/api/alerts/stock/1/threshold",
            "/api/alerts/stock/1/acknowledge",
        )
        for route in routes:
            with self.subTest(route=route):
                handler = self.handler()
                payload = b"{}"
                handler.path = route
                handler.current_session = lambda: None
                handler.headers = {"Content-Length": str(len(payload))}
                handler.rfile = io.BytesIO(payload)
                handler.do_POST()
                self.assertEqual(handler.result[0], 401)

    def test_role_restrictions_are_applied_by_business_endpoint_groups(self):
        denied = (
            ("/api/products", "viewer"),
            ("/api/products", "finance"),
            ("/api/finance/entries", "operator"),
            ("/api/purchasing/orders/1/receive", "finance"),
            ("/api/hr/employees", "operator"),
            ("/api/integrations/google-sheets/export", "operator"),
            ("/api/auth/users", "finance"),
        )
        for route, role in denied:
            with self.subTest(route=route, role=role):
                self.assertEqual(self.post_as(route, role)[0], 403)

    def test_every_registered_write_api_route_requires_csrf(self):
        routes = (
            "/api/auth/logout", "/api/auth/users", "/api/org-units", "/api/reports/sales",
            "/api/hr/departments", "/api/hr/employees", "/api/hr/absences",
            "/api/hr/documents", "/api/hr/work-time", "/api/purchasing/suppliers",
            "/api/purchasing/requests", "/api/purchasing/quotes",
            "/api/purchasing/requests/1/approve", "/api/purchasing/requests/1/order",
            "/api/purchasing/orders/1/receive", "/api/finance/entries",
            "/api/finance/entries/1/delete", "/api/work-items", "/api/telemetry",
            "/api/integrations/google-sheets/export", "/api/clients", "/api/products",
            "/api/products/1", "/api/products/1/deactivate", "/api/products/1/activate",
            "/api/products/1/delete", "/api/alerts/stock/1/threshold",
            "/api/alerts/stock/1/acknowledge",
        )
        for route in routes:
            with self.subTest(route=route):
                handler = self.handler(headers={"Content-Length": "2"})
                handler.path = route
                handler.current_session = lambda: None
                handler.rfile = io.BytesIO(b"{}")
                handler.require_authenticated_request = lambda request_path: {
                    "id": 1, "username": "csrf-test", "role": "admin", "csrf_token": "expected"
                }
                handler.do_POST()
                self.assertEqual(handler.result[0], 403)


if __name__ == "__main__":
    unittest.main()
