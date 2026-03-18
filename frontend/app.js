const state = {
    customers: [],
    vehicles: [],
    reservations: [],
    notifications: [],
};

const feedbackEl = document.getElementById("feedback");
const systemStatusEl = document.getElementById("systemStatus");

function showFeedback(message, isError = false) {
    feedbackEl.textContent = message;
    feedbackEl.classList.toggle("error", isError);
}

function formatCurrency(value) {
    return new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL",
    }).format(value ?? 0);
}

function formatDate(value) {
    if (!value) {
        return "-";
    }
    return new Intl.DateTimeFormat("pt-BR").format(new Date(value));
}

function formatDateTime(value) {
    if (!value) {
        return "-";
    }
    return new Intl.DateTimeFormat("pt-BR", {
        dateStyle: "short",
        timeStyle: "short",
    }).format(new Date(value));
}

async function apiRequest(path, options = {}) {
    const response = await fetch(path, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });

    if (!response.ok) {
        const payload = await response.json().catch(() => ({ detail: "Erro inesperado." }));
        throw new Error(payload.detail || "Erro inesperado.");
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}

function fillSelect(selectId, items, formatter) {
    const select = document.getElementById(selectId);
    select.innerHTML = "";

    if (!items.length) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "Nenhum item disponivel";
        select.appendChild(option);
        return;
    }

    items.forEach((item) => {
        const option = document.createElement("option");
        option.value = item.id;
        option.textContent = formatter(item);
        select.appendChild(option);
    });
}

function renderSummary(summary) {
    document.getElementById("summaryCustomers").textContent = summary.customers_count;
    document.getElementById("summaryVehicles").textContent = summary.vehicles_count;
    document.getElementById("summaryAvailable").textContent = summary.available_vehicles;
    document.getElementById("summaryReservations").textContent = summary.active_reservations;
    document.getElementById("summaryPayments").textContent = summary.pending_payments;
    document.getElementById("summaryNotifications").textContent = summary.recent_notifications;

    systemStatusEl.textContent = summary.pending_payments > 0
        ? "Processando reservas pendentes"
        : "Fila sincronizada";
}

function renderCustomers() {
    const tbody = document.getElementById("customersTableBody");
    tbody.innerHTML = state.customers.map((customer) => `
        <tr>
            <td>${customer.full_name}</td>
            <td>${customer.email}</td>
            <td>${customer.phone || "-"}</td>
        </tr>
    `).join("");

    fillSelect("reservationCustomerId", state.customers, (item) => `${item.full_name} (${item.email})`);
}

function renderVehicles() {
    const tbody = document.getElementById("vehiclesTableBody");
    tbody.innerHTML = state.vehicles.map((vehicle) => `
        <tr>
            <td>${vehicle.brand} ${vehicle.model} ${vehicle.year}</td>
            <td>${vehicle.license_plate}</td>
            <td>${formatCurrency(vehicle.daily_rate)}</td>
            <td><span class="status-chip ${vehicle.status}">${vehicle.status}</span></td>
        </tr>
    `).join("");

    fillSelect(
        "reservationVehicleId",
        state.vehicles.filter((vehicle) => vehicle.status === "available"),
        (item) => `${item.brand} ${item.model} - ${item.license_plate}`,
    );
    fillSelect(
        "statusVehicleId",
        state.vehicles,
        (item) => `${item.brand} ${item.model} - ${item.status}`,
    );
}

function renderReservations() {
    const tbody = document.getElementById("reservationsTableBody");
    tbody.innerHTML = state.reservations.map((reservation) => `
        <tr>
            <td>#${reservation.id}</td>
            <td>${reservation.customer.full_name}</td>
            <td>${reservation.vehicle.brand} ${reservation.vehicle.model}</td>
            <td>${formatDate(reservation.start_date)} ate ${formatDate(reservation.end_date)}</td>
            <td>${formatCurrency(reservation.total_amount)}</td>
            <td><span class="status-chip ${reservation.status}">${reservation.status}</span></td>
            <td>
                ${reservation.payment?.status || "-"}
                ${reservation.simulate_payment_failure ? "<br><small>falha simulada</small>" : ""}
            </td>
        </tr>
    `).join("");
}

function renderNotifications() {
    const container = document.getElementById("notificationsList");

    if (!state.notifications.length) {
        container.innerHTML = "<p class='empty-state'>Nenhuma notificacao processada ainda.</p>";
        return;
    }

    container.innerHTML = state.notifications.map((notification) => `
        <article class="timeline-item">
            <span>${formatDateTime(notification.sent_at)}</span>
            <strong>${notification.customer_name}</strong>
            <p>${notification.message}</p>
            <small>${notification.customer_email}</small>
        </article>
    `).join("");
}

async function loadDashboard() {
    const [summary, customers, vehicles, reservations, notifications] = await Promise.all([
        apiRequest("/api/dashboard/summary"),
        apiRequest("/api/customers"),
        apiRequest("/api/vehicles"),
        apiRequest("/api/reservations"),
        apiRequest("/api/notifications/preview"),
    ]);

    state.customers = customers;
    state.vehicles = vehicles;
    state.reservations = reservations;
    state.notifications = notifications;

    renderSummary(summary);
    renderCustomers();
    renderVehicles();
    renderReservations();
    renderNotifications();
}

async function handleFormSubmit(formId, path, buildPayload, successMessage) {
    const form = document.getElementById(formId);
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(form);

        try {
            await apiRequest(path, {
                method: "POST",
                body: JSON.stringify(buildPayload(formData)),
            });
            form.reset();
            showFeedback(successMessage);
            await loadDashboard();
        } catch (error) {
            showFeedback(error.message, true);
        }
    });
}

async function init() {
    const today = new Date();
    const tomorrow = new Date();
    tomorrow.setDate(today.getDate() + 1);
    document.querySelector("#reservationForm input[name='start_date']").value = today.toISOString().slice(0, 10);
    document.querySelector("#reservationForm input[name='end_date']").value = tomorrow.toISOString().slice(0, 10);

    await loadDashboard().catch((error) => showFeedback(error.message, true));

    handleFormSubmit(
        "customerForm",
        "/api/customers",
        (formData) => ({
            full_name: formData.get("full_name"),
            email: formData.get("email"),
            phone: formData.get("phone") || null,
        }),
        "Cliente cadastrado com sucesso.",
    );

    handleFormSubmit(
        "vehicleForm",
        "/api/vehicles",
        (formData) => ({
            brand: formData.get("brand"),
            model: formData.get("model"),
            year: Number(formData.get("year")),
            daily_rate: Number(formData.get("daily_rate")),
            license_plate: String(formData.get("license_plate")).toUpperCase(),
        }),
        "Veiculo cadastrado com sucesso.",
    );

    handleFormSubmit(
        "reservationForm",
        "/api/reservations",
        (formData) => ({
            customer_id: Number(formData.get("customer_id")),
            vehicle_id: Number(formData.get("vehicle_id")),
            start_date: formData.get("start_date"),
            end_date: formData.get("end_date"),
            simulate_payment_failure: formData.get("simulate_payment_failure") === "on",
        }),
        "Reserva criada e enviada para a fila de pagamentos.",
    );

    document.getElementById("vehicleStatusForm").addEventListener("submit", async (event) => {
        event.preventDefault();
        const formData = new FormData(event.currentTarget);

        try {
            await apiRequest(`/api/vehicles/${formData.get("vehicle_id")}/status`, {
                method: "PATCH",
                body: JSON.stringify({ status: formData.get("status") }),
            });
            showFeedback("Status do veiculo atualizado.");
            await loadDashboard();
        } catch (error) {
            showFeedback(error.message, true);
        }
    });

    document.getElementById("refreshButton").addEventListener("click", async () => {
        try {
            await loadDashboard();
            showFeedback("Painel atualizado.");
        } catch (error) {
            showFeedback(error.message, true);
        }
    });

    setInterval(async () => {
        try {
            await loadDashboard();
        } catch (error) {
            showFeedback(error.message, true);
        }
    }, 10000);
}

init();
