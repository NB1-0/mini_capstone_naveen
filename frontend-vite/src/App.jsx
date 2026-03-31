import React, { useEffect, useMemo, useState } from "react";
import { apiFetch } from "./api.js";
import AccountPage from "./pages/Account.jsx";
import CatalogPage from "./pages/Catalog.jsx";
import CartPage from "./pages/Cart.jsx";
import OrdersPage from "./pages/Orders.jsx";
import AdminPage from "./pages/Admin.jsx";

const SESSION_KEY = "storyshelf.session";
const CART_KEY = "storyshelf.cart";

export default function App() {
  const [activePage, setActivePage] = useState("catalog");
  const [token, setToken] = useState("");
  const [user, setUser] = useState(null);
  const [books, setBooks] = useState([]);
  const [cart, setCart] = useState([]);
  const [orders, setOrders] = useState([]);
  const [adminOrders, setAdminOrders] = useState([]);
  const [salesReport, setSalesReport] = useState(null);
  const [message, setMessage] = useState("Ready.");

  useEffect(() => {
    const savedSession = readJson(SESSION_KEY);
    const savedCart = readJson(CART_KEY);

    if (savedSession?.token && savedSession?.user) {
      setToken(savedSession.token);
      setUser(savedSession.user);
    }

    if (Array.isArray(savedCart)) {
      setCart(savedCart);
    }
  }, []);

  useEffect(() => {
    loadBooks();
  }, []);

  useEffect(() => {
    if (user?.role === "customer") {
      loadOrders();
      setAdminOrders([]);
      setSalesReport(null);
    } else if (user?.role === "admin") {
      loadAdminData();
      setOrders([]);
    } else {
      setOrders([]);
      setAdminOrders([]);
      setSalesReport(null);
    }
  }, [user?.role]);

  useEffect(() => {
    window.localStorage.setItem(CART_KEY, JSON.stringify(cart));
  }, [cart]);

  const pages = useMemo(
    () => [
      { id: "catalog", label: "Catalog" },
      { id: "cart", label: "Cart" },
      { id: "orders", label: "Orders" },
      { id: "admin", label: "Admin" },
      { id: "account", label: "Account" }
    ],
    []
  );

  async function loadBooks() {
    try {
      const data = await apiFetch("/books", {}, token);
      setBooks(data);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function loadOrders() {
    if (!user || user.role !== "customer") {
      return;
    }
    try {
      const data = await apiFetch("/orders", {}, token);
      setOrders(data);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function loadAdminData() {
    if (!user || user.role !== "admin") {
      return;
    }
    try {
      const [ordersData, report] = await Promise.all([
        apiFetch("/admin/orders", {}, token),
        apiFetch("/admin/salesreport", {}, token)
      ]);
      setAdminOrders(ordersData);
      setSalesReport(report);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function handleLogin(credentials) {
    try {
      const response = await apiFetch("/auth/login", {
        method: "POST",
        body: credentials
      });
      setToken(response.access_token);
      setUser(response.user);
      window.localStorage.setItem(SESSION_KEY, JSON.stringify({
        token: response.access_token,
        user: response.user
      }));
      setMessage(`Welcome back, ${response.user.email}.`);
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function handleRegister(credentials) {
    try {
      const response = await apiFetch("/auth/register", {
        method: "POST",
        body: credentials
      });
      setToken(response.access_token);
      setUser(response.user);
      window.localStorage.setItem(SESSION_KEY, JSON.stringify({
        token: response.access_token,
        user: response.user
      }));
      setMessage("Account created.");
    } catch (error) {
      setMessage(error.message);
    }
  }

  function handleLogout() {
    setToken("");
    setUser(null);
    setOrders([]);
    setAdminOrders([]);
    setSalesReport(null);
    setCart([]);
    window.localStorage.removeItem(SESSION_KEY);
    setMessage("Signed out.");
  }

  function addToCart(book, quantity) {
    if (!book || book.stock < 1) {
      setMessage("Book is out of stock.");
      return;
    }
    const qty = Math.max(1, Number(quantity || 1));
    setCart((prev) => {
      const existing = prev.find((item) => item.bookId === book.id);
      if (existing) {
        return prev.map((item) =>
          item.bookId === book.id
            ? { ...item, quantity: Math.min(item.quantity + qty, book.stock) }
            : item
        );
      }
      return [
        ...prev,
        { bookId: book.id, title: book.title, price: book.price, quantity: Math.min(qty, book.stock) }
      ];
    });
  }

  function updateCartQuantity(bookId, quantity) {
    if (!Number.isFinite(quantity) || quantity < 1) {
      removeFromCart(bookId);
      return;
    }
    const book = books.find((b) => b.id === bookId);
    setCart((prev) =>
      prev.map((item) =>
        item.bookId === bookId
          ? { ...item, quantity: Math.min(quantity, book?.stock || quantity) }
          : item
      )
    );
  }

  function removeFromCart(bookId) {
    setCart((prev) => prev.filter((item) => item.bookId !== bookId));
  }

  async function handleCheckout() {
    if (!user || user.role !== "customer") {
      setMessage("Log in as a customer to place an order.");
      return;
    }
    if (cart.length === 0) {
      setMessage("Cart is empty.");
      return;
    }
    try {
      await apiFetch("/orders", {
        method: "POST",
        body: {
          items: cart.map((item) => ({
            book_id: item.bookId,
            quantity: item.quantity
          }))
        }
      }, token);
      setCart([]);
      setMessage("Order placed.");
      await loadBooks();
      await loadOrders();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function handleCreateBook(payload) {
    if (!user || user.role !== "admin") {
      return;
    }
    try {
      await apiFetch("/books", {
        method: "POST",
        body: {
          title: payload.title,
          author: payload.author,
          price: Number(payload.price),
          stock: Number(payload.stock)
        }
      }, token);
      setMessage("Book created.");
      await loadBooks();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function handleUpdateStatus(orderId, status) {
    if (!user || user.role !== "admin") {
      return;
    }
    try {
      await apiFetch(`/admin/orders/${orderId}/status`, {
        method: "PATCH",
        body: { status }
      }, token);
      setMessage(`Order ${orderId} updated.`);
      await loadAdminData();
      await loadBooks();
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function handleDeleteBook(book) {
    if (!user || user.role !== "admin") {
      return;
    }
    const confirmDelete = window.confirm(`Delete "${book.title}"?`);
    if (!confirmDelete) return;
    try {
      await apiFetch(`/books/${book.id}`, { method: "DELETE" }, token);
      setMessage("Book deleted.");
      await loadBooks();
    } catch (error) {
      setMessage(error.message);
    }
  }

  function handleEditBook(book) {
    setMessage(`Edit not wired yet for ${book.title}. Use the Admin create form for now.`);
  }

  return (
    <div className="container">
      <header className="header">
        <div>
          <h1>StoryShelf Console</h1>
          <p className="muted">Vite + React frontend for the bookstore API.</p>
        </div>
        <div className="nav">
          {pages.map((page) => (
            <button
              key={page.id}
              type="button"
              className={page.id === activePage ? "active" : ""}
              onClick={() => setActivePage(page.id)}
            >
              {page.label}
            </button>
          ))}
        </div>
      </header>

      <section className="page-section">
        <div className="section-title">
          <h2>Status</h2>
          <button type="button" className="secondary" onClick={loadBooks}>
            Refresh Books
          </button>
        </div>
        <div className="message">{message}</div>
      </section>

      {activePage === "account" && (
        <AccountPage user={user} onLogin={handleLogin} onRegister={handleRegister} onLogout={handleLogout} />
      )}
      {activePage === "catalog" && (
        <CatalogPage
          books={books}
          user={user}
          onAddToCart={addToCart}
          onEditBook={handleEditBook}
          onDeleteBook={handleDeleteBook}
        />
      )}
      {activePage === "cart" && (
        <CartPage
          cart={cart}
          books={books}
          user={user}
          onCheckout={handleCheckout}
          onUpdateQty={updateCartQuantity}
          onRemove={removeFromCart}
        />
      )}
      {activePage === "orders" && <OrdersPage user={user} orders={orders} />}
      {activePage === "admin" && (
        <AdminPage
          user={user}
          salesReport={salesReport}
          adminOrders={adminOrders}
          onRefresh={loadAdminData}
          onSubmitBook={handleCreateBook}
          onUpdateStatus={handleUpdateStatus}
        />
      )}
    </div>
  );
}

function readJson(key) {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}
