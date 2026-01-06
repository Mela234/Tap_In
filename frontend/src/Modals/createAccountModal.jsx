import React, { useState } from "react";
import "./modal.css";

function CreateAccountModal({ onClose, onEmailSignUp }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault(); // prevent page reload
    if (!email || !password) {
      alert("Please enter both email and password.");
      return;
    }

    // Call the function passed from App.js
    await onEmailSignUp(email, password);

    // Clear the form (optional)
    setEmail("");
    setPassword("");
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <button className="close-btn" onClick={onClose}>×</button>
        <h2>Create Account</h2>

        <form className="modal-form" onSubmit={handleSubmit}>
          <label>
            Email
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>

          <label>
            Password
            <input
              type="password"
              placeholder="Create a password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>

          <button type="submit" className="primary-btn">
            Create Account
          </button>
        </form>
      </div>
    </div>
  );
}

export default CreateAccountModal;
