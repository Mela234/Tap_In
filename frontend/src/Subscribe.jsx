import "./Subscribe.css";
import { useState } from "react";

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

function EmailSubscriptionModal({ onClose, onSubscribe }) {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleEmailSubscribe = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch(
        "http://127.0.0.1:8000/api/email/subscribe",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, subscribe: true }),
        }
      );

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to subscribe");
      }

      setSuccess(true);
      setEmail("");
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (err) {
      console.error("Email subscription failed:", err);
      setError(err.message || "Failed to subscribe to email digest");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content email-subscription-modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        
        <div className="modal-header">
          <h2>📧 Get Weekly Trends</h2>
          <p>Receive our curated trends digest every 2 weeks, delivered straight to your inbox</p>
        </div>

        {success ? (
          <div className="success-message">
            <p>✅ Successfully subscribed! Check your email for confirmation.</p>
          </div>
        ) : (
          <form onSubmit={handleEmailSubscribe} className="email-form">
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            {error && <p className="error-message">{error}</p>}

            <div className="form-benefits">
              <p>✨ What you'll get:</p>
              <ul>
                <li>📊 Top 10 trends curated weekly</li>
                <li>💡 Why it matters to Gen Z</li>
                <li>🔗 Direct source links</li>
                <li>📱 Mobile-friendly format</li>
              </ul>
            </div>

            <button
              type="submit"
              className="submit-btn"
              disabled={loading || !email}
            >
              {loading ? "Subscribing..." : "Subscribe to Digest"}
            </button>

            <p className="form-note">
              We respect your privacy. Unsubscribe anytime from any email.
            </p>
          </form>
        )}
      </div>
    </div>
  );
}

function Subscribe({ trends = [], user }) {
  const [showEmailModal, setShowEmailModal] = useState(false);

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
        <div className="email-subscription-cta">
          <p>Want weekly digest emails too?</p>
          <button
            className="email-subscribe-btn"
            onClick={() => setShowEmailModal(true)}
          >
            📧 Enable Email Digest
          </button>
        </div>
        {showEmailModal && (
          <EmailSubscriptionModal
            onClose={() => setShowEmailModal(false)}
            onSubscribe={() => setShowEmailModal(false)}
          />
        )}
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

            <div className="alternative-cta">
              <p>Or get a free weekly digest:</p>
              <button
                className="email-digest-btn"
                onClick={() => setShowEmailModal(true)}
              >
                📧 Free Email Digest
              </button>
            </div>
          </div>
        </div>
      )}

      {showEmailModal && (
        <EmailSubscriptionModal
          onClose={() => setShowEmailModal(false)}
          onSubscribe={() => setShowEmailModal(false)}
        />
      )}
    </div>
  );
}

export default Subscribe;
