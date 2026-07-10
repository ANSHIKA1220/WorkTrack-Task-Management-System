from functools import wraps
import logging

import mysql.connector
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from config import SECRET_KEY, TASK_TITLE_OPTIONS
from db import format_created_at, format_date, get_db, task_columns

app = Flask(__name__)
app.secret_key = SECRET_KEY
logging.basicConfig(level=logging.INFO)


def normalize_role(role):
    return (role or "").strip().title()


def current_role():
    return normalize_role(session.get("role"))


def wants_json():
    return request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json"


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if wants_json():
                return jsonify({"error": "Please log in to continue."}), 401
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


def role_required(*roles):
    allowed = {normalize_role(role) for role in roles}

    def decorator(f):
        @wraps(f)
        @login_required
        def decorated(*args, **kwargs):
            if current_role() not in allowed:
                message = "You do not have permission to access this page."
                if wants_json():
                    return jsonify({"error": message}), 403
                flash(message, "error")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)

        return decorated

    return decorator


def request_data():
    return request.get_json(silent=True) or {}


def clean_name(name):
    return " ".join((name or "").strip().split()).title()


def to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 1
    return str(value).strip().lower() in {"1", "true", "yes", "completed"}


def task_select_sql(conn):
    columns = task_columns(conn)
    extra = []
    if "task_description" in columns:
        extra.append("t.task_description")
    if "due_date" in columns:
        extra.append("t.due_date")
    if "updated_at" in columns:
        extra.append("t.updated_at")
    extra_sql = ", " + ", ".join(extra) if extra else ""
    return f"""
        SELECT t.task_id, t.employee_id, e.employee_name, t.task_title, t.completed, t.created_at{extra_sql}
        FROM tasks t
        JOIN employees e ON t.employee_id = e.employee_id
        ORDER BY t.task_id DESC
    """


def format_task(row):
    row["completed"] = bool(row["completed"])
    row["created_at"] = format_created_at(row.get("created_at"))
    if "updated_at" in row:
        row["updated_at"] = format_created_at(row.get("updated_at"))
    if "due_date" in row:
        row["due_date"] = format_date(row.get("due_date"))
    row.setdefault("task_description", "")
    row.setdefault("due_date", None)
    return row


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role = normalize_role(request.form.get("role", "Manager"))

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("login.html")

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, username, password, role FROM login_table WHERE username = %s",
            (username,),
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and normalize_role(user["role"]) == role and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role"] = normalize_role(user["role"])
            flash(f"Welcome, {user['username']} ({session['role']})!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username, password, or role. Please try again.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        task_titles=TASK_TITLE_OPTIONS,
        username=session.get("username"),
        role=current_role(),
    )


@app.route("/admin/users")
@role_required("Admin")
def admin_users_page():
    flash("User Management is available from the Admin sidebar.", "info")
    return redirect(url_for("dashboard") + "#users")


@app.route("/api/me")
@login_required
def api_me():
    return jsonify(
        {
            "user_id": session.get("user_id"),
            "username": session.get("username"),
            "role": current_role(),
            "can_manage_users": current_role() == "Admin",
            "can_delete_employees": current_role() == "Admin",
            "can_delete_tasks": current_role() == "Admin",
        }
    )


@app.route("/api/users")
@role_required("Admin")
def api_users():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, username, role FROM login_table ORDER BY user_id")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    for user in users:
        user["role"] = normalize_role(user["role"])
    return jsonify(users)


@app.route("/api/employees", methods=["GET"])
@role_required("Admin", "Manager")
def api_employees():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT e.employee_id, e.employee_name,
               COUNT(t.task_id) AS task_count,
               COALESCE(SUM(CASE WHEN t.completed = 1 THEN 1 ELSE 0 END), 0) AS completed_count,
               COALESCE(SUM(CASE WHEN t.completed = 0 THEN 1 ELSE 0 END), 0) AS pending_count
        FROM employees e
        LEFT JOIN tasks t ON t.employee_id = e.employee_id
        GROUP BY e.employee_id, e.employee_name
        ORDER BY e.employee_name
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/api/employees", methods=["POST"])
@role_required("Admin", "Manager")
def api_add_employee():
    data = request_data()
    name = clean_name(data.get("employee_name"))

    if len(name) < 2:
        return jsonify({"error": "Employee name must be at least 2 characters."}), 400
    if len(name) > 100:
        return jsonify({"error": "Employee name is too long."}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT employee_id, employee_name FROM employees WHERE LOWER(employee_name) = LOWER(%s)",
            (name,),
        )
        existing = cursor.fetchone()
        if existing:
            return jsonify(
                {
                    "message": f"Employee '{existing['employee_name']}' already exists.",
                    "employee_id": existing["employee_id"],
                    "employee_name": existing["employee_name"],
                    "already_exists": True,
                }
            ), 200

        cursor.execute("INSERT INTO employees (employee_name) VALUES (%s)", (name,))
        conn.commit()
        employee_id = cursor.lastrowid
        return jsonify(
            {"message": f"Employee '{name}' added successfully.", "employee_id": employee_id, "employee_name": name}
        ), 201
    except mysql.connector.Error:
        app.logger.exception("Could not add employee")
        conn.rollback()
        return jsonify({"error": "Could not add employee. Please try again."}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/api/employees/<int:employee_id>", methods=["PUT"])
@role_required("Admin")
def api_update_employee(employee_id):
    name = clean_name(request_data().get("employee_name"))
    if len(name) < 2:
        return jsonify({"error": "Employee name must be at least 2 characters."}), 400

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE employees SET employee_name = %s WHERE employee_id = %s", (name, employee_id))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Employee not found."}), 404
        return jsonify({"message": "Employee updated successfully."})
    except mysql.connector.IntegrityError:
        conn.rollback()
        return jsonify({"error": "Another employee already has that name."}), 409
    finally:
        cursor.close()
        conn.close()


@app.route("/api/employees/<int:employee_id>", methods=["DELETE"])
@role_required("Admin")
def api_delete_employee(employee_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total FROM tasks WHERE employee_id = %s", (employee_id,))
        assigned = cursor.fetchone()["total"]
        if assigned:
            return jsonify({"error": "Employee cannot be deleted while tasks are assigned."}), 409
        cursor.execute("DELETE FROM employees WHERE employee_id = %s", (employee_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Employee not found."}), 404
        return jsonify({"message": "Employee deleted safely."})
    finally:
        cursor.close()
        conn.close()


@app.route("/api/tasks", methods=["GET"])
@role_required("Admin", "Manager")
def api_get_tasks():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(task_select_sql(conn))
    rows = [format_task(row) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/api/tasks", methods=["POST"])
@role_required("Admin", "Manager")
def api_create_task():
    data = request_data()
    employee_id = data.get("employee_id")
    task_title = (data.get("task_title") or "").strip()
    completed = to_bool(data.get("completed", False))
    description = (data.get("task_description") or "").strip()
    due_date = (data.get("due_date") or None) or None

    if not employee_id or not task_title:
        return jsonify({"error": "Employee and task type are required."}), 400
    if task_title not in TASK_TITLE_OPTIONS:
        return jsonify({"error": "Invalid task type selected."}), 400
    if len(description) > 500:
        return jsonify({"error": "Task description must be 500 characters or fewer."}), 400

    conn = get_db()
    columns = task_columns(conn)
    cursor = conn.cursor()

    fields = ["employee_id", "task_title", "completed"]
    placeholders = ["%s", "%s", "%s"]
    values = [int(employee_id), task_title, int(completed)]

    if "task_description" in columns:
        fields.append("task_description")
        placeholders.append("%s")
        values.append(description)
    if "due_date" in columns:
        fields.append("due_date")
        placeholders.append("%s")
        values.append(due_date)
    if "created_by" in columns:
        fields.append("created_by")
        placeholders.append("%s")
        values.append(session.get("user_id"))

    try:
        cursor.execute(
            f"INSERT INTO tasks ({', '.join(fields)}) VALUES ({', '.join(placeholders)})",
            tuple(values),
        )
        conn.commit()
        return jsonify({"message": "Task assigned successfully.", "task_id": cursor.lastrowid}), 201
    except (ValueError, mysql.connector.Error):
        app.logger.exception("Could not create task")
        conn.rollback()
        return jsonify({"error": "Could not assign task. Check the employee and due date."}), 400
    finally:
        cursor.close()
        conn.close()


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
@role_required("Admin", "Manager")
def api_update_task(task_id):
    data = request_data()
    conn = get_db()
    columns = task_columns(conn)
    cursor = conn.cursor()

    if current_role() == "Manager":
        cursor.execute("UPDATE tasks SET completed = %s WHERE task_id = %s", (int(to_bool(data.get("completed"))), task_id))
    else:
        employee_id = data.get("employee_id")
        task_title = (data.get("task_title") or "").strip()
        completed = to_bool(data.get("completed", False))
        description = (data.get("task_description") or "").strip()
        due_date = (data.get("due_date") or None) or None

        if not employee_id or not task_title:
            cursor.close()
            conn.close()
            return jsonify({"error": "Employee and task type are required."}), 400
        if task_title not in TASK_TITLE_OPTIONS:
            cursor.close()
            conn.close()
            return jsonify({"error": "Invalid task type selected."}), 400

        fields = ["employee_id = %s", "task_title = %s", "completed = %s"]
        values = [int(employee_id), task_title, int(completed)]
        if "task_description" in columns:
            fields.append("task_description = %s")
            values.append(description)
        if "due_date" in columns:
            fields.append("due_date = %s")
            values.append(due_date)
        values.append(task_id)
        cursor.execute(f"UPDATE tasks SET {', '.join(fields)} WHERE task_id = %s", tuple(values))

    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()

    if affected == 0:
        return jsonify({"error": "Task not found."}), 404
    return jsonify({"message": "Task updated successfully."})


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@role_required("Admin")
def api_delete_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()

    if affected == 0:
        return jsonify({"error": "Task not found."}), 404
    return jsonify({"message": "Task deleted successfully."})


@app.route("/api/reports")
@role_required("Admin", "Manager")
def api_reports():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_tasks,
            COALESCE(SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END), 0) AS completed_tasks,
            COALESCE(SUM(CASE WHEN completed = 0 THEN 1 ELSE 0 END), 0) AS pending_tasks
        FROM tasks
        """
    )
    totals = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) AS total_employees FROM employees")
    total_employees = cursor.fetchone()["total_employees"]
    cursor.execute("SELECT COUNT(*) AS total_users FROM login_table")
    total_users = cursor.fetchone()["total_users"]
    cursor.execute(
        """
        SELECT task_title,
               COUNT(*) AS total,
               COALESCE(SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END), 0) AS completed,
               COALESCE(SUM(CASE WHEN completed = 0 THEN 1 ELSE 0 END), 0) AS pending
        FROM tasks
        GROUP BY task_title
        ORDER BY total DESC, task_title
        """
    )
    by_type = cursor.fetchall()
    cursor.execute(
        """
        SELECT e.employee_id, e.employee_name,
               COUNT(t.task_id) AS total,
               COALESCE(SUM(CASE WHEN t.completed = 1 THEN 1 ELSE 0 END), 0) AS completed,
               COALESCE(SUM(CASE WHEN t.completed = 0 THEN 1 ELSE 0 END), 0) AS pending
        FROM employees e
        LEFT JOIN tasks t ON t.employee_id = e.employee_id
        GROUP BY e.employee_id, e.employee_name
        HAVING total > 0
        ORDER BY total DESC, e.employee_name
        LIMIT 8
        """
    )
    workload = cursor.fetchall()
    cursor.close()
    conn.close()

    total_tasks = int(totals["total_tasks"] or 0)
    completed_tasks = int(totals["completed_tasks"] or 0)
    pending_tasks = int(totals["pending_tasks"] or 0)
    return jsonify(
        {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": round((completed_tasks / total_tasks) * 100) if total_tasks else 0,
            "total_employees": int(total_employees or 0),
            "total_users": int(total_users or 0),
            "avg_tasks_per_employee": round(total_tasks / total_employees, 1) if total_employees else 0,
            "by_type": by_type,
            "workload": workload,
        }
    )


if __name__ == "__main__":
    print("Starting WorkTrack (MySQL)")
    print("Open http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
