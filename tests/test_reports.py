from __future__ import annotations

import io
import json
import sqlite3
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

    def setUp(self):
        with app.get_db() as conn:
            conn.execute("DROP TRIGGER IF EXISTS stock_movements_no_update")
            conn.execute("DROP TRIGGER IF EXISTS stock_movements_no_delete")
            conn.execute("DELETE FROM stock_movements")
            conn.execute("""CREATE TRIGGER stock_movements_no_update
                            BEFORE UPDATE ON stock_movements
                            BEGIN SELECT RAISE(ABORT, 'stock movements are immutable'); END""")
            conn.execute("""CREATE TRIGGER stock_movements_no_delete
                            BEFORE DELETE ON stock_movements
                            BEGIN SELECT RAISE(ABORT, 'stock movements are immutable'); END""")
            conn.execute("DELETE FROM sales_items")
            conn.execute("DELETE FROM sales")
            conn.execute("DELETE FROM finance_entries")
            conn.execute("DELETE FROM products")
            conn.execute("DELETE FROM audit_log")
            conn.execute(
                "INSERT OR IGNORE INTO app_users (id, username, password_hash, role) VALUES (1, 'reports-test', 'test-hash', 'admin')"
            )
            self.user_id = conn.execute(
                "SELECT id FROM app_users WHERE username='reports-test'"
            ).fetchone()[0]
            self.product_id = conn.execute(
                """INSERT INTO products
                   (name, category, sku, reference, brand, status, price, quantity, supplier, created_by)
                   VALUES ('Report item', 'Test', 'REPORT-SKU', 'REPORT-REF', 'Example',
                           'available', 19.99, 5, 'Supplier', ?)""",
                (self.user_id,),
            ).lastrowid
            app.record_stock_movement(
                conn, product_id=self.product_id, movement_type="OPENING_BALANCE",
                quantity_delta=5, quantity_before=0, reason="Test fixture opening balance",
                actor_id=self.user_id, reference_type="product", reference_id=self.product_id,
            )

    def handler(self, path):
        handler = app.AppHandler.__new__(app.AppHandler)
        handler.path = path
        handler.result = None
        handler.current_user = {"id": 1, "username": "reports-test", "role": "admin"}
        handler.require_authenticated_request = lambda request_path: handler.current_user
        handler.send_json = lambda payload, status=200: setattr(handler, "result", (status, payload))
        return handler

    def post_json(self, path, payload):
        body = json.dumps(payload).encode("utf-8")
        handler = self.handler(path)
        handler.headers = {"Content-Length": str(len(body))}
        handler.rfile = io.BytesIO(body)
        handler.client_address = ("127.0.0.1", 0)
        handler.validate_csrf = lambda current_user: True
        handler.do_POST()
        return handler.result

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

    def test_paid_sale_post_updates_stock_ledger_and_finance_together(self):
        status, response = self.post_json(
            "/api/reports/sales",
            {
                "product_id": self.product_id,
                "quantity": 2,
                "unit_price": "19.99",
                "sale_date": "2026-10-13",
                "status": "paid",
            },
        )
        self.assertEqual(status, 201)
        self.assertGreater(response["id"], 0)
        self.assertEqual(response["total_cents"], 3998)
        with app.get_db() as conn:
            quantity = conn.execute(
                "SELECT quantity FROM products WHERE id=?", (self.product_id,)
            ).fetchone()[0]
            sale = conn.execute(
                "SELECT status, total_cents FROM sales WHERE id=?", (response["id"],)
            ).fetchone()
            finance = conn.execute(
                """SELECT status, amount_cents FROM finance_entries
                   WHERE description LIKE ? AND entry_type='income'""",
                (f"Venda #{response['id']}%",),
            ).fetchone()
            movements = conn.execute(
                """SELECT movement_type, quantity_delta, quantity_before, quantity_after
                   FROM stock_movements WHERE reference_type='sale' AND reference_id=?""",
                (response["id"],),
            ).fetchall()
        self.assertEqual(quantity, 3)
        self.assertEqual(tuple(sale), ("paid", 3998))
        self.assertEqual(tuple(finance), ("paid", 3998))
        self.assertEqual(len(movements), 1)
        self.assertEqual(tuple(movements[0]), ("SALE_OUT", -2, 5, 3))

    def test_paid_sale_rolls_back_every_write_when_ledger_insert_fails(self):
        with app.get_db() as conn:
            conn.execute("""CREATE TRIGGER reject_sale_movement
                            BEFORE INSERT ON stock_movements
                            WHEN NEW.reference_type='sale'
                            BEGIN SELECT RAISE(ABORT, 'injected ledger failure'); END""")

        with self.assertRaisesRegex(sqlite3.IntegrityError, "injected ledger failure"):
            self.post_json(
                "/api/reports/sales",
                {
                    "product_id": self.product_id,
                    "quantity": 2,
                    "unit_price": "19.99",
                    "sale_date": "2026-10-13",
                    "status": "paid",
                },
            )

        with app.get_db() as conn:
            quantity = conn.execute(
                "SELECT quantity FROM products WHERE id=?", (self.product_id,)
            ).fetchone()[0]
            sales = conn.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
            items = conn.execute("SELECT COUNT(*) FROM sales_items").fetchone()[0]
            income = conn.execute(
                "SELECT COUNT(*) FROM finance_entries WHERE category='Vendas'"
            ).fetchone()[0]
            movements = conn.execute(
                "SELECT COUNT(*) FROM stock_movements WHERE reference_type='sale'"
            ).fetchone()[0]
            audit_events = conn.execute(
                "SELECT COUNT(*) FROM audit_log WHERE entity='sale'"
            ).fetchone()[0]
            conn.execute("DROP TRIGGER reject_sale_movement")

        self.assertEqual(quantity, 5)
        self.assertEqual((sales, items, income, movements, audit_events), (0, 0, 0, 0, 0))

    def test_paid_sale_rolls_back_when_audit_insert_fails(self):
        with app.get_db() as conn:
            conn.execute("""CREATE TRIGGER reject_sale_audit
                            BEFORE INSERT ON audit_log
                            WHEN NEW.entity='sale'
                            BEGIN SELECT RAISE(ABORT, 'injected audit failure'); END""")

        with self.assertRaisesRegex(sqlite3.IntegrityError, "injected audit failure"):
            self.post_json(
                "/api/reports/sales",
                {
                    "product_id": self.product_id,
                    "quantity": 2,
                    "unit_price": "19.99",
                    "sale_date": "2026-10-13",
                    "status": "paid",
                },
            )

        with app.get_db() as conn:
            quantity = conn.execute(
                "SELECT quantity FROM products WHERE id=?", (self.product_id,)
            ).fetchone()[0]
            counts = tuple(
                conn.execute(query).fetchone()[0]
                for query in (
                    "SELECT COUNT(*) FROM sales",
                    "SELECT COUNT(*) FROM sales_items",
                    "SELECT COUNT(*) FROM finance_entries WHERE category='Vendas'",
                    "SELECT COUNT(*) FROM stock_movements WHERE reference_type='sale'",
                    "SELECT COUNT(*) FROM audit_log WHERE entity='sale'",
                )
            )
            conn.execute("DROP TRIGGER reject_sale_audit")

        self.assertEqual(quantity, 5)
        self.assertEqual(counts, (0, 0, 0, 0, 0))

    def test_planned_sale_does_not_decrease_stock(self):
        status, response = self.post_json(
            "/api/reports/sales",
            {
                "product_id": self.product_id,
                "quantity": 2,
                "unit_price": "19.99",
                "sale_date": "2026-10-13",
                "status": "planned",
            },
        )
        self.assertEqual(status, 201)
        with app.get_db() as conn:
            quantity = conn.execute(
                "SELECT quantity FROM products WHERE id=?", (self.product_id,)
            ).fetchone()[0]
            finance_status = conn.execute(
                "SELECT status FROM finance_entries WHERE description LIKE ?",
                (f"Venda #{response['id']}%",),
            ).fetchone()[0]
            sale_movements = conn.execute(
                "SELECT COUNT(*) FROM stock_movements WHERE reference_type='sale' AND reference_id=?",
                (response["id"],),
            ).fetchone()[0]
        self.assertEqual(quantity, 5)
        self.assertEqual(finance_status, "planned")
        self.assertEqual(sale_movements, 0)

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
