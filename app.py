from functools import wraps

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
from db import ensure_sequential_task_ids, format_created_at, get_db, renumber_tasks

app = Flask(__name__)
app.secret_key = SECRET_KEY


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


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
        role = request.form.get("role", "Manager")

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT user_id, username, password, role FROM login_table WHERE username = %s AND role = %s",
            (username, role),
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash(f"Welcome, {user['username']} ({user['role']})!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid credentials. Please try again.", "error")

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
        role=session.get("role"),
    )


@app.route("/api/employees", methods=["GET"])
@login_required
def api_employees():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT employee_id, employee_name FROM employees ORDER BY employee_name")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/api/employees", methods=["POST"])
@login_required
def api_add_employee():
    data = request.get_json()
    name = (data.get("employee_name") or "").strip()

    if len(name) < 2:
        return jsonify({"error": "Employee name must be at least 2 characters."}), 400
    if len(name) > 100:
        return jsonify({"error": "Employee name is too long."}), 400

    name = " ".join(word.capitalize() for word in name.split())

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT employee_id, employee_name FROM employees WHERE LOWER(employee_name) = LOWER(%s)",
        (name,),
    )
    existing = cursor.fetchone()
    if existing:
        cursor.close()
        conn.close()
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
    cursor.close()
    conn.close()

    return jsonify(
        {"message": f"Employee '{name}' added successfully.", "employee_id": employee_id, "employee_name": name}
    ), 201


@app.route("/api/tasks", methods=["GET"])
@login_required
def api_get_tasks():
    conn = get_db()
    ensure_sequential_task_ids(conn)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT t.task_id, t.employee_id, e.employee_name, t.task_title, t.completed, t.created_at
        FROM tasks t
        JOIN employees e ON t.employee_id = e.employee_id
        ORDER BY t.task_id ASC
        """
    )
    rows = cursor.fetchall()
    for row in rows:
        row["completed"] = bool(row["completed"])
        row["created_at"] = format_created_at(row.get("created_at"))
    cursor.close()
    conn.close()
    return jsonify(rows)


@app.route("/api/tasks", methods=["POST"])
@login_required
def api_create_task():
    data = request.get_json()
    employee_id = data.get("employee_id")
    task_title = data.get("task_title")
    completed = data.get("completed", False)

    if not employee_id or not task_title:
        return jsonify({"error": "Employee and Task Title are required."}), 400

    if task_title not in TASK_TITLE_OPTIONS:
        return jsonify({"error": "Invalid task title selected."}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (employee_id, task_title, completed) VALUES (%s, %s, %s)",
        (int(employee_id), task_title, int(bool(completed))),
    )
    conn.commit()
    task_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"message": "Task submitted successfully!", "task_id": task_id}), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
@login_required
def api_update_task(task_id):
    data = request.get_json()
    employee_id = data.get("employee_id")
    task_title = data.get("task_title")
    completed = data.get("completed", False)

    if not employee_id or not task_title:
        return jsonify({"error": "Employee and Task Title are required."}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE tasks SET employee_id = %s, task_title = %s, completed = %s
        WHERE task_id = %s
        """,
        (int(employee_id), task_title, int(bool(completed)), task_id),
    )
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()

    if affected == 0:
        return jsonify({"error": "Task not found."}), 404
    return jsonify({"message": "Task updated successfully!"})


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def api_delete_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE task_id = %s", (task_id,))
    conn.commit()
    affected = cursor.rowcount
    cursor.close()

    if affected == 0:
        conn.close()
        return jsonify({"error": "Task not found."}), 404

    renumber_tasks(conn)
    conn.close()
    return jsonify({"message": "Task removed. IDs reordered."})


if __name__ == "__main__":
    print("Starting Task Management System (MySQL)")
    print("Open http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
