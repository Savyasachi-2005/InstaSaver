import axios from "axios";

function normalizeApiBase(input) {
  const base = (input || "http://localhost:8000/api").replace(/\/+$/, "");
  return /\/api$/i.test(base) ? base : `${base}/api`;
}

const api = axios.create({
  baseURL: normalizeApiBase(import.meta.env.VITE_API_BASE_URL),
  timeout: 20000,
});

export async function fetchReel(url) {
  const { data } = await api.post("/download/reel", { url });
  return data;
}

export async function fetchPost(url) {
  const { data } = await api.post("/download/post", { url });
  return data;
}

export default api;
