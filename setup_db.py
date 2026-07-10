"""Initialize MySQL database with schema and default users."""

import sys

import mysql.connector
from werkzeug.security import generate_password_hash

from config import DB_CONFIG
from database.employee_names import generate_alphabet_names

USERS = [
    ("admin", "admin123", "Admin"),
    ("manager", "manager123", "Manager"),
]


def seed_employees(cursor):
    names = generate_alphabet_names()
    added = 0

    for name in names:
        cursor.execute("SELECT employee_id FROM employees WHERE employee_name = %s", (name,))
        if cursor.fetchone():
            continue
        cursor.execute("INSERT INTO employees (employee_name) VALUES (%s)", (name,))
        added += 1

    cursor.execute("SELECT COUNT(*) FROM employees")
    total = cursor.fetchone()[0]
    print(f"  Employees: {total} in directory ({added} new names added, A–Z covered).")
    return total


def setup():
    print("Connecting to MySQL...")
    print(f"  Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"  User: {DB_CONFIG['user']}")
    print(f"  Database: {DB_CONFIG['database']}")

    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
    except mysql.connector.Error as exc:
        errno = getattr(exc, "errno", None)
        print("\nERROR: Could not connect to MySQL.\n")
        if errno == 1045:
            print("MySQL is running, but the username/password is wrong.")
            print(f"  User tried: {DB_CONFIG['user']} (password {'set' if DB_CONFIG['password'] else 'empty'})")
            print("\nFix:")
            print(f"  1. Copy .env.example to .env in this folder")
            print(f"  2. Set MYSQL_PASSWORD=your_mysql_password")
            print(f"  3. Run again: python setup_db.py")
            print("\nIf you use XAMPP and never set a password, try opening phpMyAdmin")
            print("and check what password works for user 'root'.")
        elif errno == 2003:
            print("Fix it with these steps:")
            print("  1. Open XAMPP Control Panel (C:\\Users\\yashp\\Documents\\SQL)")
            print("  2. Click 'Start' next to MySQL")
            print("  3. Run this command again: python setup_db.py")
        else:
            print("Check MySQL is running and your .env settings are correct.")
        print(f"\nDetails: {exc}")
        sys.exit(1)

    cursor = conn.cursor()

    with open("database/schema.sql", encoding="utf-8") as f:
        for statement in f.read().split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt)

    conn.commit()
    conn.database = DB_CONFIG["database"]
    cursor = conn.cursor()

    for username, plain, role in USERS:
        cursor.execute(
            """
            INSERT INTO login_table (username, password, role)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE password = VALUES(password), role = VALUES(role)
            """,
            (username, generate_password_hash(plain), role),
        )

    seed_employees(cursor)

    conn.commit()
    cursor.close()
    conn.close()

    print("\nMySQL database setup complete.")
    print("Login: admin / admin123  OR  manager / manager123")
    print("\nNext step: python app.py")


if __name__ == "__main__":
    setup()
