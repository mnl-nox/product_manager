from __future__ import annotations

import os
from pathlib import Path
import sqlite3
import tempfile
import unittest
from contextlib import closing

from scripts.database_recovery import backup_database, restore_database


class DatabaseRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="product-manager-recovery-")
        self.root = Path(self.temp_dir.name)
        self.source = self.root / "live.db"
        self.backup = self.root / "backup.db"
        self.restored = self.root / "restored.db"
        self.create_database(self.source, "before-backup")

    def tearDown(self):
        self.temp_dir.cleanup()

    @staticmethod
    def create_database(path: Path, marker: str):
        with closing(sqlite3.connect(path)) as conn, conn:
            conn.executescript("""
                CREATE TABLE app_users (id INTEGER PRIMARY KEY);
                CREATE TABLE products (id INTEGER PRIMARY KEY);
                CREATE TABLE finance_entries (id INTEGER PRIMARY KEY);
                CREATE TABLE recovery_marker (value TEXT NOT NULL);
            """)
            conn.execute("INSERT INTO recovery_marker(value) VALUES (?)", (marker,))

    @staticmethod
    def marker(path: Path) -> str:
        with closing(sqlite3.connect(path)) as conn, conn:
            return conn.execute("SELECT value FROM recovery_marker").fetchone()[0]

    def test_online_backup_and_restore_preserve_a_consistent_snapshot(self):
        backup_database(self.source, self.backup)
        self.assertEqual(self.marker(self.backup), "before-backup")
        self.assertEqual(self.backup.stat().st_mode & 0o077, 0)

        restore_database(self.backup, self.restored)
        self.assertEqual(self.marker(self.restored), "before-backup")
        self.assertEqual(self.restored.stat().st_mode & 0o077, 0)

    def test_restore_replaces_existing_database_only_when_explicit(self):
        backup_database(self.source, self.backup)
        self.create_database(self.restored, "old-target")
        with self.assertRaises(FileExistsError):
            restore_database(self.backup, self.restored)
        self.assertEqual(self.marker(self.restored), "old-target")

        restore_database(self.backup, self.restored, replace=True)
        self.assertEqual(self.marker(self.restored), "before-backup")

    def test_corrupt_backup_is_rejected_without_creating_target(self):
        corrupt = self.root / "corrupt.db"
        corrupt.write_bytes(b"not a sqlite database")
        with self.assertRaises(sqlite3.DatabaseError):
            restore_database(corrupt, self.restored)
        self.assertFalse(self.restored.exists())


if __name__ == "__main__":
    unittest.main()
