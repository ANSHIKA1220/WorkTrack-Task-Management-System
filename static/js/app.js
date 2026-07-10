document.addEventListener("DOMContentLoaded", () => {
    const state = {
        role: document.body.dataset.role || "Manager",
        employees: [],
        tasks: [],
        users: [],
        report: null,
        editingTaskId: null,
    };

    const canAdmin = state.role === "Admin";
    const $ = (id) => document.getElementById(id);

    initShell();
    initForms();
    loadAll();

    function initShell() {
        $("todayLabel").textContent = new Date().toLocaleDateString(undefined, {
            weekday: "short",
            day: "numeric",
            month: "short",
            year: "numeric",
        });

        document.querySelectorAll(".flash").forEach((el) => setTimeout(() => el.remove(), 4500));
        $("mobileMenuBtn")?.addEventListener("click", () => $("sidebar").classList.toggle("sidebar--open"));

        document.querySelectorAll(".sidebar-link[data-panel]").forEach((link) => {
            link.addEventListener("click", (event) => {
                event.preventDefault();
                showPanel(link.dataset.panel);
            });
        });

        document.querySelectorAll("[data-panel-jump]").forEach((button) => {
            button.addEventListener("click", () => showPanel(button.dataset.panelJump));
        });

        const hash = location.hash.replace("#", "");
        if (hash) showPanel(hash);
    }

    function showPanel(name) {
        const link = document.querySelector(`.sidebar-link[data-panel="${name}"]`);
        const panel = $(`panel-${name}`);
        if (!link || !panel) return;

        document.querySelectorAll(".sidebar-link").forEach((item) => {
            item.classList.toggle("sidebar-link--active", item.dataset.panel === name);
        });
        document.querySelectorAll(".panel").forEach((item) => {
            item.classList.toggle("panel--active", item.id === `panel-${name}`);
        });
        $("sidebar").classList.remove("sidebar--open");
        history.replaceState(null, "", `#${name}`);

        const titles = {
            overview: [state.role === "Admin" ? "Admin Dashboard" : "Manager Dashboard", "Live task metrics and workload signals."],
            employees: ["Employee Directory", "Search employees and review assignment counts."],
            tasks: ["Assign Tasks", "Create tasks, filter work, and update status."],
            reports: ["Reports", "Completion and workload analytics from MySQL."],
            users: ["User Management", "Admin-only view of login accounts."],
        };
        const meta = titles[name] || titles.overview;
        $("pageTitle").textContent = meta[0];
        $("pageDesc").textContent = meta[1];
    }

    function initForms() {
        $("addEmployeeForm")?.addEventListener("submit", addEmployee);
        $("taskForm")?.addEventListener("submit", saveTask);
        $("taskForm")?.addEventListener("reset", resetTaskForm);
        $("employeeSearch")?.addEventListener("input", renderEmployees);
        ["taskSearch", "statusFilter", "typeFilter", "employeeFilter"].forEach((id) => {
            $(id)?.addEventListener("input", renderTasks);
            $(id)?.addEventListener("change", renderTasks);
        });
        initEmployeeCombobox();
    }

    async function loadAll() {
        await Promise.all([loadEmployees(), loadTasks(), loadReport(), canAdmin ? loadUsers() : Promise.resolve()]);
    }

    async function loadEmployees() {
        const res = await fetchJson("/api/employees");
        state.employees = res || [];
        renderEmployees();
        refreshEmployeeOptions();
    }

    async function loadTasks() {
        const res = await fetchJson("/api/tasks");
        state.tasks = res || [];
        updateStats();
        renderRecentTasks();
        renderTasks();
    }

    async function loadReport() {
        state.report = await fetchJson("/api/reports");
        renderReport();
    }

    async function loadUsers() {
        state.users = await fetchJson("/api/users") || [];
        renderUsers();
    }

    async function fetchJson(url, options = {}) {
        try {
            const res = await fetch(url, options);
            const data = await res.json();
            if (!res.ok) {
                showToast($("formMessage"), data.error || "Request failed.", "error");
                return null;
            }
            return data;
        } catch {
            showToast($("formMessage"), "Network error. Is the server running?", "error");
            return null;
        }
    }

    function updateStats() {
        const total = state.tasks.length;
        const done = state.tasks.filter((task) => task.completed).length;
        const pending = total - done;
        const rate = total ? Math.round((done / total) * 100) : 0;
        $("statTotal").textContent = total;
        $("statPending").textContent = pending;
        $("statDone").textContent = done;
        $("statRate").textContent = `${rate}%`;
        $("progressLabel").textContent = `${rate}%`;
        $("progressBar").style.width = `${rate}%`;
    }

    function renderRecentTasks() {
        const body = $("recentTasksBody");
        const rows = state.tasks.slice(0, 6);
        if (!rows.length) {
            body.innerHTML = '<tr><td colspan="5" class="empty-cell">No tasks yet. Assign one from the Tasks page.</td></tr>';
            return;
        }
        body.innerHTML = rows.map((task) => `
            <tr>
                <td class="task-id">#${task.task_id}</td>
                <td>${employeeCell(task.employee_name)}</td>
                <td>${escapeHtml(task.task_title)}</td>
                <td>${statusBadge(task.completed)}</td>
                <td>${task.due_date || "-"}</td>
            </tr>
        `).join("");
    }

    function renderEmployees() {
        const body = $("employeeListBody");
        const query = ($("employeeSearch")?.value || "").toLowerCase();
        const employees = state.employees.filter((employee) => employee.employee_name.toLowerCase().includes(query));
        $("employeeListCount").textContent = `${employees.length} of ${state.employees.length} employees shown`;

        if (!employees.length) {
            body.innerHTML = `<tr><td colspan="${canAdmin ? 5 : 4}" class="empty-cell">No employees match your search.</td></tr>`;
            return;
        }

        body.innerHTML = employees.map((employee) => `
            <tr>
                <td>${employeeCell(employee.employee_name)}</td>
                <td>${employee.task_count || 0}</td>
                <td><span class="status-pill status-done">${employee.completed_count || 0}</span></td>
                <td><span class="status-pill status-pending">${employee.pending_count || 0}</span></td>
                ${canAdmin ? `<td class="action-cell">
                    <button class="btn-small" data-edit-employee="${employee.employee_id}">Edit</button>
                    <button class="btn-small btn-danger" data-delete-employee="${employee.employee_id}">Delete</button>
                </td>` : ""}
            </tr>
        `).join("");

        body.querySelectorAll("[data-edit-employee]").forEach((button) => {
            button.addEventListener("click", () => editEmployee(button.dataset.editEmployee));
        });
        body.querySelectorAll("[data-delete-employee]").forEach((button) => {
            button.addEventListener("click", () => deleteEmployee(button.dataset.deleteEmployee));
        });
    }

    function refreshEmployeeOptions() {
        const employeeFilter = $("employeeFilter");
        const typeFilter = $("typeFilter");
        if (employeeFilter) {
            const current = employeeFilter.value;
            employeeFilter.innerHTML = '<option value="">All employees</option>' + state.employees
                .map((employee) => `<option value="${employee.employee_id}">${escapeHtml(employee.employee_name)}</option>`)
                .join("");
            employeeFilter.value = current;
        }
        if (typeFilter) {
            const types = [...new Set(state.tasks.map((task) => task.task_title))].sort();
            const current = typeFilter.value;
            typeFilter.innerHTML = '<option value="">All types</option>' + types
                .map((type) => `<option value="${escapeHtml(type)}">${escapeHtml(type)}</option>`)
                .join("");
            typeFilter.value = current;
        }
        $("employeeCountHint").textContent = `${state.employees.length} employees available`;
    }

    function renderTasks() {
        const body = $("tasksBody");
        let tasks = [...state.tasks];
        const query = ($("taskSearch")?.value || "").toLowerCase();
        const status = $("statusFilter")?.value || "";
        const type = $("typeFilter")?.value || "";
        const employeeId = $("employeeFilter")?.value || "";

        if (query) {
            tasks = tasks.filter((task) =>
                task.employee_name.toLowerCase().includes(query) ||
                task.task_title.toLowerCase().includes(query) ||
                (task.task_description || "").toLowerCase().includes(query)
            );
        }
        if (status) tasks = tasks.filter((task) => status === "completed" ? task.completed : !task.completed);
        if (type) tasks = tasks.filter((task) => task.task_title === type);
        if (employeeId) tasks = tasks.filter((task) => String(task.employee_id) === employeeId);

        if (!tasks.length) {
            body.innerHTML = '<tr><td colspan="6" class="empty-cell">No tasks found.</td></tr>';
            return;
        }

        body.innerHTML = tasks.map((task) => `
            <tr>
                <td class="task-id">#${task.task_id}</td>
                <td>${employeeCell(task.employee_name)}</td>
                <td><strong>${escapeHtml(task.task_title)}</strong><small>${escapeHtml(task.task_description || "")}</small></td>
                <td>${statusBadge(task.completed)}</td>
                <td>${task.due_date || "-"}</td>
                <td class="action-cell">
                    ${canAdmin ? `<button class="btn-small" data-edit-task="${task.task_id}">Edit</button>` : ""}
                    <button class="btn-small" data-toggle-task="${task.task_id}">${task.completed ? "Mark Pending" : "Complete"}</button>
                    ${canAdmin ? `<button class="btn-small btn-danger" data-delete-task="${task.task_id}">Delete</button>` : ""}
                </td>
            </tr>
        `).join("");

        body.querySelectorAll("[data-edit-task]").forEach((button) => {
            button.addEventListener("click", () => editTask(button.dataset.editTask));
        });
        body.querySelectorAll("[data-toggle-task]").forEach((button) => {
            button.addEventListener("click", () => toggleTask(button.dataset.toggleTask));
        });
        body.querySelectorAll("[data-delete-task]").forEach((button) => {
            button.addEventListener("click", () => deleteTask(button.dataset.deleteTask));
        });
    }

    function renderReport() {
        const report = state.report;
        if (!report) return;
        $("reportCompletion").textContent = `${report.completion_rate}%`;
        $("reportProgressBar").style.width = `${report.completion_rate}%`;
        $("reportSummary").textContent = `${report.completed_tasks} completed, ${report.pending_tasks} pending, ${report.avg_tasks_per_employee} average tasks per employee.`;

        $("reportTypeBody").innerHTML = report.by_type.length ? report.by_type.map((row) => `
            <tr><td>${escapeHtml(row.task_title)}</td><td>${row.total}</td><td>${row.completed}</td><td>${row.pending}</td></tr>
        `).join("") : '<tr><td colspan="4" class="empty-cell">No task type data yet.</td></tr>';

        $("reportWorkloadBody").innerHTML = report.workload.length ? report.workload.map((row) => `
            <tr><td>${employeeCell(row.employee_name)}</td><td>${row.total}</td><td>${row.completed}</td><td>${row.pending}</td></tr>
        `).join("") : '<tr><td colspan="4" class="empty-cell">No workload data yet.</td></tr>';

        $("workloadList").innerHTML = report.workload.length ? report.workload.slice(0, 5).map((row) => `
            <div class="workload-item"><span>${escapeHtml(row.employee_name)}</span><strong>${row.total}</strong></div>
        `).join("") : '<p class="muted">No assigned tasks yet.</p>';
    }

    function renderUsers() {
        const body = $("usersBody");
        if (!body) return;
        body.innerHTML = state.users.map((user) => `
            <tr><td class="task-id">#${user.user_id}</td><td>${escapeHtml(user.username)}</td><td><span class="role-tag role-${user.role.toLowerCase()}">${escapeHtml(user.role)}</span></td></tr>
        `).join("");
    }

    async function addEmployee(event) {
        event.preventDefault();
        const input = $("newEmployeeName");
        const name = input.value.trim();
        if (name.length < 2) {
            showToast($("addEmployeeMessage"), "Employee name must be at least 2 characters.", "error");
            return;
        }
        const data = await fetchJson("/api/employees", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ employee_name: name }),
        });
        if (!data) return;
        showToast($("addEmployeeMessage"), data.message, "success");
        input.value = "";
        await loadEmployees();
    }

    async function editEmployee(id) {
        const employee = state.employees.find((item) => String(item.employee_id) === String(id));
        const nextName = prompt("Update employee name", employee?.employee_name || "");
        if (!nextName) return;
        const data = await fetchJson(`/api/employees/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ employee_name: nextName }),
        });
        if (data) {
            showToast($("addEmployeeMessage"), data.message, "success");
            await loadEmployees();
            await loadReport();
        }
    }

    async function deleteEmployee(id) {
        const employee = state.employees.find((item) => String(item.employee_id) === String(id));
        if (!confirm(`Delete ${employee?.employee_name || "this employee"}?\n\nThis only works when no tasks are assigned.`)) return;
        const data = await fetchJson(`/api/employees/${id}`, { method: "DELETE" });
        if (data) {
            showToast($("addEmployeeMessage"), data.message, "success");
            await loadEmployees();
            await loadReport();
        }
    }

    async function saveTask(event) {
        event.preventDefault();
        if (!$("employee_id").value) {
            showToast($("formMessage"), "Please select an employee.", "error");
            return;
        }
        const payload = {
            employee_id: $("employee_id").value,
            task_title: $("task_title").value,
            task_description: $("task_description").value.trim(),
            due_date: $("due_date").value,
            completed: $("completed").value === "true",
        };
        const url = state.editingTaskId ? `/api/tasks/${state.editingTaskId}` : "/api/tasks";
        const method = state.editingTaskId ? "PUT" : "POST";
        const data = await fetchJson(url, {
            method,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        if (!data) return;
        showToast($("formMessage"), data.message, "success");
        resetTaskForm();
        await loadTasks();
        await loadEmployees();
        await loadReport();
        refreshEmployeeOptions();
    }

    function editTask(id) {
        const task = state.tasks.find((item) => String(item.task_id) === String(id));
        if (!task) return;
        state.editingTaskId = id;
        $("taskFormTitle").textContent = `Edit Task #${id}`;
        $("submitBtn").textContent = "Update Task";
        $("employee_id").value = task.employee_id;
        $("employeeInput").value = task.employee_name;
        $("employeeClear").classList.remove("hidden");
        $("task_title").value = task.task_title;
        $("task_description").value = task.task_description || "";
        $("due_date").value = task.due_date || "";
        $("completed").value = String(Boolean(task.completed));
        document.querySelector("#panel-tasks .card").scrollIntoView({ behavior: "smooth" });
    }

    async function toggleTask(id) {
        const task = state.tasks.find((item) => String(item.task_id) === String(id));
        if (!task) return;
        const payload = canAdmin
            ? { ...task, completed: !task.completed }
            : { completed: !task.completed };
        const data = await fetchJson(`/api/tasks/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        if (data) {
            await loadTasks();
            await loadEmployees();
            await loadReport();
        }
    }

    async function deleteTask(id) {
        if (!confirm(`Delete Task #${id}? This cannot be undone.`)) return;
        const data = await fetchJson(`/api/tasks/${id}`, { method: "DELETE" });
        if (data) {
            showToast($("formMessage"), data.message, "success");
            await loadTasks();
            await loadEmployees();
            await loadReport();
        }
    }

    function resetTaskForm() {
        state.editingTaskId = null;
        $("taskForm").reset();
        $("taskFormTitle").textContent = "Assign Task";
        $("submitBtn").textContent = "Assign Task";
        $("employee_id").value = "";
        $("employeeInput").value = "";
        $("employeeClear").classList.add("hidden");
    }

    function initEmployeeCombobox() {
        const input = $("employeeInput");
        const hidden = $("employee_id");
        const list = $("employeeList");
        const clear = $("employeeClear");
        if (!input || !list) return;

        input.addEventListener("input", () => {
            hidden.value = "";
            renderEmployeeChoices(input.value);
        });
        input.addEventListener("focus", () => renderEmployeeChoices(input.value));
        clear.addEventListener("click", () => {
            input.value = "";
            hidden.value = "";
            clear.classList.add("hidden");
            list.classList.add("hidden");
        });
        document.addEventListener("click", (event) => {
            if (!$("employeeCombobox").contains(event.target)) list.classList.add("hidden");
        });
    }

    function renderEmployeeChoices(query) {
        const list = $("employeeList");
        const q = query.toLowerCase();
        const matches = state.employees
            .filter((employee) => employee.employee_name.toLowerCase().includes(q))
            .slice(0, 12);
        if (!matches.length) {
            list.innerHTML = '<li class="combobox-item combobox-item--empty">No employees found</li>';
        } else {
            list.innerHTML = matches.map((employee) => `
                <li class="combobox-item" data-id="${employee.employee_id}" data-name="${escapeHtml(employee.employee_name)}">${escapeHtml(employee.employee_name)}</li>
            `).join("");
            list.querySelectorAll(".combobox-item[data-id]").forEach((item) => {
                item.addEventListener("mousedown", (event) => {
                    event.preventDefault();
                    $("employee_id").value = item.dataset.id;
                    $("employeeInput").value = item.dataset.name;
                    $("employeeClear").classList.remove("hidden");
                    list.classList.add("hidden");
                });
            });
        }
        list.classList.remove("hidden");
    }

    function employeeCell(name) {
        return `<div class="emp-cell"><span class="emp-avatar">${initials(name)}</span><span>${escapeHtml(name)}</span></div>`;
    }

    function statusBadge(done) {
        return `<span class="status-pill ${done ? "status-done" : "status-pending"}">${done ? "Completed" : "Pending"}</span>`;
    }

    function initials(name) {
        return String(name || "?").split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase();
    }

    function showToast(el, text, type) {
        if (!el) return;
        el.textContent = text;
        el.className = `toast toast--${type}`;
        if (type === "success") setTimeout(() => el.className = "toast toast--hidden", 3000);
    }

    function escapeHtml(value) {
        const div = document.createElement("div");
        div.textContent = value == null ? "" : String(value);
        return div.innerHTML;
    }
});
