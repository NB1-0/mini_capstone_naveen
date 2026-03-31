import React from "react";
import Section from "../components/Section.jsx";
import { formatCurrency, formatDate } from "../api.js";

export default function OrdersPage({ user, orders }) {
  return (
    <Section title="Orders">
      {!user ? (
        <p className="muted">Log in as a customer to view orders.</p>
      ) : user.role !== "customer" ? (
        <p className="muted">Orders are only available for customer accounts.</p>
      ) : orders.length === 0 ? (
        <p className="muted">No orders yet.</p>
      ) : (
        <div className="order-list">
          {orders.map((order) => (
            <article key={order.id} className="order-card">
              <div className="row">
                <strong>Order {order.id}</strong>
                <span className="status-tag">{order.status}</span>
              </div>
              <p className="muted">Placed {formatDate(order.created_at)}</p>
              <p>Total {formatCurrency(order.total_amount)}</p>
              <ul className="stack">
                {order.items.map((item) => (
                  <li key={`${order.id}-${item.book_id}`}>
                    Book {item.book_id} x {item.quantity} ({formatCurrency(item.price)})
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      )}
    </Section>
  );
}
