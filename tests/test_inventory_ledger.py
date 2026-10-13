from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from api import app


class InventoryLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._previous_db_path = app.DB_PATH
        cls._temp_dir = tempfile.TemporaryDirectory(prefix="product-manager-inventory-ledger-")
        app.DB_PATH = Path(cls._temp_dir.name) / "ledger.db"
        app.ensure_database()
        with app.get_db() as conn:
            conn.execute(
                "INSERT INTO app_users (username, password_hash, role) VALUES (?, ?, ?)",
                ("ledger-test-admin", "test-hash", "admin"),
            )
            cls.user_id = conn.execute(
                "SELECT id FROM app_users WHERE username='ledger-test-admin'"
            ).fetchone()[0]

    @classmethod
    def tearDownClass(cls):
        app.DB_PATH = cls._previous_db_path
        cls._temp_dir.cleanup()

    def handler(self, path="/api/inventory/movements"):
        handler = app.AppHandler.__new__(app.AppHandler)
        handler.path = path
        handler.result = None
        handler.send_json = lambda payload, status=200: setattr(handler, "result", (status, payload))
        handler.headers = {}
        handler.client_address = ("127.0.0.1", 0)
        handler.current_user = {"id": self.user_id, "username": "ledger-test-admin", "role": "admin"}
        handler.require_authenticated_request = lambda request_path: handler.current_user
        handler.require_permission = lambda user, permission: True
        return handler

    def create_product(self, sku, quantity):
        handler = self.handler("/api/products")
        handler.create_product({
            "name": "Ledger item",
            "category": "Test",
            "sku": sku,
            "reference": sku,
            "brand": "Test",
            "status": "available",
            "price": 10,
            "quantity": quantity,
            "supplier": "Test supplier",
            "notes": "",
        })
        return handler.result

    def test_opening_balance_is_recorded(self):
        status, response = self.create_product("LEDGER-OPEN-1", 4)
        self.assertEqual(status, 201)
        with app.get_db() as conn:
            row = conn.execute(
                """SELECT movement_type, quantity_delta, quantity_before, quantity_after
                   FROM stock_movements WHERE product_id=?""",
                (response["id"],),
            ).fetchone()
        self.assertEqual(tuple(row), ("OPENING_BALANCE", 4, 0, 4))

    def test_zero_stock_does_not_create_a_zero_delta_movement(self):
        status, response = self.create_product("LEDGER-ZERO-1", 0)
        self.assertEqual(status, 201)
        with app.get_db() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM stock_movements WHERE product_id=?",
                (response["id"],),
            ).fetchone()[0]
        self.assertEqual(count, 0)

    def test_ledger_rejects_update_and_delete(self):
        status, response = self.create_product("LEDGER-IMMUTABLE-1", 2)
        self.assertEqual(status, 201)
        with app.get_db() as conn:
            movement_id = conn.execute(
                "SELECT id FROM stock_movements WHERE product_id=?",
                (response["id"],),
            ).fetchone()[0]
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("UPDATE stock_movements SET reason='tampered' WHERE id=?", (movement_id,))
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("DELETE FROM stock_movements WHERE id=?", (movement_id,))

    def test_inventory_endpoint_returns_movement_history(self):
        status, response = self.create_product("LEDGER-API-1", 3)
        self.assertEqual(status, 201)
        handler = self.handler("/api/inventory/movements")
        handler.do_GET()
        status, body = handler.result
        self.assertEqual(status, 200)
        self.assertEqual(body[0]["product_id"], response["id"])
        self.assertEqual(body[0]["movement_type"], "OPENING_BALANCE")


if __name__ == "__main__":
    unittest.main()
