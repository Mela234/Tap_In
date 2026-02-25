import "./Subscribe.css";

const FREE_TRENDS_COUNT = 3;

function TrendCard({ trend }) {
  return (
    <div className="trend-card">
      <div className="trend-card-header">
        <span className="trend-category">{trend.category}</span>
        <span className="trend-score">
          🔥 {Math.round((trend.relevance_score || 0) * 100)}%
        </span>
      </div>
      <h3 className="trend-title">{trend.title}</h3>
      <p className="trend-description">{trend.description}</p>
      {trend.why_it_matters && (
        <p className="trend-why">💡 {trend.why_it_matters}</p>
      )}
    </div>
  );
}

function LockedTrendCard({ trend }) {
  return (
    <div className="trend-card trend-card-locked">
      <div className="trend-card-header">
        <span className="trend-category">{trend.category}</span>
      </div>
      <h3 className="trend-title">{trend.title}</h3>
      <p className="trend-description">{trend.description}</p>
    </div>
  );
}

function Subscribe({ trends = [], user }) {
  const handleSubscribe = async () => {
    try {
      const res = await fetch(
        "http://127.0.0.1:4242/api/create-checkout-session",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ uid: user?.uid }),
        },
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
    } catch (err) {
      console.error("Stripe checkout failed:", err);
      alert("Checkout failed — check console + backend logs");
    }
  };

  // ── Subscribed: show everything ──
  if (user?.isSubscribed) {
    return (
      <div className="subscribe-page">
        <div className="trends-list">
          {trends.map((trend) => (
            <TrendCard key={trend.id} trend={trend} />
          ))}
        </div>
      </div>
    );
  }

  // ── Not subscribed: show 3 free + lock the rest ──
  const freeTrends = trends.slice(0, FREE_TRENDS_COUNT);
  const lockedTrends = trends.slice(FREE_TRENDS_COUNT);

  return (
    <div className="subscribe-page">
      {/* Free trends */}
      <div className="trends-list">
        {freeTrends.map((trend) => (
          <TrendCard key={trend.id} trend={trend} />
        ))}
      </div>

      {/* Locked section */}
      {lockedTrends.length > 0 && (
        <div className="locked-section">
          <div className="locked-trends">
            {lockedTrends.map((trend) => (
              <LockedTrendCard key={trend.id} trend={trend} />
            ))}
            <div className="locked-fade" />
          </div>

          {/* Paywall card */}
          <div className="paywall-card">
            <span className="lock-icon">🔒</span>
            <h2>You've seen the tip of the iceberg</h2>
            <p>One concise weekly brief for parents. No scrolling. No noise.</p>
            <h3 className="paywall-price">$3.99 / month</h3>
            <p className="paywall-cancel">Cancel anytime.</p>
            <button className="subscribe-btn" onClick={handleSubscribe}>
              Unlock All Trends
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Subscribe;
