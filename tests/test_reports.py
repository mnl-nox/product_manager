from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from api import app


class ReportsApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._previous_db_path = app.DB_PATH
        cls._temp_dir = tempfile.TemporaryDirectory(prefix="product-manager-reportsapitests-")
        app.DB_PATH = Path(cls._temp_dir.name) / "test.db"
        app.ensure_database()

    @classmethod
    def tearDownClass(cls):
        app.DB_PATH = cls._previous_db_path
        cls._temp_dir.cleanup()

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

    def test_reporting_dimensions_are_migrated(self):
        with app.get_db() as conn:
            finance_columns = {row[1] for row in conn.execute("PRAGMA table_info(finance_entries)")}
            sales_columns = {row[1] for row in conn.execute("PRAGMA table_info(sales)")}
            names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({"department_id", "org_unit_id"}.issubset(finance_columns))
        self.assertTrue({"department_id", "org_unit_id"}.issubset(sales_columns))
        self.assertIn("org_units", names)

    def test_summary_returns_period_and_zero_safe_margin(self):
        handler = self.handler("/api/reports/summary?from=2026-01-01&to=2026-01-31")
        handler.do_GET()
        status, body = handler.result
        self.assertEqual(status, 200)
        self.assertEqual(body["period"], {"from": "2026-01-01", "to": "2026-01-31"})
        self.assertIn("profit_cents", body["totals"])
        self.assertIsNone(body["totals"]["profit_margin_percent"])
        self.assertIn("topProducts", body)
        self.assertIn("byDepartment", body)
        self.assertIn("byUnit", body)

    def test_summary_rejects_reversed_period(self):
        handler = self.handler("/api/reports/summary?from=2026-02-01&to=2026-01-01")
        handler.do_GET()
        self.assertEqual(handler.result[0], 400)


if __name__ == "__main__":
    unittest.main()
