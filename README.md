# WorkTrack - Task Management System

**A full-stack web application for assigning employee tasks, tracking completion status, and viewing role-based productivity reports.**

| | |
|---|---|
| **Course** | MP Online Internship - Software Development |
| **Batch** | 10B |
| **Application No.** | IN26012584 |
| **Project Type** | Internship Project Submission |
| **Author** | Anshika Shrivastava ([@ANSHIKA1220](https://github.com/ANSHIKA1220)) |
| **Repository** | [WorkTrack-Task-Management-System](https://github.com/ANSHIKA1220/WorkTrack-Task-Management-System) |
| **Technologies** | HTML, CSS, JavaScript, Python (Flask), MySQL |

---

## Abstract

WorkTrack is a browser-based **Task Management System** developed for the **MP Online Internship - Software Development Course (Batch 10B)**. The application allows Admin and Manager users to maintain an employee directory, assign tasks, update task completion status, and view reports generated from live MySQL data.

The system uses Flask for backend routing and session handling, MySQL for persistent storage, Jinja templates for rendering pages, and plain JavaScript for dashboard interactivity. It includes role-based access control so that Admin and Manager users receive different permissions while sharing the same application interface.

---

## Problem Statement

Manual task assignment through spreadsheets, chat messages, or paper records becomes difficult to manage as teams grow. Common issues include:

- No centralized place to view assigned work
- Difficulty tracking pending and completed tasks
- Limited visibility into employee workload
- No clear separation between Admin and Manager permissions
- Reports requiring manual counting or spreadsheet formulas

WorkTrack solves these problems by providing a structured web application where tasks, employees, user roles, and reports are managed through a MySQL-backed system.

---

## Objectives

- Provide secure login for Admin and Manager users
- Maintain employee records in a searchable directory
- Assign tasks to employees with task type, status, optional description, and optional due date
- Display dashboard counters for total, pending, completed, and completion rate
- Generate reports from actual MySQL records
- Enforce backend role-based access control
- Provide realistic seed data for demonstration
- Keep the user interface responsive and suitable for a college project presentation

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript | Login page, dashboard panels, forms, filters, and dynamic table rendering |
| **Backend** | Python, Flask | Routing, sessions, role checks, REST API endpoints, and business logic |
| **Database** | MySQL / MariaDB | Stores users, employees, and task assignments |
| **Templating** | Jinja2 | Server-rendered login and dashboard pages |
| **Security** | Werkzeug | Password hashing and password verification |
| **Configuration** | `.env` file | Local MySQL and secret key settings |

---

## System Architecture

```text
+-----------------------------+
|           Browser           |
|  HTML, CSS, JavaScript UI   |
+--------------+--------------+
               |
               | HTTP / JSON
               v
+-----------------------------+
|        Flask Application    |
| app.py routes, sessions,    |
| role checks, REST APIs      |
+--------------+--------------+
               |
               | mysql-connector-python
               v
+-----------------------------+
|          MySQL Database     |
| login_table, employees,     |
| tasks                       |
+-----------------------------+
```

---

## Database Design

WorkTrack uses three primary tables. Tasks are connected to employees using a foreign key relationship.

```text
login_table
  user_id (PK)
  username
  password
  role

employees
  employee_id (PK)
  employee_name

tasks
  task_id (PK)
  employee_id (FK -> employees.employee_id)
  task_title
  task_description
  completed
  due_date
  created_at
  created_by
  updated_at
```

| Table | Description |
|---|---|
| `login_table` | Stores Admin and Manager login accounts with hashed passwords |
| `employees` | Stores employee names used for task assignment |
| `tasks` | Stores assigned tasks, completion status, optional due dates, and task metadata |

The task schema is extended safely through `migrate.py`, which checks existing columns and indexes before applying changes.

---

## Features

### Authentication

- Login page with username, password, and role selection
- Password show/hide toggle on the login form
- Flask session-based authentication
- Hashed password verification using Werkzeug
- Logout route that clears the active session
- Unauthenticated dashboard access redirects to the login page

### Employee Management

- Searchable employee directory
- Add employee form
- Employee initials/avatar display
- Workload counts per employee:
  - Total assigned tasks
  - Completed tasks
  - Pending tasks
- Admin-only employee editing
- Admin-only employee deletion
- Employee deletion is blocked when tasks are already assigned
- Duplicate employee names are handled safely

### Task Management

- Assign tasks to selected employees
- Task ID is generated automatically by MySQL
- Supported task fields:
  - Employee
  - Task type
  - Optional task description
  - Optional due date
  - Pending or Completed status
- Task list with filters:
  - Search text
  - Status
  - Task type
  - Employee
- Admin users can edit full task details
- Admin users can delete tasks
- Manager users can update task status

### Reports & Analytics

Reports are calculated from MySQL records through `/api/reports`.

The reports section includes:

- Total tasks
- Pending tasks
- Completed tasks
- Completion rate
- Average tasks per employee
- Task type breakdown
- Employee workload summary

### Role-based Access Control

The backend uses reusable decorators:

- `login_required`
- `role_required("Admin")`
- `role_required("Admin", "Manager")`

Admin users can:

- View dashboard metrics
- View, add, edit, and safely delete employees
- View, assign, edit, update, and delete tasks
- View reports
- View application users

Manager users can:

- View dashboard metrics
- View employees
- Add employees
- Assign tasks
- View task lists
- Update task status
- View reports

Manager users cannot:

- Delete employees
- Delete tasks
- Edit full task details
- View application users
- Access Admin-only API routes

If a Manager accesses an Admin-only API route, the server returns a permission error. If they access the Admin-only page route, they are redirected back to the dashboard with a clear flash message.

---

## REST API Endpoints

All API endpoints require an authenticated session unless otherwise noted.

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/me` | Admin, Manager | Returns current session user and permission flags |
| `GET` | `/api/users` | Admin | Lists application users |
| `GET` | `/api/employees` | Admin, Manager | Lists employees with workload counts |
| `POST` | `/api/employees` | Admin, Manager | Adds a new employee |
| `PUT` | `/api/employees/<employee_id>` | Admin | Updates an employee name |
| `DELETE` | `/api/employees/<employee_id>` | Admin | Deletes an employee only if no tasks are assigned |
| `GET` | `/api/tasks` | Admin, Manager | Lists tasks with employee details |
| `POST` | `/api/tasks` | Admin, Manager | Creates a new task |
| `PUT` | `/api/tasks/<task_id>` | Admin, Manager | Admin updates task details; Manager updates status |
| `DELETE` | `/api/tasks/<task_id>` | Admin | Deletes a task |
| `GET` | `/api/reports` | Admin, Manager | Returns task totals, completion rate, type summary, and workload data |

Page routes:

| Route | Description |
|---|---|
| `/` | Redirects to dashboard when logged in, otherwise login |
| `/login` | Login page and login form handler |
| `/dashboard` | Main WorkTrack dashboard |
| `/admin/users` | Admin-only redirect to User Management panel |
| `/logout` | Clears session and redirects to login |

---

## Prerequisites

Install the following before running the project:

| Software | Recommended Version | Notes |
|---|---|---|
| Python | 3.10+ | Required for Flask backend |
| MySQL / MariaDB | MySQL 8+ or MariaDB equivalent | Required database server |
| pip | Latest available | Installs Python dependencies |
| Browser | Chrome, Edge, Firefox, etc. | Opens the web application |

---

## Installation & Setup

Clone the repository:

```powershell
git clone https://github.com/ANSHIKA1220/WorkTrack-Task-Management-System.git
cd WorkTrack-Task-Management-System
```

Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Copy the environment example file:

```powershell
copy .env.example .env
```

Update `.env` with your local MySQL settings:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=task_management
SECRET_KEY=change-this-for-production
```

---

## Database Initialization

Make sure MySQL is running, then initialize the database:

```powershell
python setup_db.py
```

This command:

- Creates the database if it does not exist
- Creates required tables from `database/schema.sql`
- Applies safe migrations through `migrate.py`
- Creates default Admin and Manager users
- Seeds the employee directory from `database/employee_names.py`

Apply migrations manually when needed:

```powershell
python migrate.py
```

Add realistic demo data:

```powershell
python seed_data.py
```

The seed script is safe to run multiple times. It avoids duplicate demo employees and duplicate seeded tasks.

Optional demo cleanup:

```powershell
python reset_demo_data.py
```

This removes only seeded demo tasks after confirmation. It does not delete employees or reset the full database.

---

## Running the Project

Start the Flask development server:

```powershell
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

Stop the server with:

```text
Ctrl + C
```

---

## Demo Credentials

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Manager | `manager` | `manager123` |

---

## Screenshots

## Login Page

(Add Screenshot Here)

## Dashboard

(Add Screenshot Here)

## Employee Directory

(Add Screenshot Here)

## Reports

(Add Screenshot Here)

## Task Assignment

(Add Screenshot Here)

---

## Project Structure

```text
WorkTrack-Task-Management-System/
|
|-- app.py
|-- config.py
|-- db.py
|-- setup_db.py
|-- migrate.py
|-- seed_data.py
|-- reset_demo_data.py
|-- check_db.py
|-- requirements.txt
|-- .env.example
|-- README.md
|
|-- database/
|   |-- schema.sql
|   |-- employee_names.py
|   |-- __init__.py
|
|-- migrations/
|   |-- 001_improve_task_schema.sql
|
|-- templates/
|   |-- login.html
|   |-- dashboard.html
|
|-- static/
|   |-- css/
|   |   |-- style.css
|   |-- js/
|   |   |-- app.js
|   |-- images/
|
|-- tests/
|   |-- test_auth.py
```

---

## How It Works

1. A user opens the application and is redirected to `/login`.
2. The user enters username, password, and role.
3. Flask checks the user record in `login_table`.
4. Werkzeug verifies the hashed password.
5. On successful login, Flask stores `user_id`, `username`, and `role` in the session.
6. The dashboard loads with role-specific sidebar items.
7. JavaScript requests employees, tasks, reports, and Admin-only user data through REST APIs.
8. Employees are loaded from the `employees` table with task counts.
9. Tasks are loaded from the `tasks` table and joined with employee names.
10. Dashboard counters and reports are calculated from live MySQL data.
11. Admin-only actions are protected by backend role checks.
12. Logout clears the session and returns the user to the login page.

---

## Testing

A small unittest suite is included for authentication and role behavior.

Run:

```powershell
python -m unittest discover -s tests
```

The tests cover:

- Dashboard login protection
- Manager restriction from Admin user API
- Admin-only page blocking for Manager role
- Task creation validation before database insertion

---

## Future Enhancements

- Employee self-login to view assigned tasks
- Task priority levels
- Task comments or activity history
- More advanced user management
- Export reports to PDF or Excel
- Email notification on task assignment
- Date range filters for reports
- Dark mode option

---

## References

- Flask Documentation - https://flask.palletsprojects.com/
- MySQL Documentation - https://dev.mysql.com/doc/
- Werkzeug Security Helpers - https://werkzeug.palletsprojects.com/
- MDN Web Docs - https://developer.mozilla.org/

---

## License

This project was developed as part of the **MP Online Internship - Software Development Course, Batch 10B**. It is intended for educational and academic project submission use.

---

<p align="center">
  <strong>WorkTrack - Task Management System</strong><br>
  <sub>MP Online Internship - Software Development - Batch 10B</sub><br>
  <sub>Application No. IN26012584 - Anshika Shrivastava - <a href="https://github.com/ANSHIKA1220">@ANSHIKA1220</a></sub>
</p>
