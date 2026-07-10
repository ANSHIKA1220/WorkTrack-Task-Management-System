# WorkTrack - Task Management System

WorkTrack is a Flask + MySQL web application for assigning employee tasks, tracking completion, and viewing role-based reports.

Tagline: **Assign. Track. Complete.**

## Technology Stack

| Layer | Technology |
| --- | --- |
| Backend | Python, Flask |
| Database | MySQL / MariaDB |
| Frontend | HTML, CSS, JavaScript |
| Auth | Flask sessions, Werkzeug password hashing |

## Features

- Session-based login for Admin and Manager users
- Role-based backend authorization
- Employee directory with search and workload counts
- Task assignment with status, description, and due date
- Task filters by search, status, type, and employee
- Reports from MySQL data: totals, completion rate, task type summary, workload
- Safe seed script for realistic demo data

## Admin vs Manager

Admin users can:

- View organization-wide dashboard metrics
- View, add, edit, and safely delete employees
- View, assign, edit, update, and delete tasks
- View reports and analytics
- View application users

Manager users can:

- View manager dashboard metrics
- View employees
- Add employees
- Assign tasks
- View tasks and update task status
- View reports

Manager users cannot delete employees, delete tasks, view application users, or access admin-only routes.

## Database Relationship

The database uses three main tables:

- `login_table`: application users and roles
- `employees`: employee directory
- `tasks`: task assignments

`tasks.employee_id` is a foreign key that references `employees.employee_id`.

## Environment Variables

Copy `.env.example` to `.env`:

```powershell
copy .env.example .env
```

Example `.env`:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=task_management
SECRET_KEY=change-this-for-production
```

Do not commit `.env`.

## Installation

```powershell
cd D:\projects\task-management-system-main
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` with your MySQL password.

## Database Setup

Start MySQL, then run:

```powershell
python setup_db.py
```

This creates the database, tables, default users, and the A-Z employee directory.

Apply migrations any time with:

```powershell
python migrate.py
```

## Seed Realistic Demo Data

Run:

```powershell
python seed_data.py
```

The seed script is safe to run more than once. It avoids duplicate employees and duplicate seeded tasks.

To remove only seeded demo tasks, run:

```powershell
python reset_demo_data.py
```

You must type `DELETE` when prompted. Employees are not deleted.

## Run the Application

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Demo Credentials

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `admin123` |
| Manager | `manager` | `manager123` |

## Folder Structure

```text
app.py                  Flask routes, auth, APIs
config.py               Environment and app configuration
db.py                   MySQL connection helpers
setup_db.py             Initial database setup
migrate.py              Safe schema migrations
seed_data.py            Realistic demo data
reset_demo_data.py      Explicit demo cleanup
database/schema.sql     Base schema
templates/              Jinja HTML templates
static/css/style.css    WorkTrack UI styles
static/js/app.js        Frontend behavior
tests/                  Small unittest suite
```

## Screenshots

Add screenshots here after running the app:

- Login page
- Admin dashboard
- Manager dashboard
- Employees page
- Reports page

## Tests

Run:

```powershell
python -m unittest
```
