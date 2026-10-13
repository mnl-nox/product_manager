from __future__ import annotations

import unittest

from api import app


class ReportsApiTests(unittest.TestCase):
    def handler(self, path):
        handler = app.AppHandler.__new__(app.AppHandler)
        handler.path = path
        handler.result = None
        handler.current_user = {"id": 1, "username": "reports-test", "role": "admin"}
        handler.require_authenticated_request = lambda request_path: handler.current_user
        handler.send_json = lambda payload, status=200: setattr(handler, "result", (status, payload))
        return handler

    def test_reports_schema_exists(self):
        with app.get_db() as conn:
            names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"sales", "sales_items"}.issubset(names))

    def test_summary_returns_period_and_zero_safe_margin(self):
        handler = self.handler("/api/reports/summary?from=2026-01-01&to=2026-01-31")
        handler.do_GET()
        status, body = handler.result
        self.assertEqual(status, 200)
        self.assertEqual(body["period"], {"from": "2026-01-01", "to": "2026-01-31"})
        self.assertIn("profit_cents", body["totals"])
        self.assertIsNone(body["totals"]["profit_margin_percent"])
        self.assertIn("topProducts", body)

    def test_summary_rejects_reversed_period(self):
        handler = self.handler("/api/reports/summary?from=2026-02-01&to=2026-01-01")
        handler.do_GET()
        self.assertEqual(handler.result[0], 400)


if __name__ == "__main__":
    unittest.main()
