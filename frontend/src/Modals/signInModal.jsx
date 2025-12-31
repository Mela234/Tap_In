import React from "react";
import "./modal.css";

function SignInModal({ onClose, onCreateAccount }) {
    return (
        <div className="modal-overlay">
            <div className="modal">
                <button className="close-btn" onClick={onClose}>×</button>
                <h2>Sign In</h2>

                <form className="modal-form">
                    <label>
                        Email
                        <input type="email" placeholder="you@example.com" />
                    </label>

                    <label>
                        Password
                        <input type="password" placeholder="••••••••" />
                    </label>

                    <button type="submit" className="primary-btn">
                        Sign In
                    </button>

                    <p className="modal-footer">
                        Not registered?{" "}
                        <button
                            type="button"
                            className="link-btn teal"
                            onClick={onCreateAccount}
                        >
                            Create an account
                        </button>
                    </p>
                </form>
            </div>
        </div>
    );
}

export default SignInModal;
