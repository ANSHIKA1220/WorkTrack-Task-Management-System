import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


def load_env_file():
    """Load KEY=VALUE pairs from .env into os.environ (does not override existing vars)."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file()

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "task_management"),
}

SECRET_KEY = os.environ.get("SECRET_KEY", "worktrack-dev-secret-change-me")

TASK_TITLE_OPTIONS = [
    "Documentation",
    "Code Review",
    "Bug Fix",
    "Development",
    "Feature Development",
    "Testing",
    "Database Update",
    "Client Follow-up",
    "UI Design",
    "Training",
    "Deployment",
]
