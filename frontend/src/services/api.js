import axios from "axios";

let API_URL = import.meta.env.DEV
  ? "http://localhost:8000"
  : import.meta.env.VITE_API_URL;

API_URL = `${API_URL}/api`;

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const getWeeklyTrends = async () => {
  const { data } = await api.get("/trends/weekly");
  return data;
};

export const getTrendById = async (id) => {
  const { data } = await api.get(`/trends/${id}`);
  return data;
};

export const getTrendsByCategory = async (category) => {
  const { data } = await api.get(`/trends/category/${category}`);
  return data;
};

export const getCategories = async () => {
  const { data } = await api.get("/categories");
  return data;
};

export const getArchive = async (page = 1, limit = 10) => {
  const { data } = await api.get(`/trends/archive?page=${page}&limit=${limit}`);
  return data;
};

export const getArchiveWeek = async (weekStart) => {
  const { data } = await api.get(`/trends/archive/${weekStart}`);
  return data;
};

export { api };
