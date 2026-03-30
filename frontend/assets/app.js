const API_PREFIX = "/api/v1";
const SESSION_KEY = "storyshelf.session";
const CART_KEY = "storyshelf.cart";
const ORDER_STATUSES = ["pending", "completed", "cancelled"];

const state = {
    token: "",
    user: null,
    books: [],
    orders: [],
    adminOrders: [],
    salesReport: null,
    cart: [],
    editingBookId: null,
    activeAuthTab: "login",
    message: {
        type: "info",
        text: "Browse the catalog below. Sign in as a customer to place orders or as an admin to manage the store.",
    },
};

const elements = {};

document.addEventListener("DOMContentLoaded", () => {
    cacheElements();
    restoreState();
    bindEvents();
    renderAll();
    bootstrap();
});

function cacheElements() {
    elements.catalogGrid = document.querySelector("#catalog-grid");
    elements.catalogCount = document.querySelector("#catalog-count");
    elements.cartItems = document.querySelector("#cart-items");
    elements.cartSummary = document.querySelector("#cart-summary");
    elements.checkoutButton = document.querySelector("#checkout-btn");
    elements.checkoutHint = document.querySelector("#checkout-hint");
    elements.ordersList = document.querySelector("#orders-list");
    elements.adminPanel = document.querySelector("#admin-panel");
    elements.adminOrders = document.querySelector("#admin-orders");
    elements.salesReport = document.querySelector("#sales-report");
    elements.messageBanner = document.querySelector("#message-banner");
    elements.logoutButton = document.querySelector("#logout-btn");
    elements.sessionSummary = document.querySelector("#session-summary");
    elements.sessionEmail = document.querySelector("#session-email");
    elements.sessionRole = document.querySelector("#session-role");
    elements.sessionCreated = document.querySelector("#session-created");
    elements.authForms = document.querySelector("#auth-forms");
    elements.loginTab = document.querySelector("#auth-tab-login");
    elements.registerTab = document.querySelector("#auth-tab-register");
    elements.loginForm = document.querySelector("#login-form");
    elements.registerForm = document.querySelector("#register-form");
    elements.bookForm = document.querySelector("#book-form");
    elements.bookFormHeading = document.querySelector("#book-form-heading");
    elements.bookFormSubmit = document.querySelector("#book-form-submit");
    elements.bookFormCancel = document.querySelector("#book-form-cancel");
    elements.refreshBooksButton = document.querySelector("#refresh-books-btn");
    elements.refreshOrdersButton = document.querySelector("#refresh-orders-btn");
    elements.refreshAdminButton = document.querySelector("#refresh-admin-btn");
    elements.clearMessageButton = document.querySelector("#clear-message-btn");
    elements.statBooks = document.querySelector("#stat-books");
    elements.statOrders = document.querySelector("#stat-orders");
    elements.statAdminOrders = document.querySelector("#stat-admin-orders");
}

function bindEvents() {
    elements.loginTab.addEventListener("click", () => setAuthTab("login"));
    elements.registerTab.addEventListener("click", () => setAuthTab("register"));
    elements.loginForm.addEventListener("submit", handleLogin);
    elements.registerForm.addEventListener("submit", handleRegister);
    elements.logoutButton.addEventListener("click", handleLogout);
    elements.refreshBooksButton.addEventListener("click", () => refreshData({ announce: true }));
    elements.refreshOrdersButton.addEventListener("click", () => loadOrders({ announce: true }));
    elements.refreshAdminButton.addEventListener("click", () => loadAdminData({ announce: true }));
    elements.checkoutButton.addEventListener("click", handleCheckout);
    elements.clearMessageButton.addEventListener("click", () => {
        setMessage("info", "Status cleared. Use Refresh Data whenever you want to sync with the backend again.");
    });
    elements.bookForm.addEventListener("submit", handleBookSubmit);
    elements.bookFormCancel.addEventListener("click", resetBookForm);
    elements.catalogGrid.addEventListener("submit", handleCatalogSubmit);
    elements.catalogGrid.addEventListener("click", handleCatalogAction);
    elements.cartItems.addEventListener("change", handleCartQuantityChange);
    elements.cartItems.addEventListener("click", handleCartAction);
    elements.adminOrders.addEventListener("submit", handleAdminStatusSubmit);
}

function restoreState() {
    const savedSession = readJsonStorage(SESSION_KEY);
    const savedCart = readJsonStorage(CART_KEY);

    if (savedSession?.token && savedSession?.user) {
        state.token = savedSession.token;
        state.user = savedSession.user;
    }

    if (Array.isArray(savedCart)) {
        state.cart = savedCart.filter((item) => item && item.bookId && item.quantity > 0);
    }
}

async function bootstrap() {
    if (state.token) {
        try {
            state.user = await apiFetch("/auth/me");
            persistSession();
        } catch (error) {
            clearSession();
            setMessage("warning", `Previous session expired. ${error.message}`);
        }
    }

    await refreshData({ silent: true });
}

async function refreshData({ silent = false, announce = false } = {}) {
    try {
        const tasks = [loadBooks({ silent: true })];

        if (state.user?.role === "customer") {
            tasks.push(loadOrders({ silent: true }));
            state.adminOrders = [];
            state.salesReport = null;
        } else if (state.user?.role === "admin") {
            tasks.push(loadAdminData({ silent: true }));
            state.orders = [];
        } else {
            state.orders = [];
            state.adminOrders = [];
            state.salesReport = null;
        }

        await Promise.all(tasks);

        if (!silent || announce) {
            setMessage("success", "Dashboard synced with the backend.");
        }
    } catch (error) {
        setMessage("error", error.message);
    }

    renderAll();
}

async function loadBooks({ silent = false, announce = false } = {}) {
    try {
        state.books = await apiFetch("/books");
        syncCartWithBooks();

        if (!silent || announce) {
            setMessage("success", "Catalog refreshed.");
        }
    } catch (error) {
        if (!silent) {
            setMessage("error", error.message);
        }
        throw error;
    } finally {
        renderAll();
    }
}

async function loadOrders({ silent = false, announce = false } = {}) {
    if (state.user?.role !== "customer") {
        state.orders = [];
        renderAll();
        return;
    }

    try {
        state.orders = await apiFetch("/orders");
        if (!silent || announce) {
            setMessage("success", "Customer orders refreshed.");
        }
    } catch (error) {
        if (!silent) {
            setMessage("error", error.message);
        }
        throw error;
    } finally {
        renderAll();
    }
}

async function loadAdminData({ silent = false, announce = false } = {}) {
    if (state.user?.role !== "admin") {
        state.adminOrders = [];
        state.salesReport = null;
        renderAll();
        return;
    }

    try {
        const [orders, report] = await Promise.all([
            apiFetch("/admin/orders"),
            apiFetch("/admin/salesreport"),
        ]);
        state.adminOrders = orders;
        state.salesReport = report;
        if (!silent || announce) {
            setMessage("success", "Admin data refreshed.");
        }
    } catch (error) {
        if (!silent) {
            setMessage("error", error.message);
        }
        throw error;
    } finally {
        renderAll();
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);

    try {
        const response = await apiFetch("/auth/login", {
            method: "POST",
            body: {
                email: String(formData.get("email") || "").trim(),
                password: String(formData.get("password") || ""),
            },
        });
        applyAuthResponse(response);
        elements.loginForm.reset();
        setMessage("success", `Welcome back, ${response.user.email}.`);
        await refreshData({ silent: true });
    } catch (error) {
        setMessage("error", error.message);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);

    try {
        const response = await apiFetch("/auth/register", {
            method: "POST",
            body: {
                email: String(formData.get("email") || "").trim(),
                password: String(formData.get("password") || ""),
            },
        });
        applyAuthResponse(response);
        elements.registerForm.reset();
        setMessage("success", "Customer account created and signed in.");
        await refreshData({ silent: true });
    } catch (error) {
        setMessage("error", error.message);
    }
}

function handleLogout() {
    clearSession();
    resetBookForm();
    setMessage("info", "Signed out. The catalog stays public, and protected actions are hidden until you log in again.");
    renderAll();
}

function handleCatalogSubmit(event) {
    const form = event.target.closest("[data-add-form]");
    if (!form) {
        return;
    }

    event.preventDefault();

    const bookId = form.dataset.bookId;
    const quantityInput = form.querySelector('input[name="quantity"]');
    const quantity = Math.max(1, Number.parseInt(quantityInput?.value || "1", 10));
    const book = state.books.find((item) => item.id === bookId);

    if (!book) {
        setMessage("error", "That book is no longer available.");
        return;
    }

    if (book.stock < 1) {
        setMessage("warning", `${book.title} is currently out of stock.`);
        return;
    }

    upsertCart(book, quantity);
    quantityInput.value = "1";
    setMessage("success", `${book.title} added to cart.`);
}

function handleCatalogAction(event) {
    const target = event.target.closest("[data-action]");
    if (!target) {
        return;
    }

    const action = target.dataset.action;
    const bookId = target.dataset.bookId;
    const book = state.books.find((item) => item.id === bookId);

    if (!book) {
        setMessage("error", "The selected book could not be found.");
        return;
    }

    if (action === "edit-book") {
        populateBookForm(book);
        return;
    }

    if (action === "delete-book") {
        void deleteBook(book);
    }
}

function handleCartQuantityChange(event) {
    const input = event.target.closest("[data-cart-quantity]");
    if (!input) {
        return;
    }

    const bookId = input.dataset.bookId;
    const quantity = Number.parseInt(input.value || "1", 10);
    updateCartQuantity(bookId, quantity);
}

function handleCartAction(event) {
    const target = event.target.closest("[data-action]");
    if (!target) {
        return;
    }

    if (target.dataset.action === "remove-cart-item") {
        removeFromCart(target.dataset.bookId);
    }
}

async function handleCheckout() {
    if (state.user?.role !== "customer") {
        setMessage("warning", "Log in as a customer to place an order.");
        return;
    }

    if (state.cart.length === 0) {
        setMessage("warning", "Add at least one book to your cart before checking out.");
        return;
    }

    try {
        await apiFetch("/orders", {
            method: "POST",
            body: {
                items: state.cart.map((item) => ({
                    book_id: item.bookId,
                    quantity: item.quantity,
                })),
            },
        });

        state.cart = [];
        persistCart();
        setMessage("success", "Order placed successfully.");
        await Promise.all([loadBooks({ silent: true }), loadOrders({ silent: true })]);
    } catch (error) {
        setMessage("error", error.message);
    } finally {
        renderAll();
    }
}

async function handleBookSubmit(event) {
    event.preventDefault();

    if (state.user?.role !== "admin") {
        setMessage("warning", "Only admin users can manage books.");
        return;
    }

    const formData = new FormData(event.currentTarget);
    const payload = {
        title: String(formData.get("title") || "").trim(),
        author: String(formData.get("author") || "").trim(),
        price: Number.parseFloat(String(formData.get("price") || "0")),
        stock: Number.parseInt(String(formData.get("stock") || "0"), 10),
    };

    try {
        if (state.editingBookId) {
            await apiFetch(`/books/${state.editingBookId}`, {
                method: "PUT",
                body: payload,
            });
            setMessage("success", "Book updated.");
        } else {
            await apiFetch("/books", {
                method: "POST",
                body: payload,
            });
            setMessage("success", "Book created.");
        }

        resetBookForm();
        await loadBooks({ silent: true });
    } catch (error) {
        setMessage("error", error.message);
    }
}

async function handleAdminStatusSubmit(event) {
    const form = event.target.closest("[data-status-form]");
    if (!form) {
        return;
    }

    event.preventDefault();

    if (state.user?.role !== "admin") {
        setMessage("warning", "Only admin users can update order statuses.");
        return;
    }

    const orderId = form.dataset.orderId;
    const formData = new FormData(form);
    const status = String(formData.get("status") || "");

    try {
        await apiFetch(`/admin/orders/${orderId}/status`, {
            method: "PATCH",
            body: { status },
        });
        setMessage("success", `Order ${orderId} updated to ${status}.`);
        await loadAdminData({ silent: true });
        await loadBooks({ silent: true });
    } catch (error) {
        setMessage("error", error.message);
    }
}

async function deleteBook(book) {
    if (state.user?.role !== "admin") {
        setMessage("warning", "Only admin users can delete books.");
        return;
    }

    const confirmed = window.confirm(`Delete "${book.title}" by ${book.author}?`);
    if (!confirmed) {
        return;
    }

    try {
        await apiFetch(`/books/${book.id}`, { method: "DELETE" });
        if (state.editingBookId === book.id) {
            resetBookForm();
        }
        setMessage("success", `"${book.title}" removed from the catalog.`);
        await loadBooks({ silent: true });
    } catch (error) {
        setMessage("error", error.message);
    }
}

function populateBookForm(book) {
    state.editingBookId = book.id;
    elements.bookFormHeading.textContent = `Edit "${book.title}"`;
    elements.bookFormSubmit.textContent = "Save Changes";
    elements.bookFormCancel.classList.remove("hidden");
    elements.bookForm.elements.title.value = book.title;
    elements.bookForm.elements.author.value = book.author;
    elements.bookForm.elements.price.value = book.price;
    elements.bookForm.elements.stock.value = book.stock;
    elements.bookForm.scrollIntoView({ behavior: "smooth", block: "start" });
}

function resetBookForm() {
    state.editingBookId = null;
    elements.bookForm.reset();
    elements.bookFormHeading.textContent = "Create Book";
    elements.bookFormSubmit.textContent = "Create Book";
    elements.bookFormCancel.classList.add("hidden");
}

function setAuthTab(tab) {
    state.activeAuthTab = tab;
    elements.loginTab.classList.toggle("active", tab === "login");
    elements.registerTab.classList.toggle("active", tab === "register");
    elements.loginForm.classList.toggle("hidden", tab !== "login");
    elements.registerForm.classList.toggle("hidden", tab !== "register");
}

function applyAuthResponse(response) {
    state.token = response.access_token;
    state.user = response.user;
    persistSession();
    if (state.user.role !== "admin") {
        resetBookForm();
    }
    renderAll();
}

function clearSession() {
    state.token = "";
    state.user = null;
    state.orders = [];
    state.adminOrders = [];
    state.salesReport = null;
    state.cart = [];
    persistCart();
    window.localStorage.removeItem(SESSION_KEY);
}

function persistSession() {
    if (!state.token || !state.user) {
        window.localStorage.removeItem(SESSION_KEY);
        return;
    }

    window.localStorage.setItem(
        SESSION_KEY,
        JSON.stringify({
            token: state.token,
            user: state.user,
        }),
    );
}

function persistCart() {
    window.localStorage.setItem(CART_KEY, JSON.stringify(state.cart));
}

function upsertCart(book, quantity) {
    const existingItem = state.cart.find((item) => item.bookId === book.id);
    const nextQuantity = existingItem ? existingItem.quantity + quantity : quantity;
    const safeQuantity = Math.min(nextQuantity, book.stock);

    if (existingItem) {
        existingItem.quantity = safeQuantity;
        existingItem.title = book.title;
        existingItem.price = book.price;
    } else {
        state.cart.push({
            bookId: book.id,
            title: book.title,
            price: book.price,
            quantity: safeQuantity,
        });
    }

    persistCart();
    renderAll();
}

function updateCartQuantity(bookId, quantity) {
    if (!Number.isFinite(quantity) || quantity < 1) {
        removeFromCart(bookId);
        return;
    }

    const book = state.books.find((item) => item.id === bookId);
    const cartItem = state.cart.find((item) => item.bookId === bookId);
    if (!book || !cartItem) {
        removeFromCart(bookId);
        return;
    }

    cartItem.quantity = Math.min(quantity, Math.max(book.stock, 1));
    persistCart();
    renderAll();
}

function removeFromCart(bookId) {
    state.cart = state.cart.filter((item) => item.bookId !== bookId);
    persistCart();
    setMessage("info", "Item removed from cart.");
    renderAll();
}

function syncCartWithBooks() {
    const bookMap = new Map(state.books.map((book) => [book.id, book]));
    state.cart = state.cart
        .map((item) => {
            const book = bookMap.get(item.bookId);
            if (!book || book.stock < 1) {
                return null;
            }

            return {
                bookId: item.bookId,
                title: book.title,
                price: book.price,
                quantity: Math.min(item.quantity, book.stock),
            };
        })
        .filter(Boolean);
    persistCart();
}

function setMessage(type, text) {
    state.message = { type, text };
    renderMessage();
}

function renderAll() {
    renderSession();
    renderMessage();
    renderStats();
    renderCatalog();
    renderCart();
    renderOrders();
    renderAdmin();
}

function renderSession() {
    const isSignedIn = Boolean(state.user);

    elements.sessionSummary.classList.toggle("hidden", !isSignedIn);
    elements.logoutButton.classList.toggle("hidden", !isSignedIn);
    elements.authForms.classList.toggle("hidden", isSignedIn);

    if (!isSignedIn) {
        setAuthTab(state.activeAuthTab);
        return;
    }

    elements.sessionEmail.textContent = state.user.email;
    elements.sessionRole.textContent = state.user.role;
    elements.sessionCreated.textContent = `Joined ${formatDate(state.user.created_at)}`;
}

function renderMessage() {
    elements.messageBanner.className = `message-banner ${state.message.type}`;
    elements.messageBanner.textContent = state.message.text;
}

function renderStats() {
    elements.statBooks.textContent = String(state.books.length);
    elements.statOrders.textContent = String(state.orders.length);
    elements.statAdminOrders.textContent = String(state.adminOrders.length);
}

function renderCatalog() {
    elements.catalogCount.textContent = `${state.books.length} book${state.books.length === 1 ? "" : "s"}`;

    if (state.books.length === 0) {
        elements.catalogGrid.innerHTML = emptyState(
            "No books found",
            "Seed the bookstore or create a new title from the admin panel."
        );
        return;
    }

    elements.catalogGrid.innerHTML = state.books
        .map((book) => {
            const stockClass = getStockClass(book.stock);
            const showAdminActions = state.user?.role === "admin";
            const purchaseDisabled = book.stock < 1 ? "disabled" : "";

            return `
                <article class="book-card">
                    <div>
                        <div class="price-row">
                            <span class="pill">Book ID ${escapeHtml(book.id)}</span>
                            <span class="stock-tag ${stockClass}">${book.stock} in stock</span>
                        </div>
                        <h4 class="spacer-top">${escapeHtml(book.title)}</h4>
                        <p class="book-meta">by ${escapeHtml(book.author)}</p>
                    </div>
                    <div class="price-row">
                        <span class="price-tag">${formatCurrency(book.price)}</span>
                        <span class="muted-text">Added ${formatDate(book.created_at)}</span>
                    </div>
                    ${
                        showAdminActions
                            ? `
                                <div class="admin-actions">
                                    <button class="ghost-button" type="button" data-action="edit-book" data-book-id="${escapeHtml(book.id)}">Edit</button>
                                    <button class="ghost-button" type="button" data-action="delete-book" data-book-id="${escapeHtml(book.id)}">Delete</button>
                                </div>
                              `
                            : `
                                <form data-add-form data-book-id="${escapeHtml(book.id)}">
                                    <label>
                                        Quantity
                                        <input name="quantity" type="number" min="1" max="${book.stock}" value="1" ${purchaseDisabled}>
                                    </label>
                                    <button class="primary-button full-width" type="submit" ${purchaseDisabled}>Add to Cart</button>
                                </form>
                              `
                    }
                </article>
            `;
        })
        .join("");
}

function renderCart() {
    const totalItems = state.cart.reduce((sum, item) => sum + item.quantity, 0);
    const totalAmount = state.cart.reduce((sum, item) => sum + item.quantity * item.price, 0);
    const canCheckout = state.user?.role === "customer" && state.cart.length > 0;

    elements.cartSummary.textContent = `${totalItems} item${totalItems === 1 ? "" : "s"} | ${formatCurrency(totalAmount)}`;
    elements.checkoutButton.disabled = !canCheckout;

    if (state.user?.role === "customer") {
        elements.checkoutHint.textContent = "Customer mode active. Checkout will call POST /api/v1/orders.";
    } else if (state.user?.role === "admin") {
        elements.checkoutHint.textContent = "Admin accounts can manage inventory but cannot place customer orders.";
    } else {
        elements.checkoutHint.textContent = "Log in as a customer to submit the cart as an order.";
    }

    if (state.cart.length === 0) {
        elements.cartItems.innerHTML = emptyState(
            "Cart is empty",
            "Add a few titles from the catalog to build an order."
        );
        return;
    }

    elements.cartItems.innerHTML = state.cart
        .map((item) => {
            const book = state.books.find((entry) => entry.id === item.bookId);
            const maxStock = book?.stock || item.quantity;

            return `
                <article class="cart-card">
                    <div class="cart-row">
                        <div>
                            <h4>${escapeHtml(item.title)}</h4>
                            <p class="cart-meta">${formatCurrency(item.price)} each</p>
                        </div>
                        <button class="text-button" type="button" data-action="remove-cart-item" data-book-id="${escapeHtml(item.bookId)}">Remove</button>
                    </div>
                    <div class="cart-row cart-controls">
                        <label>
                            Quantity
                            <input
                                type="number"
                                min="1"
                                max="${maxStock}"
                                value="${item.quantity}"
                                data-cart-quantity
                                data-book-id="${escapeHtml(item.bookId)}"
                            >
                        </label>
                        <span class="price-tag">${formatCurrency(item.price * item.quantity)}</span>
                    </div>
                </article>
            `;
        })
        .join("");
}

function renderOrders() {
    if (!state.user) {
        elements.ordersList.innerHTML = emptyState(
            "Customer orders are protected",
            "Log in as a customer to view your own order history."
        );
        return;
    }

    if (state.user.role !== "customer") {
        elements.ordersList.innerHTML = emptyState(
            "Admin account detected",
            "Customer order history is hidden for admin sessions."
        );
        return;
    }

    if (state.orders.length === 0) {
        elements.ordersList.innerHTML = emptyState(
            "No orders yet",
            "Once you check out, new orders will appear here."
        );
        return;
    }

    elements.ordersList.innerHTML = state.orders
        .map((order) => renderOrderCard(order, false))
        .join("");
}

function renderAdmin() {
    const isAdmin = state.user?.role === "admin";
    elements.adminPanel.classList.toggle("hidden", !isAdmin);

    if (!isAdmin) {
        return;
    }

    if (!state.salesReport) {
        elements.salesReport.innerHTML = emptyState(
            "No report yet",
            "Refresh admin data to fetch the live sales report."
        );
    } else {
        const report = state.salesReport;
        const metrics = [
            ["Total Orders", report.total_orders],
            ["Pending", report.pending_orders],
            ["Completed", report.completed_orders],
            ["Cancelled", report.cancelled_orders],
            ["Gross Revenue", formatCurrency(report.gross_revenue)],
            ["Completed Revenue", formatCurrency(report.completed_revenue)],
            ["Items Sold", report.total_items_sold],
            ["Generated", formatDate(report.generated_at)],
        ];

        elements.salesReport.innerHTML = metrics
            .map(
                ([label, value]) => `
                    <article class="metric-card">
                        <span>${escapeHtml(String(label))}</span>
                        <strong>${escapeHtml(String(value))}</strong>
                    </article>
                `
            )
            .join("");
    }

    if (state.adminOrders.length === 0) {
        elements.adminOrders.innerHTML = emptyState(
            "No orders in the queue",
            "Customer orders will appear here for status updates."
        );
        return;
    }

    elements.adminOrders.innerHTML = state.adminOrders
        .map((order) => renderOrderCard(order, true))
        .join("");
}

function renderOrderCard(order, adminMode) {
    const itemsMarkup = order.items
        .map((item) => {
            const book = state.books.find((entry) => entry.id === item.book_id);
            const label = book ? `${book.title}` : `Book ${item.book_id}`;
            return `<li>${escapeHtml(label)} x ${item.quantity} at ${formatCurrency(item.price)}</li>`;
        })
        .join("");

    return `
        <article class="order-card">
            <div class="order-topline">
                <div>
                    <h4>Order ${escapeHtml(order.id)}</h4>
                    <p class="order-meta">Placed ${formatDate(order.created_at)}${
                        adminMode ? ` by user ${escapeHtml(order.user_id)}` : ""
                    }</p>
                </div>
                <span class="status-tag ${escapeHtml(order.status)}">${escapeHtml(order.status)}</span>
            </div>
            <p class="order-meta">Total ${formatCurrency(order.total_amount)}</p>
            <ol class="order-items">${itemsMarkup}</ol>
            ${
                adminMode
                    ? `
                        <form class="status-form" data-status-form data-order-id="${escapeHtml(order.id)}">
                            <label>
                                Update Status
                                <select name="status">
                                    ${ORDER_STATUSES.map(
                                        (status) =>
                                            `<option value="${status}" ${status === order.status ? "selected" : ""}>${status}</option>`
                                    ).join("")}
                                </select>
                            </label>
                            <button type="submit">Save Status</button>
                        </form>
                      `
                    : ""
            }
        </article>
    `;
}

function emptyState(title, description) {
    return `
        <article class="empty-state">
            <h4>${escapeHtml(title)}</h4>
            <p>${escapeHtml(description)}</p>
        </article>
    `;
}

async function apiFetch(path, options = {}) {
    const headers = {
        Accept: "application/json",
        ...(options.headers || {}),
    };

    if (state.token) {
        headers.Authorization = `Bearer ${state.token}`;
    }

    let body = options.body;
    if (body && !(body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
        body = JSON.stringify(body);
    }

    const response = await fetch(`${API_PREFIX}${path}`, {
        method: options.method || "GET",
        headers,
        body,
    });

    if (response.status === 204) {
        return null;
    }

    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json")
        ? await response.json()
        : await response.text();

    if (!response.ok) {
        throw new Error(extractErrorMessage(payload) || `Request failed with status ${response.status}.`);
    }

    return payload;
}

function extractErrorMessage(payload) {
    if (!payload) {
        return "Request failed.";
    }

    if (typeof payload === "string") {
        return payload;
    }

    if (typeof payload.detail === "string") {
        return payload.detail;
    }

    if (Array.isArray(payload.errors) && payload.errors[0]?.msg) {
        return payload.errors[0].msg;
    }

    return "Request failed.";
}

function formatCurrency(value) {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 2,
    }).format(Number(value || 0));
}

function formatDate(value) {
    if (!value) {
        return "Unknown time";
    }

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
    }).format(date);
}

function getStockClass(stock) {
    if (stock < 1) {
        return "out-of-stock";
    }
    if (stock < 5) {
        return "low-stock";
    }
    return "in-stock";
}

function readJsonStorage(key) {
    try {
        const raw = window.localStorage.getItem(key);
        return raw ? JSON.parse(raw) : null;
    } catch (_error) {
        return null;
    }
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}
