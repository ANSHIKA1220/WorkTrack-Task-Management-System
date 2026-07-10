"""MySQL database connection."""

from datetime import datetime

import mysql.connector

from config import DB_CONFIG, ENV_FILE


def get_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as exc:
        errno = getattr(exc, "errno", None)
        if errno == 1045:
            raise mysql.connector.Error(
                f"MySQL access denied for user '{DB_CONFIG['user']}'@'{DB_CONFIG['host']}'. "
                f"Your MySQL root user requires a password.\n\n"
                f"Fix:\n"
                f"  1. Create a file: {ENV_FILE}\n"
                f"  2. Add this line (use your MySQL password):\n"
                f"       MYSQL_PASSWORD=your_password_here\n"
                f"  3. Restart: python app.py\n\n"
                f"XAMPP tip: open phpMyAdmin — if root has no password, leave MYSQL_PASSWORD empty.\n"
                f"If you set a password in phpMyAdmin, use that same value.\n\n"
                f"Original error: {exc}"
            ) from exc
        if errno == 2003:
            raise mysql.connector.Error(
                f"Cannot connect to MySQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}. "
                f"Start MySQL in XAMPP Control Panel, then run: python setup_db.py\n"
                f"Original error: {exc}"
            ) from exc
        raise mysql.connector.Error(
            f"MySQL connection failed ({DB_CONFIG['host']}:{DB_CONFIG['port']}). "
            f"Check .env settings and that MySQL is running.\n"
            f"Original error: {exc}"
        ) from exc


def format_created_at(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value)[:16]


def renumber_tasks(conn):
    """Reassign task_id 1..n in ascending order after a delete."""
    cursor = conn.cursor()
    cursor.execute("SELECT task_id FROM tasks ORDER BY task_id ASC")
    ids = [row[0] for row in cursor.fetchall()]

    if not ids:
        cursor.execute("ALTER TABLE tasks AUTO_INCREMENT = 1")
        conn.commit()
        cursor.close()
        return

    offset = max(ids) + 1000
    cursor.execute("UPDATE tasks SET task_id = task_id + %s", (offset,))

    for new_id, old_id in enumerate(ids, start=1):
        cursor.execute(
            "UPDATE tasks SET task_id = %s WHERE task_id = %s",
            (new_id, old_id + offset),
        )

    cursor.execute("ALTER TABLE tasks AUTO_INCREMENT = %s", (len(ids) + 1,))
    conn.commit()
    cursor.close()


def ensure_sequential_task_ids(conn):
    """Renumber only when gaps exist (e.g. after a delete before this fix)."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(MAX(task_id), 0) FROM tasks")
    max_id = cursor.fetchone()[0]
    cursor.close()
    if count and max_id != count:
        renumber_tasks(conn)
