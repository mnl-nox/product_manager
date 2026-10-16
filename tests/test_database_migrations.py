from __future__ import annotations

import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from api import app


class LegacyDatabaseMigrationTests(unittest.TestCase):
    def setUp(self):
        self.previous_db_path = app.DB_PATH
        self.temp_dir = tempfile.TemporaryDirectory(prefix="product-manager-legacy-db-")
        self.legacy_path = Path(self.temp_dir.name) / "legacy.db"
        with closing(sqlite3.connect(self.legacy_path)) as conn, conn:
            conn.executescript("""
                CREATE TABLE app_users (
                    id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL, role TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE products (
                    id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
                    sku TEXT NOT NULL UNIQUE, reference TEXT NOT NULL, brand TEXT NOT NULL,
                    status TEXT NOT NULL, price REAL NOT NULL, quantity INTEGER NOT NULL,
                    supplier TEXT NOT NULL, notes TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE finance_entries (
                    id INTEGER PRIMARY KEY, entry_type TEXT NOT NULL, category TEXT NOT NULL,
                    description TEXT NOT NULL, amount REAL, entry_date TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'paid', created_by INTEGER,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                INSERT INTO app_users(id, username, password_hash, role)
                    VALUES (1, 'legacy-admin', 'test-hash', 'admin');
                INSERT INTO products(id, name, category, sku, reference, brand, status,
                                     price, quantity, supplier)
                    VALUES (1, 'Legacy product', 'Test', 'LEGACY-1', 'LEGACY-1', 'Test',
                            'available', 12.34, 7, 'Legacy supplier');
                INSERT INTO finance_entries(id, entry_type, category, description,
                                            amount, entry_date, status, created_by)
                    VALUES (1, 'expense', 'Legacy', 'Legacy expense', 12.34,
                            '2026-01-02', 'paid', 1);
            """)
        app.DB_PATH = self.legacy_path

    def tearDown(self):
        app.DB_PATH = self.previous_db_path
        self.temp_dir.cleanup()

    def test_legacy_finance_migration_aborts_without_losing_invalid_rows(self):
        with closing(sqlite3.connect(self.legacy_path)) as conn, conn:
            conn.executemany(
                "INSERT INTO finance_entries(id, entry_type, category, description, amount, entry_date, status, created_by) "
                "VALUES (?, 'expense', 'Legacy', ?, ?, '2026-01-03', 'paid', 1)",
                (
                    (2, "Zero amount", 0),
                    (3, "Negative amount", -4.25),
                    (4, "Null amount", None),
                ),
            )

        with self.assertRaisesRegex(RuntimeError, r"invalid row IDs: 2, 3, 4"):
            app.ensure_database()

        # The legacy table and every row must remain intact after the abort.
        with closing(sqlite3.connect(self.legacy_path)) as conn:
            columns = {row[1] for row in conn.execute("PRAGMA table_info(finance_entries)")}
            rows = conn.execute(
                "SELECT id, amount FROM finance_entries ORDER BY id"
            ).fetchall()
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]

        self.assertIn("amount", columns)
        self.assertNotIn("amount_cents", columns)
        self.assertEqual(rows, [(1, 12.34), (2, 0.0), (3, -4.25), (4, None)])
        self.assertEqual(integrity, "ok")

    def test_legacy_schema_migrates_once_and_preserves_values(self):
        app.ensure_database()
        app.ensure_database()

        with app.get_db() as conn:
            finance_columns = {row[1] for row in conn.execute("PRAGMA table_info(finance_entries)")}
            amount = conn.execute(
                "SELECT amount_cents FROM finance_entries WHERE id=1"
            ).fetchone()[0]
            product_columns = {row[1] for row in conn.execute("PRAGMA table_info(products)")}
            product = conn.execute("SELECT quantity, active FROM products WHERE id=1").fetchone()
            movements = conn.execute(
                "SELECT movement_type, quantity_delta, quantity_before, quantity_after "
                "FROM stock_movements WHERE product_id=1"
            ).fetchall()
            integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]

        self.assertIn("amount_cents", finance_columns)
        self.assertNotIn("amount", finance_columns)
        self.assertEqual(amount, 1234)
        self.assertTrue({"created_by", "active"}.issubset(product_columns))
        self.assertEqual(tuple(product), (7, 1))
        self.assertEqual(len(movements), 1)
        self.assertEqual(tuple(movements[0]), ("OPENING_BALANCE", 7, 0, 7))
        self.assertEqual(integrity, "ok")


if __name__ == "__main__":
    unittest.main()
