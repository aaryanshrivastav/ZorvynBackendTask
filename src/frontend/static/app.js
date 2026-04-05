const state = {
    baseUrl: window.location.origin,
    accessToken: "",
    refreshToken: "",
    currentUser: null,
};

const elements = {
    baseUrl: document.getElementById("base-url"),
    healthBadge: document.getElementById("health-badge"),
    authBadge: document.getElementById("auth-badge"),
    currentRole: document.getElementById("current-role"),
    currentUser: document.getElementById("current-user"),
    requestOutput: document.getElementById("request-output"),
    responseOutput: document.getElementById("response-output"),
};

function setDefaultOccurredAt() {
    const input = document.getElementById("tx-occurred-at");
    const now = new Date();
    const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    input.value = local;
}

function pretty(value) {
    if (typeof value === "string") {
        return value;
    }
    return JSON.stringify(value, null, 2);
}

function updateAuthSummary() {
    const isSignedIn = Boolean(state.accessToken);
    elements.authBadge.textContent = isSignedIn ? "Signed in" : "Signed out";
    elements.authBadge.className = `badge ${isSignedIn ? "" : "muted"}`.trim();
    elements.currentRole.textContent = state.currentUser?.role ?? "-";
    elements.currentUser.textContent = state.currentUser?.username ?? "-";
}

function setHealthStatus(ok, label) {
    elements.healthBadge.textContent = label;
    elements.healthBadge.className = `badge ${ok ? "" : "error"}`.trim();
}

async function apiCall(path, options = {}) {
    state.baseUrl = elements.baseUrl.value.trim() || window.location.origin;
    const url = `${state.baseUrl}${path}`;
    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    };

    if (state.accessToken) {
        headers.Authorization = `Bearer ${state.accessToken}`;
    }

    const requestSummary = {
        method: options.method || "GET",
        url,
        headers,
    };

    if (options.body) {
        requestSummary.body = JSON.parse(options.body);
    }

    elements.requestOutput.textContent = pretty(requestSummary);

    const response = await fetch(url, {
        ...options,
        headers,
    });

    const raw = await response.text();
    let payload;

    try {
        payload = raw ? JSON.parse(raw) : null;
    } catch {
        payload = raw;
    }

    elements.responseOutput.textContent = pretty({
        status: response.status,
        ok: response.ok,
        body: payload,
    });

    if (!response.ok) {
        throw new Error(typeof payload === "string" ? payload : payload?.detail || "Request failed");
    }

    return payload;
}

async function refreshProfile() {
    const me = await apiCall("/auth/me");
    state.currentUser = me;
    updateAuthSummary();
}

async function handleHealthCheck() {
    try {
        const payload = await apiCall("/health", { headers: {} });
        setHealthStatus(payload.status === "ok", payload.status === "ok" ? "Healthy" : "Unexpected");
    } catch (error) {
        setHealthStatus(false, "Unavailable");
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    const payload = await apiCall("/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
    });

    state.accessToken = payload.access_token;
    state.refreshToken = payload.refresh_token;
    await refreshProfile();
}

async function handleLogout() {
    if (!state.accessToken || !state.refreshToken) {
        state.accessToken = "";
        state.refreshToken = "";
        state.currentUser = null;
        updateAuthSummary();
        return;
    }

    try {
        await apiCall("/auth/logout", {
            method: "POST",
            body: JSON.stringify({ refresh_token: state.refreshToken }),
        });
    } finally {
        state.accessToken = "";
        state.refreshToken = "";
        state.currentUser = null;
        updateAuthSummary();
    }
}

async function handleCreateTransaction(event) {
    event.preventDefault();
    const occurredAt = document.getElementById("tx-occurred-at").value;
    const body = {
        transaction_id: document.getElementById("tx-transaction-id").value.trim(),
        occurred_at: new Date(occurredAt).toISOString(),
        account_number: document.getElementById("tx-account-number").value.trim(),
        transaction_type: document.getElementById("tx-type").value,
        amount: document.getElementById("tx-amount").value,
        currency: document.getElementById("tx-currency").value.trim(),
        counterparty: document.getElementById("tx-counterparty").value.trim(),
        category: document.getElementById("tx-category").value.trim(),
        payment_method: document.getElementById("tx-payment-method").value.trim(),
        notes: document.getElementById("tx-notes").value.trim(),
    };

    const created = await apiCall("/transactions", {
        method: "POST",
        body: JSON.stringify(body),
    });

    document.getElementById("cr-transaction-id").value = created.id;
}

async function handleCreateChangeRequest(event) {
    event.preventDefault();
    const proposedChanges = JSON.parse(document.getElementById("cr-payload").value);
    await apiCall("/change-requests/update", {
        method: "POST",
        body: JSON.stringify({
            transaction_id: Number(document.getElementById("cr-transaction-id").value),
            reason: document.getElementById("cr-reason").value.trim(),
            proposed_changes: proposedChanges,
        }),
    });
}

function bindQuickReadButtons() {
    document.querySelectorAll("[data-endpoint]").forEach((button) => {
        button.addEventListener("click", async () => {
            await apiCall(button.dataset.endpoint);
        });
    });
}

function bindEvents() {
    document.getElementById("health-btn").addEventListener("click", handleHealthCheck);
    document.getElementById("login-form").addEventListener("submit", async (event) => {
        try {
            await handleLogin(event);
        } catch (error) {
            updateAuthSummary();
        }
    });
    document.getElementById("logout-btn").addEventListener("click", handleLogout);
    document.getElementById("transaction-form").addEventListener("submit", handleCreateTransaction);
    document.getElementById("change-request-form").addEventListener("submit", handleCreateChangeRequest);
    document.getElementById("clear-console-btn").addEventListener("click", () => {
        elements.requestOutput.textContent = "No request yet.";
        elements.responseOutput.textContent = "No response yet.";
    });
    bindQuickReadButtons();
}

function init() {
    elements.baseUrl.value = state.baseUrl;
    setDefaultOccurredAt();
    updateAuthSummary();
    bindEvents();
    handleHealthCheck();
}

init();
