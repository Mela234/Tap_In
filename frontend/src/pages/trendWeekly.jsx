import { useEffect, useState } from "react";
import { getWeeklyTrends } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import Subscribe from "../Subscribe";

function TrendWeekly() {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        setLoading(true);
        const data = await getWeeklyTrends();
        console.log("📊 Weekly trends data:", data); // ← ADD THIS
        console.log("📊 Trends array:", data.trends); // ← ADD THIS
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
  console.log("🔍 Current state:", {
    loading,
    error,
    trendsCount: trends.length,
    user,
  });

  return (
    <div className="weekly-page">
      <h2 className="page-title">This Week's Trends</h2>
      <Subscribe trends={trends} user={user} />
    </div>
  );
}

export default TrendWeekly;
