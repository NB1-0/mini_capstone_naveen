import React, { useState } from "react";
import Section from "../components/Section.jsx";

export default function AccountPage({ user, onLogin, onRegister, onLogout }) {
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [registerEmail, setRegisterEmail] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");

  return (
    <Section
      title="Account"
      action={
        user ? (
          <button type="button" onClick={onLogout}>
            Log Out
          </button>
        ) : null
      }
    >
      {user ? (
        <div className="stack">
          <p>
            Signed in as <strong>{user.email}</strong>
          </p>
          <p className="muted">Role: {user.role}</p>
        </div>
      ) : (
        <div className="two-col">
          <form
            className="stack"
            onSubmit={(event) => {
              event.preventDefault();
              onLogin({ email: loginEmail, password: loginPassword });
            }}
          >
            <h3>Login</h3>
            <label>
              Email
              <input
                type="email"
                value={loginEmail}
                onChange={(event) => setLoginEmail(event.target.value)}
                required
              />
            </label>
            <label>
              Password
              <input
                type="password"
                value={loginPassword}
                onChange={(event) => setLoginPassword(event.target.value)}
                required
              />
            </label>
            <button type="submit">Login</button>
          </form>

          <form
            className="stack"
            onSubmit={(event) => {
              event.preventDefault();
              onRegister({ email: registerEmail, password: registerPassword });
            }}
          >
            <h3>Register</h3>
            <label>
              Email
              <input
                type="email"
                value={registerEmail}
                onChange={(event) => setRegisterEmail(event.target.value)}
                required
              />
            </label>
            <label>
              Password
              <input
                type="password"
                value={registerPassword}
                onChange={(event) => setRegisterPassword(event.target.value)}
                required
              />
            </label>
            <button type="submit">Register</button>
          </form>
        </div>
      )}
    </Section>
  );
}
