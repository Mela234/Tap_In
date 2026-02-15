import React from "react";

function Subscribe() {
  const handleSubscribe = async () => {
  try {
    const res = await fetch(
      "http://127.0.0.1:4242/api/create-checkout-session",
      { method: "POST" }
    );

    if (!res.ok) {
      const err = await res.text();
      throw new Error(err);
    }

    const data = await res.json();

    if (!data.url) {
      throw new Error("No checkout URL returned");
    }

      window.location.href = data.url;
    }
    catch (err) {
      console.error("Stripe checkout failed:", err);
      alert("Checkout failed — check console + backend logs");
    }
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
