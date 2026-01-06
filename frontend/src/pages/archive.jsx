import { useEffect, useState } from "react";

function TrendWeekly() {
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:5000/api/trends/weekly")
      .then(res => res.json())
      .then(data => {
        setTrends(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Loading trends...</p>;

  return (
    <div className="weekly-page">
      <h2>This Week’s Trends</h2>

      {trends.map(trend => (
        <div key={trend.id} className="trend-card">
          <h3>{trend.title}</h3>
          <p>{trend.description}</p>
        </div>
      ))}
    </div>
  );
}

export default TrendWeekly;
