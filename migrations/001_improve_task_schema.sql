-- WorkTrack task metadata migration.
-- Recommended command: python migrate.py
-- migrate.py checks information_schema first, so it is safe to run repeatedly.

USE task_management;

ALTER TABLE tasks ADD COLUMN task_description VARCHAR(500) NULL AFTER task_title;
ALTER TABLE tasks ADD COLUMN due_date DATE NULL AFTER completed;
ALTER TABLE tasks ADD COLUMN created_by INT NULL AFTER created_at;
ALTER TABLE tasks ADD COLUMN updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP AFTER created_by;

CREATE INDEX idx_tasks_employee_id ON tasks (employee_id);
CREATE INDEX idx_tasks_completed ON tasks (completed);
CREATE INDEX idx_tasks_due_date ON tasks (due_date);
