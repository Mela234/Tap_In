import React from "react";

function Subscribe({ onSubscribe }) {
    return (
      <div className="subscribe-page">
        <h1>Unlock Weekly Trends</h1>
  
        <p>
          One concise weekly brief for parents.
          No scrolling. No noise.
        </p>
  
        <h2>$3.99 / month</h2>
        <p>Cancel anytime.</p>
  
        <button className="subscribe-btn" onClick={onSubscribe}>
          Subscribe Now
        </button>
      </div>
    );
  }
  
  export default Subscribe;
  