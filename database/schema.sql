-- Task Management System - MySQL Schema
-- Run: mysql -u root -p < database/schema.sql

CREATE DATABASE IF NOT EXISTS task_management;
USE task_management;

-- Login table for Admin / Manager authentication
CREATE TABLE IF NOT EXISTS login_table (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Manager') NOT NULL
);

-- Employee master table (linked via foreign key from tasks)
CREATE TABLE IF NOT EXISTS employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL UNIQUE
);

-- Task management table
CREATE TABLE IF NOT EXISTS tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    task_title VARCHAR(100) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Employees seeded by setup_db.py (500 records)

-- Default login credentials (passwords hashed by setup script)
-- admin / admin123  (Admin role)
-- manager / manager123  (Manager role)
