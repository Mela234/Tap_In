import React, { useState, useEffect } from "react";
import { getWeeklyTrends } from "./services/api";
import "./HighlightCarousel.css";

function HighlightCarousel() {
  const [highlights, setHighlights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [index, setIndex] = useState(0);

  // Fetch trends on component mount
  useEffect(() => {
    const fetchTrends = async () => {
      try {
        setLoading(true);
        const data = await getWeeklyTrends();
        setHighlights(data.trends);
      } catch (err) {
        console.error("Error fetching trends:", err);
        setError("Failed to load trends");
      } finally {
        setLoading(false);
      }
    };

    fetchTrends();
  }, []);

  useEffect(() => {
    if (highlights.length === 0) return;

    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % highlights.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [highlights.length]);

  if (loading) {
    return (
      <section className="highlights-window">
        <div className="highlights-header">
          <h2>This Week's Highlights</h2>
        </div>
        <div className="loading">Loading trends...</div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="highlights-window">
        <div className="highlights-header">
          <h2>This Week's Highlights</h2>
        </div>
        <div className="error">{error}</div>
      </section>
    );
  }

  return (
    <section className="highlights-window">
      <div className="highlights-header">
        <h2>This Week's Highlights</h2>
      </div>

      <div className="highlights-viewport">
        <div
          className="highlights-track"
          style={{ transform: `translateX(-${index * 100}%)` }}
        >
          {highlights.map((item) => (
            <div className="highlights-card" key={item.id}>
              <span className={`platform ${item.category.toLowerCase()}`}>
                {item.category}
              </span>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default HighlightCarousel;
