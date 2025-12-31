import React from "react";
import "./modal.css";

function CreateAccountModal({ onClose }) {
    return (
        <div className="modal-overlay">
            <div className="modal">
                <button className="close-btn" onClick={onClose}>×</button>
                <h2>Create Account</h2>

                <form className="modal-form">
                    <label>
                        Email
                        <input type="email" placeholder="you@example.com" />
                    </label>

                    <label>
                        Password
                        <input type="password" placeholder="Create a password" />
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
