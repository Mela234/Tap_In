import { useEffect, useState } from "react";
import { getWeeklyTrends } from "../services/api";

function TrendWeekly() {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        setLoading(true);
        const data = await getWeeklyTrends();
        setTrends(data.trends);
      } catch (err) {
        console.error("Error fetching trends:", err);
        setError("Failed to load trends");
      } finally {
        setLoading(false);
      }
    };

    fetchTrends();
  }, []);

  if (loading) {
    return (
      <div className="weekly-page">
        <p className="loading">Loading trends...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="weekly-page">
        <p className="error">{error}</p>
      </div>
    );
  }

  return (
    <div className="weekly-page">
      <h2>This Week's Trends</h2>

      {trends.map((trend) => (
        <div key={trend.id} className="trend-card">
          <span className={`category ${trend.category?.toLowerCase()}`}>
            {trend.category}
          </span>
          <h3>{trend.title}</h3>
          <p>{trend.description}</p>
        </div>
      ))}
    </div>
  );
}

export default TrendWeekly;
