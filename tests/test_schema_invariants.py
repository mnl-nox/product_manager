from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path


SCHEMA_PATH = Path(__file__).resolve().parents[1] / "db" / "schema.sql"


class SchemaInvariantTests(unittest.TestCase):
    """Characterize database constraints that protect critical business records."""

    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.user_id = self.connection.execute(
            "INSERT INTO app_users (username, password_hash, role) VALUES (?, ?, ?)",
            ("schema-test-admin", "test-hash", "admin"),
        ).lastrowid
        self.product_id = self.connection.execute(
            """INSERT INTO products
               (name, category, sku, reference, brand, status, price, quantity, supplier)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("Produto de teste", "Teste", "SCHEMA-1", "REF-1", "Marca", "available", 10.0, 5, "Fornecedor"),
        ).lastrowid
        self.connection.commit()

    def tearDown(self):
        self.connection.close()

    def test_finance_entries_reject_non_positive_amounts(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                """INSERT INTO finance_entries
                   (entry_type, category, description, amount_cents, entry_date)
                   VALUES ('expense', 'Teste', 'Valor inválido', 0, '2026-01-01')"""
            )

    def test_purchase_order_item_rejects_received_quantity_above_ordered(self):
        supplier_id = self.connection.execute(
            "INSERT INTO suppliers (name) VALUES (?)", ("Fornecedor teste",)
        ).lastrowid
        request_id = self.connection.execute(
            """INSERT INTO purchase_requests (description, requested_by)
               VALUES (?, ?)""",
            ("Compra de teste", self.user_id),
        ).lastrowid
        order_id = self.connection.execute(
            """INSERT INTO purchase_orders (request_id, supplier_id, total_cents)
               VALUES (?, ?, ?)""",
            (request_id, supplier_id, 1000),
        ).lastrowid

        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                """INSERT INTO purchase_order_items
                   (order_id, product_id, description, ordered_quantity, received_quantity, unit_cents)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (order_id, self.product_id, "Item de teste", 2, 3, 500),
            )

    def test_stock_movement_rejects_inconsistent_quantity_transition(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                """INSERT INTO stock_movements
                   (product_id, movement_type, quantity_delta, quantity_before,
                    quantity_after, reason)
                   VALUES (?, 'ADJUSTMENT', 2, 5, 8, 'Transição inconsistente')""",
                (self.product_id,),
            )

    def test_stock_movement_is_append_only(self):
        movement_id = self.connection.execute(
            """INSERT INTO stock_movements
               (product_id, movement_type, quantity_delta, quantity_before,
                quantity_after, reason)
               VALUES (?, 'ADJUSTMENT', 1, 5, 6, 'Movimento válido')""",
            (self.product_id,),
        ).lastrowid
        self.connection.commit()

        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "UPDATE stock_movements SET reason=? WHERE id=?",
                ("Tentativa de alteração", movement_id),
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.connection.execute(
                "DELETE FROM stock_movements WHERE id=?",
                (movement_id,),
            )


if __name__ == "__main__":
    unittest.main()
