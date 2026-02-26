import { useState, useEffect } from "react";
import { auth } from "../firebase";
import { api, getCategories } from "../services/api";

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
        setCategories(data);
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
      // Get Firebase auth token
      const user = auth.currentUser;
      if (!user) {
        alert("You must be signed in");
        return;
      }

      const token = await user.getIdToken();

      // Create trend via API
      const response = await api.post("/admin/trends", form, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      alert("Trend created successfully!");
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
    <div style={{ maxWidth: "600px", margin: "2rem auto", padding: "2rem" }}>
      <h2>Create New Trend</h2>
      <form
        onSubmit={handleSubmit}
        style={{ display: "flex", flexDirection: "column", gap: "1rem" }}
      >
        <input
          name="title"
          placeholder="Title"
          value={form.title}
          onChange={handleChange}
          required
          style={{ padding: "0.5rem" }}
        />

        <textarea
          name="description"
          placeholder="Description"
          value={form.description}
          onChange={handleChange}
          required
          rows="4"
          style={{ padding: "0.5rem" }}
        />

        <textarea
          name="why_it_matters"
          placeholder="Why it matters"
          value={form.why_it_matters}
          onChange={handleChange}
          rows="3"
          style={{ padding: "0.5rem" }}
        />

        <textarea
          name="how_to_talk_about_it"
          placeholder="How to talk about it"
          value={form.how_to_talk_about_it}
          onChange={handleChange}
          rows="3"
          style={{ padding: "0.5rem" }}
        />

        <select
          name="category_id"
          value={form.category_id}
          onChange={handleChange}
          style={{ padding: "0.5rem" }}
        >
          <option value="">Select Category (Optional)</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>

        <input
          name="sources"
          placeholder="Sources (URLs, comma separated)"
          value={form.sources}
          onChange={handleChange}
          style={{ padding: "0.5rem" }}
        />

        <label>
          Relevance Score:
          <input
            type="number"
            name="relevance_score"
            value={form.relevance_score}
            onChange={handleChange}
            step="0.01"
            min="0"
            max="1"
            style={{ padding: "0.5rem", marginLeft: "0.5rem" }}
          />
        </label>

        <label>
          Week Start:
          <input
            type="date"
            name="week_start"
            value={form.week_start}
            onChange={handleChange}
            style={{ padding: "0.5rem", marginLeft: "0.5rem" }}
          />
        </label>

        <label>
          Week End:
          <input
            type="date"
            name="week_end"
            value={form.week_end}
            onChange={handleChange}
            style={{ padding: "0.5rem", marginLeft: "0.5rem" }}
          />
        </label>

        <button
          type="submit"
          style={{
            padding: "0.75rem",
            background: "#012b2b",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "1rem",
          }}
        >
          Create Trend
        </button>
      </form>
    </div>
  );
}

export default AdminCreateTrend;
