import { useEffect, useState } from "react";
import { getArchive } from "../services/api";
import { useAuth } from "../hooks/useAuth";
import Subscribe from "../Subscribe";

function Archive() {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    const fetchArchive = async () => {
      try {
        setLoading(true);
        const data = await getArchive();
        setTrends(data.trends);
      } catch (err) {
        console.error("Error fetching archive:", err);
        setError("Failed to load archive");
      } finally {
        setLoading(false);
      }
    };

    fetchArchive();
  }, []);

  if (loading) {
    return (
      <div className="archive-page">
        <p className="loading">Loading archive...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="archive-page">
        <p className="error">{error}</p>
      </div>
    );
  }

  return (
    <div className="archive-page">
      <h2 className="page-title">Trend Archive</h2>
      <Subscribe trends={trends} user={user} />
    </div>
  );
}

export default Archive;
