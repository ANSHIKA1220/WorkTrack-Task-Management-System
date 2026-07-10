document.addEventListener("DOMContentLoaded", () => {
    const taskForm = document.getElementById("taskForm");
    const tasksBody = document.getElementById("tasksBody");
    const formMessage = document.getElementById("formMessage");
    const employeeInput = document.getElementById("employeeInput");
    const employeeId = document.getElementById("employee_id");
    const employeeList = document.getElementById("employeeList");
    const employeeClear = document.getElementById("employeeClear");
    const employeeCombobox = document.getElementById("employeeCombobox");
    const employeeCountHint = document.getElementById("employeeCountHint");
    const submitBtn = document.getElementById("submitBtn");
    const addEmployeeForm = document.getElementById("addEmployeeForm");
    const addEmployeeMessage = document.getElementById("addEmployeeMessage");

    let editingTaskId = null;
    let allEmployees = [];
    let allTasks = [];
    let activeIndex = -1;
    let addEmployeeMessageTimer = null;
    let formMessageTimer = null;

    loadEmployees();
    loadTasks();
    initEmployeeCombobox();
    initAddEmployeeForm();
    initSidebarNav();
    initEmployeeSearch();

    function initSidebarNav() {
        const links = document.querySelectorAll(".sidebar-link[data-panel]");
        const panels = document.querySelectorAll(".panel");
        const heroTitle = document.querySelector(".page-title");
        const heroDesc = document.querySelector(".page-desc");

        const panelMeta = {
            dashboard: {
                title: `Good day, ${document.querySelector(".sidebar-user-name")?.textContent || "there"}`,
                desc: "Assign tasks, manage employees, track completion.",
            },
            employees: {
                title: "Employee Directory",
                desc: "Add team members and browse the full employee list.",
            },
            reports: {
                title: "Reports & Analytics",
                desc: "Task completion stats and breakdown by type.",
            },
        };

        function showPanel(name) {
            links.forEach((link) => {
                link.classList.toggle("sidebar-link--active", link.dataset.panel === name);
            });
            panels.forEach((panel) => {
                panel.classList.toggle("panel--active", panel.id === `panel-${name}`);
            });

            const metricsGrid = document.querySelector(".main-content > .metrics-grid");
            if (metricsGrid) {
                metricsGrid.style.display = name === "dashboard" ? "" : "none";
            }

            const meta = panelMeta[name];
            if (meta && heroTitle && heroDesc) {
                heroTitle.textContent = meta.title;
                heroDesc.textContent = meta.desc;
            }

            if (name === "employees") renderEmployeeList();
            if (name === "reports") renderReports();
        }

        links.forEach((link) => {
            link.addEventListener("click", (e) => {
                e.preventDefault();
                showPanel(link.dataset.panel);
                history.replaceState(null, "", `#${link.dataset.panel}`);
            });
        });

        const hash = location.hash.replace("#", "");
        if (hash && panelMeta[hash]) {
            showPanel(hash);
        }
    }

    function initEmployeeSearch() {
        const search = document.getElementById("employeeSearch");
        if (!search) return;
        search.addEventListener("input", () => renderEmployeeList(search.value.trim()));
    }

    function renderEmployeeList(filter = "") {
        const body = document.getElementById("employeeListBody");
        const countEl = document.getElementById("employeeListCount");
        if (!body) return;

        const q = filter.toLowerCase();
        const filtered = q
            ? allEmployees.filter((e) => e.employee_name.toLowerCase().includes(q))
            : allEmployees;

        if (countEl) {
            countEl.textContent = filter
                ? `${filtered.length} of ${allEmployees.length} employees`
                : `${allEmployees.length} employees in directory`;
        }

        if (filtered.length === 0) {
            body.innerHTML = `<tr><td colspan="2" class="empty-cell">${filter ? "No employees match your search." : "No employees yet — add one above."}</td></tr>`;
            return;
        }

        body.innerHTML = filtered
            .map(
                (e) => `
            <tr>
                <td class="task-id">#${e.employee_id}</td>
                <td>
                    <div class="emp-cell">
                        <span class="emp-avatar">${getInitials(e.employee_name)}</span>
                        <span>${escapeHtml(e.employee_name)}</span>
                    </div>
                </td>
            </tr>`
            )
            .join("");
    }

    function renderReports() {
        const completionEl = document.getElementById("reportCompletion");
        const employeesEl = document.getElementById("reportEmployees");
        const avgEl = document.getElementById("reportAvgTasks");
        const body = document.getElementById("reportBody");
        if (!body) return;

        const total = allTasks.length;
        const done = allTasks.filter((t) => t.completed).length;
        const rate = total ? Math.round((done / total) * 100) : 0;

        if (completionEl) completionEl.textContent = `${rate}%`;
        if (employeesEl) employeesEl.textContent = allEmployees.length;
        if (avgEl) {
            avgEl.textContent = allEmployees.length
                ? (total / allEmployees.length).toFixed(1)
                : "0";
        }

        const byType = {};
        allTasks.forEach((t) => {
            if (!byType[t.task_title]) {
                byType[t.task_title] = { total: 0, done: 0, pending: 0 };
            }
            byType[t.task_title].total++;
            if (t.completed) byType[t.task_title].done++;
            else byType[t.task_title].pending++;
        });

        const types = Object.keys(byType).sort();
        if (types.length === 0) {
            body.innerHTML = '<tr><td colspan="4" class="empty-cell">No tasks yet — assign some from Dashboard.</td></tr>';
            return;
        }

        body.innerHTML = types
            .map(
                (type) => {
                    const row = byType[type];
                    return `
                <tr>
                    <td>${escapeHtml(type)}</td>
                    <td>${row.total}</td>
                    <td><span class="status-pill status-done">${row.done}</span></td>
                    <td><span class="status-pill status-pending">${row.pending}</span></td>
                </tr>`;
                }
            )
            .join("");
    }

    async function addEmployeeByName(rawName, { selectInTaskForm = false, showInAddPanel = false } = {}) {
        const name = rawName.trim();
        if (name.length < 2) {
            return { ok: false, error: "Name must be at least 2 characters." };
        }

        const res = await fetch("/api/employees", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ employee_name: name }),
        });
        const data = await res.json();

        if (!res.ok) {
            return { ok: false, error: data.error || "Could not add employee." };
        }

        await loadEmployees();

        if (selectInTaskForm) {
            employeeId.value = data.employee_id;
            employeeInput.value = data.employee_name;
            employeeClear.classList.remove("hidden");
            employeeCombobox.classList.add("combobox--selected");
            closeList();
        }

        if (showInAddPanel) {
            showAddEmployeeMessage(data.message, "success");
        }

        return { ok: true, data };
    }

    function initAddEmployeeForm() {
        if (!addEmployeeForm) return;

        addEmployeeForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const nameInput = document.getElementById("newEmployeeName");
            const btn = document.getElementById("addEmployeeBtn");

            btn.disabled = true;
            btn.textContent = "Adding...";
            hideAddEmployeeMessage();

            try {
                const result = await addEmployeeByName(nameInput.value, {
                    selectInTaskForm: false,
                    showInAddPanel: true,
                });
                if (!result.ok) {
                    showAddEmployeeMessage(result.error, "error");
                    return;
                }
                nameInput.value = "";
                clearSelection(true);
            } catch {
                showAddEmployeeMessage("Network error. Is the server running?", "error");
            } finally {
                btn.disabled = false;
                btn.textContent = "Add Employee";
            }
        });
    }

    function showAddEmployeeMessage(text, type) {
        if (!addEmployeeMessage) return;
        if (addEmployeeMessageTimer) {
            clearTimeout(addEmployeeMessageTimer);
            addEmployeeMessageTimer = null;
        }
        addEmployeeMessage.textContent = text;
        addEmployeeMessage.className = `toast toast--${type}`;

        if (type === "success") {
            addEmployeeMessageTimer = setTimeout(() => {
                hideAddEmployeeMessage();
                addEmployeeMessageTimer = null;
            }, 2000);
        }
    }

    function hideAddEmployeeMessage() {
        if (!addEmployeeMessage) return;
        if (addEmployeeMessageTimer) {
            clearTimeout(addEmployeeMessageTimer);
            addEmployeeMessageTimer = null;
        }
        addEmployeeMessage.className = "toast toast--hidden";
    }

    function initEmployeeCombobox() {
        employeeInput.addEventListener("input", () => {
            clearSelection(false);
            openList(employeeInput.value.trim());
        });

        employeeInput.addEventListener("focus", () => {
            openList(employeeInput.value.trim());
        });

        employeeInput.addEventListener("keydown", async (e) => {
            const items = employeeList.querySelectorAll(
                ".combobox-item:not(.combobox-item--empty):not(.combobox-item--hint)"
            );

            if (e.key === "ArrowDown") {
                e.preventDefault();
                activeIndex = Math.min(activeIndex + 1, items.length - 1);
                highlightItem(items);
            } else if (e.key === "ArrowUp") {
                e.preventDefault();
                activeIndex = Math.max(activeIndex - 1, 0);
                highlightItem(items);
            } else if (e.key === "Enter") {
                e.preventDefault();
                if (activeIndex >= 0 && items[activeIndex]) {
                    if (items[activeIndex].classList.contains("combobox-item--add")) {
                        await handleInlineAdd(items[activeIndex].dataset.name);
                    } else {
                        selectEmployee(items[activeIndex]);
                    }
                } else {
                    const query = employeeInput.value.trim();
                    const exact = findExactMatch(query);
                    if (exact) {
                        selectEmployeeByData(exact.employee_id, exact.employee_name);
                    } else if (query.length >= 2) {
                        await handleInlineAdd(query);
                    }
                }
            } else if (e.key === "Escape") {
                closeList();
            }
        });

        employeeClear.addEventListener("click", () => {
            clearSelection(true);
            employeeInput.focus();
        });

        document.addEventListener("click", (e) => {
            if (!employeeCombobox.contains(e.target)) {
                closeList();
            }
        });
    }

    function findExactMatch(query) {
        const q = query.toLowerCase();
        return allEmployees.find((e) => e.employee_name.toLowerCase() === q);
    }

    function filterEmployees(query) {
        if (!query) return allEmployees.slice(0, 10);
        const q = query.toLowerCase();
        return allEmployees
            .filter((e) => e.employee_name.toLowerCase().includes(q))
            .slice(0, 15);
    }

    function openList(query) {
        activeIndex = -1;
        employeeList.innerHTML = "";
        const results = filterEmployees(query);

        if (results.length === 0 && query.length >= 2) {
            const addLi = document.createElement("li");
            addLi.className = "combobox-item combobox-item--add";
            addLi.role = "option";
            addLi.dataset.name = query;
            addLi.innerHTML = `<strong>+ Add</strong> "${escapeHtml(query)}" as new employee`;
            addLi.addEventListener("mousedown", (e) => {
                e.preventDefault();
                handleInlineAdd(query);
            });
            employeeList.appendChild(addLi);
        } else if (results.length === 0) {
            employeeList.innerHTML =
                '<li class="combobox-item combobox-item--empty">Type a name to search or add</li>';
        } else {
            results.forEach((emp) => {
                const li = document.createElement("li");
                li.className = "combobox-item";
                li.role = "option";
                li.dataset.id = emp.employee_id;
                li.dataset.name = emp.employee_name;
                li.textContent = emp.employee_name;
                li.addEventListener("mousedown", (e) => {
                    e.preventDefault();
                    selectEmployee(li);
                });
                employeeList.appendChild(li);
            });

            if (query.length >= 2 && !findExactMatch(query)) {
                const addLi = document.createElement("li");
                addLi.className = "combobox-item combobox-item--add";
                addLi.role = "option";
                addLi.dataset.name = query;
                addLi.innerHTML = `<strong>+ Add new:</strong> "${escapeHtml(query)}"`;
                addLi.addEventListener("mousedown", (e) => {
                    e.preventDefault();
                    handleInlineAdd(query);
                });
                employeeList.appendChild(addLi);
            }
        }

        employeeList.classList.remove("hidden");
        employeeCombobox.classList.add("combobox--open");
    }

    async function handleInlineAdd(name) {
        try {
            const result = await addEmployeeByName(name, { selectInTaskForm: true });
            if (!result.ok) {
                showMessage(result.error, "error");
                return;
            }
            showMessage(result.data.message, "success");
        } catch {
            showMessage("Network error. Is the server running?", "error");
        }
    }

    function closeList() {
        employeeList.classList.add("hidden");
        employeeCombobox.classList.remove("combobox--open");
        activeIndex = -1;
    }

    function highlightItem(items) {
        items.forEach((item, i) => {
            item.classList.toggle("combobox-item--active", i === activeIndex);
        });
        if (items[activeIndex]) {
            items[activeIndex].scrollIntoView({ block: "nearest" });
        }
    }

    function selectEmployee(item) {
        selectEmployeeByData(item.dataset.id, item.dataset.name);
    }

    function selectEmployeeByData(id, name) {
        employeeId.value = id;
        employeeInput.value = name;
        employeeClear.classList.remove("hidden");
        employeeCombobox.classList.add("combobox--selected");
        closeList();
    }

    function clearSelection(clearInput) {
        employeeId.value = "";
        employeeCombobox.classList.remove("combobox--selected");
        employeeClear.classList.add("hidden");
        if (clearInput) {
            employeeInput.value = "";
            closeList();
        }
    }

    function resetEmployeePicker() {
        employeeInput.value = "";
        clearSelection(true);
    }

    taskForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        hideMessage();

        if (!employeeId.value) {
            const query = employeeInput.value.trim();
            if (query.length >= 2) {
                const exact = findExactMatch(query);
                if (exact) {
                    selectEmployeeByData(exact.employee_id, exact.employee_name);
                } else {
                    await handleInlineAdd(query);
                    if (!employeeId.value) return;
                }
            } else {
                showMessage("Please select or add an employee name.", "error");
                employeeInput.focus();
                openList(query);
                return;
            }
        }

        const payload = {
            employee_id: employeeId.value,
            task_title: document.getElementById("task_title").value,
            completed: document.getElementById("completed").value === "true",
        };

        submitBtn.disabled = true;
        submitBtn.textContent = "Submitting...";

        try {
            const url = editingTaskId ? `/api/tasks/${editingTaskId}` : "/api/tasks";
            const method = editingTaskId ? "PUT" : "POST";

            const res = await fetch(url, {
                method,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            const data = await res.json();

            if (!res.ok) {
                showMessage(data.error || "Something went wrong.", "error");
                return;
            }

            showMessage(data.message, "success");
            taskForm.reset();
            resetEmployeePicker();
            editingTaskId = null;
            submitBtn.textContent = "Submit Task";
            loadTasks();
        } catch {
            showMessage("Network error. Is the server running?", "error");
        } finally {
            submitBtn.disabled = false;
            if (!editingTaskId) {
                submitBtn.textContent = "Submit Task";
            }
        }
    });

    taskForm.addEventListener("reset", () => {
        editingTaskId = null;
        submitBtn.textContent = "Submit Task";
        resetEmployeePicker();
        hideMessage();
    });

    async function loadEmployees() {
        try {
            const res = await fetch("/api/employees");
            allEmployees = await res.json();

            if (employeeCountHint) {
                employeeCountHint.textContent = `${allEmployees.length} employees — search or add any name`;
            }
            renderEmployeeList(document.getElementById("employeeSearch")?.value.trim() || "");
            renderReports();
        } catch {
            if (employeeCountHint) {
                employeeCountHint.textContent = "Could not load employees";
            }
        }
    }

    async function loadTasks() {
        try {
            const res = await fetch("/api/tasks");
            const tasks = await res.json();
            allTasks = tasks;

            updateStats(tasks);
            renderReports();

            if (tasks.length === 0) {
                tasksBody.innerHTML =
                    '<tr><td colspan="6" class="empty-cell">No tasks yet — assign one using the form.</td></tr>';
                return;
            }

            tasksBody.innerHTML = tasks
                .map(
                    (t) => `
                <tr>
                    <td class="task-id">#${t.task_id}</td>
                    <td>
                        <div class="emp-cell">
                            <span class="emp-avatar">${getInitials(t.employee_name)}</span>
                            <span>${escapeHtml(t.employee_name)}</span>
                        </div>
                    </td>
                    <td>${escapeHtml(t.task_title)}</td>
                    <td>
                        <span class="status-pill ${t.completed ? "status-done" : "status-pending"}">
                            ${t.completed ? "Completed" : "Pending"}
                        </span>
                    </td>
                    <td class="date-cell">${t.created_at || "—"}</td>
                    <td class="action-cell">
                        <button class="btn-edit" data-id="${t.task_id}"
                            data-employee="${t.employee_id}"
                            data-name="${escapeHtml(t.employee_name)}"
                            data-title="${escapeHtml(t.task_title)}"
                            data-completed="${t.completed}">Edit</button>
                        <button class="btn-delete" data-id="${t.task_id}"
                            data-title="${escapeHtml(t.task_title)}">Remove</button>
                    </td>
                </tr>`
                )
                .join("");

            document.querySelectorAll(".btn-edit").forEach((btn) => {
                btn.addEventListener("click", () => editTask(btn));
            });

            document.querySelectorAll(".btn-delete").forEach((btn) => {
                btn.addEventListener("click", () => deleteTask(btn));
            });
        } catch {
            tasksBody.innerHTML =
                '<tr><td colspan="6" class="empty-cell">Failed to load tasks.</td></tr>';
        }
    }

    function updateStats(tasks) {
        const total = document.getElementById("statTotal");
        const pending = document.getElementById("statPending");
        const done = document.getElementById("statDone");
        if (!total) return;

        total.textContent = tasks.length;
        pending.textContent = tasks.filter((t) => !t.completed).length;
        done.textContent = tasks.filter((t) => t.completed).length;
    }

    function editTask(btn) {
        editingTaskId = btn.dataset.id;
        employeeId.value = btn.dataset.employee;
        employeeInput.value = btn.dataset.name || "";
        employeeClear.classList.remove("hidden");
        employeeCombobox.classList.add("combobox--selected");
        document.getElementById("task_title").value = btn.dataset.title;
        document.getElementById("completed").value = btn.dataset.completed;
        submitBtn.textContent = "Update Task";

        document.getElementById("taskForm").closest(".card").scrollIntoView({ behavior: "smooth" });
        showMessage(`Editing Task #${editingTaskId}`, "success");
    }

    async function deleteTask(btn) {
        const taskId = btn.dataset.id;
        const taskTitle = btn.dataset.title;
        const confirmed = confirm(
            `Remove Task #${taskId} (${taskTitle})?\n\nThis cannot be undone.`
        );
        if (!confirmed) return;

        try {
            const res = await fetch(`/api/tasks/${taskId}`, { method: "DELETE" });
            const data = await res.json();

            if (!res.ok) {
                showMessage(data.error || "Could not remove task.", "error");
                return;
            }

            if (editingTaskId) {
                taskForm.reset();
                resetEmployeePicker();
                editingTaskId = null;
                submitBtn.textContent = "Submit Task";
            }

            showMessage(data.message, "success");
            loadTasks();
        } catch {
            showMessage("Network error. Is the server running?", "error");
        }
    }

    function showMessage(text, type) {
        if (formMessageTimer) {
            clearTimeout(formMessageTimer);
            formMessageTimer = null;
        }
        formMessage.textContent = text;
        formMessage.className = `toast toast--${type}`;

        if (type === "success") {
            formMessageTimer = setTimeout(() => {
                hideMessage();
                formMessageTimer = null;
            }, 2000);
        }
    }

    function hideMessage() {
        if (formMessageTimer) {
            clearTimeout(formMessageTimer);
            formMessageTimer = null;
        }
        formMessage.className = "toast toast--hidden";
    }

    function getInitials(name) {
        return name
            .split(" ")
            .map((w) => w[0])
            .join("")
            .slice(0, 2)
            .toUpperCase();
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }
});
