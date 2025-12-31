import React from "react";
import "./modal.css";

function ContactModal({ onClose }) {
    return (
        <div className="modal-overlay">
            <div className="modal">
                <button className="close-btn" onClick={onClose}>×</button>
                <h2>Contact Us</h2>

                <form className="modal-form">
                    <label>
                        Title
                        <input type="text" placeholder="Subject" />
                    </label>

                    <label>
                        Message
                        <textarea placeholder="Write your message here..." rows="5" />
                    </label>

                    <button type="submit" className="primary-btn">
                        Send Message
                    </button>
                </form>
            </div>
        </div>
    );
}

export default ContactModal;
