import React from "react";

export default function Section({ title, action, children }) {
  return (
    <section className="page-section">
      <div className="section-title">
        <h2>{title}</h2>
        {action}
      </div>
      {children}
    </section>
  );
}
