import React, { useState } from "react";
import Section from "../components/Section.jsx";
import { formatCurrency, formatDate } from "../api.js";

const ORDER_STATUSES = ["pending", "completed", "cancelled"];

export default function AdminPage({ user, salesReport, adminOrders, onRefresh, onSubmitBook, onUpdateStatus }) {
  const [formData, setFormData] = useState({
    title: "",
    author: "",
    price: "",
    stock: ""
  });

  if (!user || user.role !== "admin") {
    return (
      <Section title="Admin">
        <p className="muted">Admin tools are only available for admin accounts.</p>
      </Section>
    );
  }

  return (
    <Section
      title="Admin"
      action={
        <button type="button" className="secondary" onClick={onRefresh}>
          Refresh Admin Data
        </button>
      }
    >
      <div className="two-col">
        <div className="stack">
          <h3>Sales Report</h3>
          {salesReport ? (
            <div className="table">
              <div>Total Orders: {salesReport.total_orders}</div>
              <div>Pending: {salesReport.pending_orders}</div>
              <div>Completed: {salesReport.completed_orders}</div>
              <div>Cancelled: {salesReport.cancelled_orders}</div>
              <div>Gross: {formatCurrency(salesReport.gross_revenue)}</div>
              <div>Completed Revenue: {formatCurrency(salesReport.completed_revenue)}</div>
              <div>Items Sold: {salesReport.total_items_sold}</div>
              <div>Generated: {formatDate(salesReport.generated_at)}</div>
            </div>
          ) : (
            <p className="muted">No report yet.</p>
          )}
        </div>

        <div className="stack">
          <h3>Create Book</h3>
          <form
            className="stack"
            onSubmit={(event) => {
              event.preventDefault();
              onSubmitBook(formData);
              setFormData({ title: "", author: "", price: "", stock: "" });
            }}
          >
            <label>
              Title
              <input
                value={formData.title}
                onChange={(event) => setFormData({ ...formData, title: event.target.value })}
                required
              />
            </label>
            <label>
              Author
              <input
                value={formData.author}
                onChange={(event) => setFormData({ ...formData, author: event.target.value })}
                required
              />
            </label>
            <label>
              Price
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={formData.price}
                onChange={(event) => setFormData({ ...formData, price: event.target.value })}
                required
              />
            </label>
            <label>
              Stock
              <input
                type="number"
                min="0"
                value={formData.stock}
                onChange={(event) => setFormData({ ...formData, stock: event.target.value })}
                required
              />
            </label>
            <button type="submit">Create Book</button>
          </form>
        </div>
      </div>

      <div className="stack" style={{ marginTop: "16px" }}>
        <h3>Order Queue</h3>
        {adminOrders.length === 0 ? (
          <p className="muted">No orders yet.</p>
        ) : (
          <div className="order-list">
            {adminOrders.map((order) => (
              <div key={order.id} className="order-card">
                <div className="row">
                  <strong>Order {order.id}</strong>
                  <span className="status-tag">{order.status}</span>
                </div>
                <p className="muted">Placed {formatDate(order.created_at)} by {order.user_id}</p>
                <p>Total {formatCurrency(order.total_amount)}</p>
                <label>
                  Update Status
                  <select
                    value={order.status}
                    onChange={(event) => onUpdateStatus(order.id, event.target.value)}
                  >
                    {ORDER_STATUSES.map((status) => (
                      <option key={status} value={status}>
                        {status}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            ))}
          </div>
        )}
      </div>
    </Section>
  );
}
