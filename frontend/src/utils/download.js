function normalizeApiBase(input) {
  const base = (input || "http://localhost:8000/api").replace(/\/+$/, "");
  return /\/api$/i.test(base) ? base : `${base}/api`;
}

const API_BASE = normalizeApiBase(import.meta.env.VITE_API_BASE_URL);

/**
 * Build a proxied stream URL for media preview (video/image).
 * Routes through the backend to avoid Instagram CDN CORS blocks.
 */
export function getStreamUrl(mediaUrl) {
  return `${API_BASE}/download/stream?url=${encodeURIComponent(mediaUrl)}`;
}

export async function downloadMedia(url, filename = "media") {
  const downloadUrl = `${API_BASE}/download/file?url=${encodeURIComponent(url)}&filename=${encodeURIComponent(filename)}`;
  const response = await fetch(downloadUrl);

  if (!response.ok) {
    throw new Error("Download failed.");
  }

  const blob = await response.blob();
  const objectUrl = window.URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  window.URL.revokeObjectURL(objectUrl);
}

