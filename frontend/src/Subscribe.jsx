import React from "react";

function Subscribe() {
  const handleSubscribe = async () => {
    const res = await fetch("FRONTEND_URL/create-checkout-session", {
      method: "POST",
    });

    const data = await res.json();
    window.location.href = data.url;
  };

  return (
    <div className="subscribe-page">
      <h1>Unlock Weekly Trends</h1>
      <p>
        One concise weekly brief for parents.
        No scrolling. No noise.
      </p>

      <h2>$3.99 / month</h2>
      <p>Cancel anytime.</p>

      <button className="subscribe-btn" onClick={handleSubscribe}>
        Subscribe Now
      </button>
    </div>
  );
}

export default Subscribe;
