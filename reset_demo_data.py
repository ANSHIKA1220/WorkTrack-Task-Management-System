"""Explicit cleanup for WorkTrack demo tasks only.

This script removes tasks whose descriptions match seed_data.py. It does not
delete employees or reset your whole database.
"""

from db import get_db
from seed_data import TASKS


def reset_demo_tasks():
    descriptions = [task[2] for task in TASKS]
    conn = get_db()
    cursor = conn.cursor()
    deleted = 0
    for description in descriptions:
        cursor.execute("DELETE FROM tasks WHERE task_description = %s", (description,))
        deleted += cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Removed {deleted} seeded demo tasks. Employees were left untouched.")


if __name__ == "__main__":
    answer = input("Delete only WorkTrack seeded demo tasks? Type DELETE to continue: ")
    if answer == "DELETE":
        reset_demo_tasks()
    else:
        print("Cancelled.")
