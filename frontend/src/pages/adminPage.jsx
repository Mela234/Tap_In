import { useState, useEffect } from "react";
import { auth } from "../firebase";
import { api, getCategories } from "../services/api";
import "./AdminPage.css";

function AdminCreateTrend() {
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState({
    title: "",
    description: "",
    why_it_matters: "",
    how_to_talk_about_it: "",
    category_id: "",
    relevance_score: 0.85,
    sources: "",
    week_start: "",
    week_end: "",
  });

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await getCategories();
        setCategories(data.categories);
      } catch (err) {
        console.error("Error fetching categories:", err);
      }
    };
    fetchCategories();
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const user = auth.currentUser;
      if (!user) {
        alert("You must be signed in");
        return;
      }

      const token = await user.getIdToken();

      const response = await api.post("/admin/trends", form, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      alert("Trend created successfully! ✅");
      console.log("Created trend:", response.data);

      // Reset form
      setForm({
        title: "",
        description: "",
        why_it_matters: "",
        how_to_talk_about_it: "",
        category_id: "",
        relevance_score: 0.85,
        sources: "",
        week_start: "",
        week_end: "",
      });
    } catch (err) {
      console.error("Error creating trend:", err);
      alert(`Error: ${err.response?.data?.detail || "Failed to create trend"}`);
    }
  };

  return (
    <div className="admin-container">
      <div className="admin-card">
        <h2 className="admin-title">Create New Trend</h2>
        <p className="admin-subtitle">Add manually curated trends to TAPIN</p>

        <form onSubmit={handleSubmit} className="admin-form">
          <div className="form-group">
            <label>Title *</label>
            <input
              name="title"
              placeholder="e.g., Rizz, NPC Streaming, Brat Summer"
              value={form.title}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Description *</label>
            <textarea
              name="description"
              placeholder="Brief explanation of what this trend is..."
              value={form.description}
              onChange={handleChange}
              required
              rows="4"
            />
          </div>

          <div className="form-group">
            <label>Why It Matters</label>
            <textarea
              name="why_it_matters"
              placeholder="Why should parents/teachers care about this?"
              value={form.why_it_matters}
              onChange={handleChange}
              rows="3"
            />
          </div>

          <div className="form-group">
            <label>How to Talk About It</label>
            <textarea
              name="how_to_talk_about_it"
              placeholder="Tips for starting conversations with Gen Z about this..."
              value={form.how_to_talk_about_it}
              onChange={handleChange}
              rows="3"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Category</label>
              <select
                name="category_id"
                value={form.category_id}
                onChange={handleChange}
              >
                <option value="">Select Category (Optional)</option>
                {Array.isArray(categories) &&
                  categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.name}
                    </option>
                  ))}
              </select>
            </div>

            <div className="form-group">
              <label>Relevance Score</label>
              <input
                type="number"
                name="relevance_score"
                value={form.relevance_score}
                onChange={handleChange}
                step="0.01"
                min="0"
                max="1"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Sources</label>
            <input
              name="sources"
              placeholder="URLs, comma separated"
              value={form.sources}
              onChange={handleChange}
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Week Start</label>
              <input
                type="date"
                name="week_start"
                value={form.week_start}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label>Week End</label>
              <input
                type="date"
                name="week_end"
                value={form.week_end}
                onChange={handleChange}
              />
            </div>
          </div>

          <button type="submit" className="admin-submit-btn">
            Create Trend
          </button>
        </form>
      </div>
    </div>
  );
}

export default AdminCreateTrend;
