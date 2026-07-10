"""Test MySQL connection using settings from .env / config.py."""

import sys

import mysql.connector

from config import DB_CONFIG, ENV_FILE


def main():
    print("MySQL connection check")
    print(f"  Config file: {ENV_FILE} ({'found' if ENV_FILE.exists() else 'missing — copy .env.example to .env'})")
    print(f"  Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"  User: {DB_CONFIG['user']}")
    print(f"  Password: {'(set)' if DB_CONFIG['password'] else '(empty)'}")
    print(f"  Database: {DB_CONFIG['database']}")
    print()

    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
        conn.close()
        print("SUCCESS — MySQL connection works.")
        print("Next: python setup_db.py  then  python app.py")
        return 0
    except mysql.connector.Error as exc:
        print(f"FAILED — {exc}")
        if getattr(exc, "errno", None) == 1045:
            print("\nCreate .env with your MySQL password, e.g.:")
            print("  MYSQL_PASSWORD=your_password_here")
        return 1


if __name__ == "__main__":
    sys.exit(main())
