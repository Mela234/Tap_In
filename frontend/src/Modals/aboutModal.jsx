import React from "react";
import "./modal.css";

function AboutModal({ onClose }) {
    return (
        <div className="modal-overlay">
            <div className="modal about-modal">
                <button className="close-btn" onClick={onClose}>×</button>

                <h2>Why Tap In Exists</h2>

                <div className="about-content">
                    <p>
                        Conversations shouldn’t feel like you’re speaking two different languages.
                    </p>

                    <p>
                        Tap In was created to help bridge the growing gap between parents and their kids,
                        and between teachers and students — especially in a world shaped by fast-moving
                        online culture.
                    </p>

                    <p>
                        Trends, slang, inside jokes, and viral moments influence how young people think,
                        communicate, and connect. When adults are left out of that loop, it can lead to
                        misunderstandings, distance, and missed opportunities for connection.
                    </p>

                    <p>
                        At the same time, many people don’t want to be on social media — whether it’s for
                        mental health, focus, or personal choice — but still want to understand what their
                        friends, families, or students are experiencing.
                    </p>

                    <p>
                        Tap In gives you the context without the scroll.
                        No endless feeds. No pressure to perform. Just clear, weekly insights that help
                        you stay informed, relatable, and connected.
                    </p>

                    <p className="about-highlight">
                        Because understanding each other starts with knowing what’s shaping the
                        conversation.
                    </p>
                </div>
            </div>
        </div>
    );
}

export default AboutModal;
