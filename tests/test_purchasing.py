from __future__ import annotations

import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from api import app


class PurchasingSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._previous_db_path = app.DB_PATH
        cls._temp_dir = tempfile.TemporaryDirectory(prefix="product-manager-purchasingschematests-")
        app.DB_PATH = Path(cls._temp_dir.name) / "test.db"
        app.ensure_database()

    @classmethod
    def tearDownClass(cls):
        app.DB_PATH = cls._previous_db_path
        cls._temp_dir.cleanup()

    """Regression checks for the purchasing persistence model."""

    def setUp(self):
        with app.get_db() as conn:
            # Each test gets an isolated ledger state; production immutability remains enabled.
            conn.execute("DROP TRIGGER IF EXISTS stock_movements_no_update")
            conn.execute("DROP TRIGGER IF EXISTS stock_movements_no_delete")
            conn.execute("DELETE FROM stock_movements")
            conn.execute("""CREATE TRIGGER stock_movements_no_update
                            BEFORE UPDATE ON stock_movements
                            BEGIN SELECT RAISE(ABORT, 'stock movements are immutable'); END""")
            conn.execute("""CREATE TRIGGER stock_movements_no_delete
                            BEFORE DELETE ON stock_movements
                            BEGIN SELECT RAISE(ABORT, 'stock movements are immutable'); END""")
            conn.execute("DELETE FROM purchase_approvals")
            conn.execute("DELETE FROM purchase_order_items")
            conn.execute("DELETE FROM purchase_orders")
            conn.execute("DELETE FROM supplier_quotes")
            conn.execute("DELETE FROM purchase_request_items")
            conn.execute("DELETE FROM purchase_requests")
            conn.execute("DELETE FROM suppliers")
            conn.execute("DELETE FROM products")
            conn.execute("DELETE FROM audit_log")
            conn.execute(
                "INSERT OR IGNORE INTO app_users (username, password_hash, role) VALUES (?, ?, ?)",
                ("purchasing-test-admin", "test-hash", "admin"),
            )
            self.user_id = conn.execute(
                "SELECT id FROM app_users WHERE username=?",
                ("purchasing-test-admin",),
            ).fetchone()[0]
            conn.execute(
                """INSERT INTO products (name, category, sku, reference, brand, status, price, quantity, supplier, created_by)
                   VALUES ('Test item', 'General', 'PURCHASE-TEST-SKU', 'TEST-REF', 'Example', 'available', 10, 2, 'Example', ?)""",
                (self.user_id,),
            )
            self.product_id = conn.execute(
                "SELECT id FROM products WHERE sku='PURCHASE-TEST-SKU'"
            ).fetchone()[0]

    def post_json(self, path, payload, role="admin"):
        body = json.dumps(payload).encode("utf-8")
        handler = app.AppHandler.__new__(app.AppHandler)
        handler.path = path
        handler.headers = {"Content-Length": str(len(body))}
        handler.rfile = io.BytesIO(body)
        handler.client_address = ("127.0.0.1", 0)
        handler.result = None
        handler.send_json = lambda response, status=200: setattr(handler, "result", (status, response))
        user = {
            "id": self.user_id,
            "username": "purchasing-test-admin",
            "role": role,
            "csrf_token": "test-csrf",
            "token_hash": "test-token-hash",
        }
        handler.require_authenticated_request = lambda request_path: user
        handler.validate_csrf = lambda current_user: True
        handler.do_POST()
        return handler.result

    def create_receipt_order(self, ordered_quantity=5):
        with app.get_db() as conn:
            request_id = conn.execute(
                "INSERT INTO purchase_requests (description, requested_by, status) VALUES ('Receipt integration test', ?, 'ordered')",
                (self.user_id,),
            ).lastrowid
            supplier_id = conn.execute(
                "INSERT INTO suppliers (name) VALUES ('Integration receipt supplier')"
            ).lastrowid
            order_id = conn.execute(
                "INSERT INTO purchase_orders (request_id, supplier_id, total_cents, created_by) VALUES (?, ?, 500, ?)",
                (request_id, supplier_id, self.user_id),
            ).lastrowid
            item_id = conn.execute(
                """INSERT INTO purchase_order_items
                   (order_id, product_id, description, ordered_quantity, unit_cents)
                   VALUES (?, ?, 'Test item', ?, 100)""",
                (order_id, self.product_id, ordered_quantity),
            ).lastrowid
        return request_id, order_id, item_id

    def test_purchasing_tables_exist(self):
        expected = {
            "suppliers", "purchase_requests", "purchase_request_items",
            "supplier_quotes", "purchase_orders", "purchase_order_items",
            "purchase_approvals",
        }
        with app.get_db() as conn:
            found = {
                row[0] for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
        self.assertTrue(expected.issubset(found))

    def test_supplier_tax_id_is_unique_when_present(self):
        with app.get_db() as conn:
            conn.execute("INSERT INTO suppliers (name, tax_id) VALUES ('Supplier A', 'TAX-123')")
            with self.assertRaises(Exception):
                conn.execute("INSERT INTO suppliers (name, tax_id) VALUES ('Supplier B', 'TAX-123')")

    def test_purchase_item_quantity_must_be_positive(self):
        with app.get_db() as conn:
            request_id = conn.execute(
                "INSERT INTO purchase_requests (description, requested_by) VALUES ('Test request', ?)",
                (self.user_id,),
            ).lastrowid
            with self.assertRaises(Exception):
                conn.execute(
                    """INSERT INTO purchase_request_items
                       (request_id, product_id, description, quantity, estimated_unit_cents)
                       VALUES (?, ?, 'Invalid quantity', 0, 100)""",
                    (request_id, self.product_id),
                )

    def test_partial_and_final_receipts_update_stock_and_ledger_atomically(self):
        request_id, order_id, item_id = self.create_receipt_order(ordered_quantity=5)

        status, response = self.post_json(
            f"/api/purchasing/orders/{order_id}/receive",
            {"items": [{"item_id": item_id, "quantity": 3}]},
        )
        self.assertEqual(status, 200)
        self.assertEqual(response["status"], "partially_received")

        with app.get_db() as conn:
            quantity = conn.execute(
                "SELECT quantity FROM products WHERE id=?", (self.product_id,)
            ).fetchone()[0]
            received_quantity = conn.execute(
                "SELECT received_quantity FROM purchase_order_items WHERE id=?", (item_id,)
            ).fetchone()[0]
            movement = conn.execute(
                """SELECT movement_type, quantity_delta, quantity_before, quantity_after
                   FROM stock_movements
                   WHERE product_id=? AND reference_type='purchase_order' AND reference_id=?""",
                (self.product_id, order_id),
            ).fetchone()
            request_status = conn.execute(
                "SELECT status FROM purchase_requests WHERE id=?", (request_id,)
            ).fetchone()[0]
        self.assertEqual(quantity, 5)
        self.assertEqual(received_quantity, 3)
        self.assertEqual(tuple(movement), ("PURCHASE_IN", 3, 2, 5))
        self.assertEqual(request_status, "ordered")

        status, response = self.post_json(
            f"/api/purchasing/orders/{order_id}/receive",
            {"items": [{"item_id": item_id, "quantity": 2}]},
        )
        self.assertEqual(status, 200)
        self.assertEqual(response["status"], "received")
        with app.get_db() as conn:
            quantity = conn.execute(
                "SELECT quantity FROM products WHERE id=?", (self.product_id,)
            ).fetchone()[0]
            received_quantity = conn.execute(
                "SELECT received_quantity FROM purchase_order_items WHERE id=?", (item_id,)
            ).fetchone()[0]
            movement_count = conn.execute(
                """SELECT COUNT(*) FROM stock_movements
                   WHERE product_id=? AND reference_type='purchase_order' AND reference_id=?""",
                (self.product_id, order_id),
            ).fetchone()[0]
            request_status = conn.execute(
                "SELECT status FROM purchase_requests WHERE id=?", (request_id,)
            ).fetchone()[0]
        self.assertEqual(quantity, 7)
        self.assertEqual(received_quantity, 5)
        self.assertEqual(movement_count, 2)
        self.assertEqual(request_status, "received")

    def test_invalid_receipt_does_not_change_order_stock_or_ledger(self):
        _, order_id, item_id = self.create_receipt_order(ordered_quantity=5)
        status, response = self.post_json(
            f"/api/purchasing/orders/{order_id}/receive",
            {"items": [{"item_id": item_id, "quantity": 6}]},
        )
        self.assertEqual(status, 400)
        self.assertIn("excede o pedido", response["error"])
        with app.get_db() as conn:
            quantity = conn.execute(
                "SELECT quantity FROM products WHERE id=?", (self.product_id,)
            ).fetchone()[0]
            received_quantity = conn.execute(
                "SELECT received_quantity FROM purchase_order_items WHERE id=?", (item_id,)
            ).fetchone()[0]
            movement_count = conn.execute(
                """SELECT COUNT(*) FROM stock_movements
                   WHERE product_id=? AND reference_type='purchase_order' AND reference_id=?""",
                (self.product_id, order_id),
            ).fetchone()[0]
        self.assertEqual(quantity, 2)
        self.assertEqual(received_quantity, 0)
        self.assertEqual(movement_count, 0)

    def test_receipt_rolls_back_every_write_when_ledger_insert_fails(self):
        request_id, order_id, item_id = self.create_receipt_order(ordered_quantity=5)
        with app.get_db() as conn:
            conn.execute("""CREATE TRIGGER reject_purchase_movement
                            BEFORE INSERT ON stock_movements
                            WHEN NEW.reference_type='purchase_order'
                            BEGIN SELECT RAISE(ABORT, 'injected ledger failure'); END""")

        with self.assertRaisesRegex(sqlite3.IntegrityError, "injected ledger failure"):
            self.post_json(
                f"/api/purchasing/orders/{order_id}/receive",
                {"items": [{"item_id": item_id, "quantity": 3}]},
            )

        with app.get_db() as conn:
            product_quantity = conn.execute(
                "SELECT quantity FROM products WHERE id=?", (self.product_id,)
            ).fetchone()[0]
            received_quantity = conn.execute(
                "SELECT received_quantity FROM purchase_order_items WHERE id=?", (item_id,)
            ).fetchone()[0]
            order_status = conn.execute(
                "SELECT status FROM purchase_orders WHERE id=?", (order_id,)
            ).fetchone()[0]
            request_status = conn.execute(
                "SELECT status FROM purchase_requests WHERE id=?", (request_id,)
            ).fetchone()[0]
            movement_count = conn.execute(
                "SELECT COUNT(*) FROM stock_movements WHERE reference_id=? AND reference_type='purchase_order'",
                (order_id,),
            ).fetchone()[0]
            audit_events = conn.execute(
                "SELECT COUNT(*) FROM audit_log WHERE entity='purchase_order' AND action='receive' AND entity_id=?",
                (order_id,),
            ).fetchone()[0]
            conn.execute("DROP TRIGGER reject_purchase_movement")

        self.assertEqual(product_quantity, 2)
        self.assertEqual(received_quantity, 0)
        self.assertEqual(order_status, "ordered")
        self.assertEqual(request_status, "ordered")
        self.assertEqual(movement_count, 0)
        self.assertEqual(audit_events, 0)

    def test_receipt_rolls_back_when_audit_insert_fails(self):
        request_id, order_id, item_id = self.create_receipt_order(ordered_quantity=5)
        with app.get_db() as conn:
            conn.execute("""CREATE TRIGGER reject_receipt_audit
                            BEFORE INSERT ON audit_log
                            WHEN NEW.entity='purchase_order' AND NEW.action='receive'
                            BEGIN SELECT RAISE(ABORT, 'injected audit failure'); END""")

        with self.assertRaisesRegex(sqlite3.IntegrityError, "injected audit failure"):
            self.post_json(
                f"/api/purchasing/orders/{order_id}/receive",
                {"items": [{"item_id": item_id, "quantity": 3}]},
            )

        with app.get_db() as conn:
            product_quantity = conn.execute(
                "SELECT quantity FROM products WHERE id=?", (self.product_id,)
            ).fetchone()[0]
            received_quantity = conn.execute(
                "SELECT received_quantity FROM purchase_order_items WHERE id=?", (item_id,)
            ).fetchone()[0]
            order_status = conn.execute(
                "SELECT status FROM purchase_orders WHERE id=?", (order_id,)
            ).fetchone()[0]
            request_status = conn.execute(
                "SELECT status FROM purchase_requests WHERE id=?", (request_id,)
            ).fetchone()[0]
            movement_count = conn.execute(
                "SELECT COUNT(*) FROM stock_movements WHERE reference_id=? AND reference_type='purchase_order'",
                (order_id,),
            ).fetchone()[0]
            audit_events = conn.execute(
                "SELECT COUNT(*) FROM audit_log WHERE entity='purchase_order' AND action='receive' AND entity_id=?",
                (order_id,),
            ).fetchone()[0]
            conn.execute("DROP TRIGGER reject_receipt_audit")

        self.assertEqual(product_quantity, 2)
        self.assertEqual(received_quantity, 0)
        self.assertEqual(order_status, "ordered")
        self.assertEqual(request_status, "ordered")
        self.assertEqual(movement_count, 0)
        self.assertEqual(audit_events, 0)

    def test_finance_role_cannot_receive_purchase_order(self):
        _, order_id, item_id = self.create_receipt_order(ordered_quantity=5)
        status, response = self.post_json(
            f"/api/purchasing/orders/{order_id}/receive",
            {"items": [{"item_id": item_id, "quantity": 1}]},
            role="finance",
        )
        self.assertEqual(status, 403)
        self.assertIn("administração ou operação", response["error"])
        with app.get_db() as conn:
            quantity = conn.execute(
                "SELECT quantity FROM products WHERE id=?", (self.product_id,)
            ).fetchone()[0]
            received_quantity = conn.execute(
                "SELECT received_quantity FROM purchase_order_items WHERE id=?", (item_id,)
            ).fetchone()[0]
        self.assertEqual(quantity, 2)
        self.assertEqual(received_quantity, 0)

    def test_order_receipt_cannot_exceed_ordered_quantity(self):
        with app.get_db() as conn:
            request_id = conn.execute(
                "INSERT INTO purchase_requests (description, requested_by, status) VALUES ('Test request', ?, 'approved')",
                (self.user_id,),
            ).lastrowid
            supplier_id = conn.execute(
                "INSERT INTO suppliers (name) VALUES ('Receipt supplier')"
            ).lastrowid
            order_id = conn.execute(
                "INSERT INTO purchase_orders (request_id, supplier_id, total_cents, created_by) VALUES (?, ?, 100, ?)",
                (request_id, supplier_id, self.user_id),
            ).lastrowid
            item_id = conn.execute(
                """INSERT INTO purchase_order_items
                   (order_id, product_id, description, ordered_quantity, unit_cents)
                   VALUES (?, ?, 'Test item', 2, 50)""",
                (order_id, self.product_id),
            ).lastrowid
            with self.assertRaises(Exception):
                conn.execute(
                    "UPDATE purchase_order_items SET received_quantity=3 WHERE id=?",
                    (item_id,),
                )


if __name__ == "__main__":
    unittest.main()
