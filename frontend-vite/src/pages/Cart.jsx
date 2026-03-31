import React from "react";
import Section from "../components/Section.jsx";
import { formatCurrency } from "../api.js";

export default function CartPage({ cart, books, user, onCheckout, onUpdateQty, onRemove }) {
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
  const totalAmount = cart.reduce((sum, item) => sum + item.quantity * item.price, 0);

  return (
    <Section title="Cart">
      <p className="muted">{totalItems} item(s) | {formatCurrency(totalAmount)}</p>
      {cart.length === 0 ? (
        <p className="muted">Cart is empty.</p>
      ) : (
        <div className="stack">
          {cart.map((item) => {
            const book = books.find((b) => b.id === item.bookId);
            const maxStock = book?.stock || item.quantity;
            return (
              <div key={item.bookId} className="order-card">
                <div className="row">
                  <strong>{item.title}</strong>
                  <button type="button" className="secondary" onClick={() => onRemove(item.bookId)}>
                    Remove
                  </button>
                </div>
                <div className="row">
                  <label>
                    Qty
                    <input
                      type="number"
                      min="1"
                      max={maxStock}
                      value={item.quantity}
                      onChange={(event) => onUpdateQty(item.bookId, Number(event.target.value || 1))}
                    />
                  </label>
                  <span>{formatCurrency(item.quantity * item.price)}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
      <div className="card-actions" style={{ marginTop: "12px" }}>
        <button type="button" onClick={onCheckout} disabled={!user || user.role !== "customer" || cart.length === 0}>
          Place Order
        </button>
      </div>
    </Section>
  );
}
