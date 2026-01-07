import React, { useState } from "react";
import "./modal.css";
import GoogleLogo from "../assets/googleLogo.png";

function SignInModal({ onClose, onGoogleSignIn, onEmailSignIn, onCreateAccount }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    return (
        <div className="modal-overlay">
            <div className="modal">
                <button className="close-btn" onClick={onClose}>×</button>
                <h2>Sign In</h2>

                <form
                    className="modal-form"
                    onSubmit={(e) => {
                        e.preventDefault();
                        onEmailSignIn(email, password);
                    }}
                >
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
                    <button
                        type="button" // important!
                        className="google-btn"
                        onClick={onGoogleSignIn}
                        >
                            <img src={GoogleLogo} alt="Google Logo" />
                            Continue with Google
                    </button>
            
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
