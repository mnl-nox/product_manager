from __future__ import annotations

import unittest

from api import app


class PurchasingSchemaTests(unittest.TestCase):
    """Regression checks for the purchasing persistence model."""

    def setUp(self):
        with app.get_db() as conn:
            conn.execute("DELETE FROM purchase_approvals")
            conn.execute("DELETE FROM purchase_order_items")
            conn.execute("DELETE FROM purchase_orders")
            conn.execute("DELETE FROM supplier_quotes")
            conn.execute("DELETE FROM purchase_request_items")
            conn.execute("DELETE FROM purchase_requests")
            conn.execute("DELETE FROM suppliers")
            conn.execute("DELETE FROM products")
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
