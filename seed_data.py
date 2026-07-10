"""Seed realistic WorkTrack demo data without duplicating rows."""

from datetime import date, timedelta

from config import DB_CONFIG
from db import get_db, task_columns
from migrate import migrate


EMPLOYEES = [
    "Aanya Patel",
    "Aarav Sharma",
    "Diya Mehta",
    "Rohan Verma",
    "Kavya Singh",
    "Arjun Nair",
    "Meera Iyer",
    "Vivaan Gupta",
    "Sara Khan",
    "Aditya Rao",
    "Neha Joshi",
    "Rahul Das",
]

TASKS = [
    ("Aanya Patel", "Documentation", "Prepare onboarding checklist", True, -8),
    ("Aarav Sharma", "Bug Fix", "Resolve login validation message issue", False, 2),
    ("Diya Mehta", "Testing", "Run regression testing for dashboard", True, -3),
    ("Rohan Verma", "Development", "Build task filters for manager view", False, 5),
    ("Kavya Singh", "Code Review", "Review employee API changes", True, -1),
    ("Arjun Nair", "Database Update", "Add optional due date support", False, 4),
    ("Meera Iyer", "Client Follow-up", "Confirm weekly report format", False, 1),
    ("Vivaan Gupta", "UI Design", "Polish mobile sidebar layout", True, -2),
    ("Sara Khan", "Documentation", "Update project setup notes", False, 6),
    ("Aditya Rao", "Testing", "Verify manager permissions", True, -4),
    ("Neha Joshi", "Development", "Improve employee workload summary", False, 3),
    ("Rahul Das", "Bug Fix", "Handle duplicate employee names", True, -5),
    ("Aanya Patel", "Client Follow-up", "Collect feedback on reports", False, 7),
    ("Diya Mehta", "Code Review", "Check seed script idempotency", True, -1),
    ("Kavya Singh", "UI Design", "Refine status badges", False, 2),
    ("Arjun Nair", "Database Update", "Validate migration script", True, -6),
    ("Meera Iyer", "Documentation", "Prepare viva feature list", False, 8),
    ("Vivaan Gupta", "Testing", "Test responsive employee table", True, -2),
]


def ensure_employee(cursor, name):
    cursor.execute("SELECT employee_id FROM employees WHERE LOWER(employee_name) = LOWER(%s)", (name,))
    row = cursor.fetchone()
    if row:
        return row[0], False
    cursor.execute("INSERT INTO employees (employee_name) VALUES (%s)", (name,))
    return cursor.lastrowid, True


def task_exists(cursor, employee_id, task_title, description):
    cursor.execute(
        """
        SELECT task_id FROM tasks
        WHERE employee_id = %s AND task_title = %s AND COALESCE(task_description, '') = %s
        LIMIT 1
        """,
        (employee_id, task_title, description),
    )
    return cursor.fetchone() is not None


def seed():
    migrate()
    conn = get_db()
    cursor = conn.cursor()
    columns = task_columns(conn)
    added_employees = 0
    added_tasks = 0
    employee_ids = {}

    for name in EMPLOYEES:
        employee_id, added = ensure_employee(cursor, name)
        employee_ids[name] = employee_id
        added_employees += int(added)

    today = date.today()
    for employee_name, task_title, description, completed, offset in TASKS:
        employee_id = employee_ids[employee_name]
        if task_exists(cursor, employee_id, task_title, description):
            continue

        fields = ["employee_id", "task_title", "completed"]
        placeholders = ["%s", "%s", "%s"]
        values = [employee_id, task_title, int(completed)]

        if "task_description" in columns:
            fields.append("task_description")
            placeholders.append("%s")
            values.append(description)
        if "due_date" in columns:
            fields.append("due_date")
            placeholders.append("%s")
            values.append(today + timedelta(days=offset))

        cursor.execute(
            f"INSERT INTO tasks ({', '.join(fields)}) VALUES ({', '.join(placeholders)})",
            tuple(values),
        )
        added_tasks += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Seed complete for {DB_CONFIG['database']}: {added_employees} employees added, {added_tasks} tasks added.")


if __name__ == "__main__":
    seed()
