import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
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
