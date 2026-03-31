import React from "react";
import Section from "../components/Section.jsx";
import { formatCurrency, formatDate } from "../api.js";

export default function CatalogPage({ books, user, onAddToCart, onEditBook, onDeleteBook }) {
  return (
    <Section title="Catalog">
      <div className="catalog-grid">
        {books.length === 0 ? (
          <p className="muted">No books found.</p>
        ) : (
          books.map((book) => {
            const outOfStock = book.stock < 1;
            return (
              <article className="book-card" key={book.id}>
                <div className="row">
                  <span className="pill">Book ID {book.id}</span>
                  <span className="pill">{book.stock} in stock</span>
                </div>
                <h4>{book.title}</h4>
                <p className="muted">by {book.author}</p>
                <div className="row">
                  <strong>{formatCurrency(book.price)}</strong>
                  <span className="muted">Added {formatDate(book.created_at)}</span>
                </div>
                {user?.role === "admin" ? (
                  <div className="card-actions">
                    <button type="button" className="secondary" onClick={() => onEditBook(book)}>
                      Edit
                    </button>
                    <button type="button" className="secondary" onClick={() => onDeleteBook(book)}>
                      Delete
                    </button>
                  </div>
                ) : (
                  <form
                    className="stack"
                    onSubmit={(event) => {
                      event.preventDefault();
                      const formData = new FormData(event.currentTarget);
                      const quantity = Number(formData.get("quantity") || 1);
                      onAddToCart(book, quantity);
                      event.currentTarget.reset();
                    }}
                  >
                    <label>
                      Quantity
                      <input name="quantity" type="number" min="1" max={book.stock} defaultValue="1" />
                    </label>
                    <button type="submit" disabled={outOfStock}>
                      {outOfStock ? "Out of Stock" : "Add to Cart"}
                    </button>
                  </form>
                )}
              </article>
            );
          })
        )}
      </div>
    </Section>
  );
}
