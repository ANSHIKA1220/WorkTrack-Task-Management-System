"""Apply safe, repeatable database migrations for WorkTrack."""

import mysql.connector

from config import DB_CONFIG


TASK_COLUMNS = {
    "task_description": "ALTER TABLE tasks ADD COLUMN task_description VARCHAR(500) NULL AFTER task_title",
    "due_date": "ALTER TABLE tasks ADD COLUMN due_date DATE NULL AFTER completed",
    "created_by": "ALTER TABLE tasks ADD COLUMN created_by INT NULL AFTER created_at",
    "updated_at": "ALTER TABLE tasks ADD COLUMN updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP AFTER created_by",
}

TASK_INDEXES = {
    "idx_tasks_employee_id": "CREATE INDEX idx_tasks_employee_id ON tasks (employee_id)",
    "idx_tasks_completed": "CREATE INDEX idx_tasks_completed ON tasks (completed)",
    "idx_tasks_due_date": "CREATE INDEX idx_tasks_due_date ON tasks (due_date)",
}


def existing_columns(cursor):
    cursor.execute("SHOW COLUMNS FROM tasks")
    return {row[0] for row in cursor.fetchall()}


def existing_indexes(cursor):
    cursor.execute("SHOW INDEX FROM tasks")
    return {row[2] for row in cursor.fetchall()}


def migrate():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    columns = existing_columns(cursor)
    for name, statement in TASK_COLUMNS.items():
        if name not in columns:
            print(f"Adding tasks.{name}")
            cursor.execute(statement)

    indexes = existing_indexes(cursor)
    for name, statement in TASK_INDEXES.items():
        if name not in indexes:
            print(f"Adding index {name}")
            cursor.execute(statement)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database migrations complete.")


if __name__ == "__main__":
    migrate()
