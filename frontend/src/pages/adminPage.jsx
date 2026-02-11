import { useState } from "react";

function AdminCreateTrend() {
    const [categories, setCategories] = useState([]);
    const [form, setForm] = useState({
        title: "",
        description: "",
        why_it_matters: "",
        how_to_talk_about_it: "",
        category_id: "",
        relevance_score: 0,
        sources: "",
        week_start: "",
        week_end: "",
    });

    useEffect(() => {
    const fetchCategories = async () => {
      const res = await fetch("/categories");
      const data = await res.json();
      setCategories(data);
    };
    fetchCategories();
  }, []);
  
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const res = await fetch("/admin/trends", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify(form),
    });

    if (res.ok) {
      alert("Trend created!");
    } else {
      alert("Error creating trend");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="title" placeholder="Title" onChange={handleChange} />
      <textarea name="description" placeholder="Description" onChange={handleChange} />
      <textarea name="why_it_matters" placeholder="Why it matters" onChange={handleChange} />
      <textarea name="how_to_talk_about_it" placeholder="How to talk about it" onChange={handleChange} />
      <input name="sources" placeholder="Sources (URLs)" onChange={handleChange} />
      <input type="number" name="relevance_score" onChange={handleChange} />
      <input type="date" name="week_start" onChange={handleChange} />
      <input type="date" name="week_end" onChange={handleChange} />

      <button type="submit">Create Trend</button>
    </form>
  );
}

export default AdminCreateTrend;
