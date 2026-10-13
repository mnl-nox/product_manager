from __future__ import annotations

import unittest

from api import app


class HumanResourcesSchemaTests(unittest.TestCase):
    def setUp(self):
        with app.get_db() as conn:
            conn.execute("DELETE FROM hr_work_time")
            conn.execute("DELETE FROM hr_documents")
            conn.execute("DELETE FROM hr_absences")
            conn.execute("DELETE FROM hr_employees")
            conn.execute("DELETE FROM hr_departments")
            conn.execute(
                "INSERT OR IGNORE INTO app_users (username, password_hash, role) VALUES (?, ?, ?)",
                ("hr-test-admin", "test-hash", "admin"),
            )
            self.user_id = conn.execute("SELECT id FROM app_users WHERE username='hr-test-admin'").fetchone()[0]
            self.department_id = conn.execute(
                "INSERT INTO hr_departments (name) VALUES ('Test Department')"
            ).lastrowid
            self.employee_id = conn.execute(
                """INSERT INTO hr_employees
                   (employee_code, full_name, job_title, department_id, hire_date, created_by)
                   VALUES ('HR-TEST-1', 'Test Employee', 'Analyst', ?, '2026-01-01', ?)""",
                (self.department_id, self.user_id),
            ).lastrowid

    def test_hr_tables_exist(self):
        expected = {"hr_departments", "hr_employees", "hr_absences", "hr_documents", "hr_work_time"}
        with app.get_db() as conn:
            found = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue(expected.issubset(found))

    def test_employee_code_is_unique(self):
        with app.get_db() as conn:
            with self.assertRaises(Exception):
                conn.execute(
                    """INSERT INTO hr_employees
                       (employee_code, full_name, job_title, hire_date)
                       VALUES ('HR-TEST-1', 'Duplicate', 'Analyst', '2026-01-02')"""
                )

    def test_absence_end_date_cannot_precede_start_date(self):
        with app.get_db() as conn:
            with self.assertRaises(Exception):
                conn.execute(
                    """INSERT INTO hr_absences (employee_id, absence_type, start_date, end_date)
                       VALUES (?, 'vacation', '2026-05-10', '2026-05-01')""",
                    (self.employee_id,),
                )

    def test_work_time_has_one_record_per_employee_and_day(self):
        with app.get_db() as conn:
            conn.execute(
                "INSERT INTO hr_work_time (employee_id, work_date, minutes_worked) VALUES (?, '2026-02-01', 480)",
                (self.employee_id,),
            )
            with self.assertRaises(Exception):
                conn.execute(
                    "INSERT INTO hr_work_time (employee_id, work_date, minutes_worked) VALUES (?, '2026-02-01', 450)",
                    (self.employee_id,),
                )


if __name__ == "__main__":
    unittest.main()
