import { useState } from "react";
import toast from "react-hot-toast";

import HistoryPanel from "../components/HistoryPanel";
import LoadingSpinner from "../components/LoadingSpinner";
import { fetchPost } from "../services/api";
import { downloadMedia, getStreamUrl } from "../utils/download";
import { loadHistory, pushHistory } from "../utils/storage";
import { isValidPostUrl } from "../utils/validators";

function PostPage() {
  const [url, setUrl] = useState("");
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [history, setHistory] = useState(loadHistory());

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!isValidPostUrl(url)) {
      toast.error("Enter a valid Instagram Post URL.");
      return;
    }

    setLoading(true);
    setPosts([]);
    setProgress(15);

    const timer = window.setInterval(() => {
      setProgress((prev) => (prev >= 90 ? 90 : prev + 8));
    }, 220);

    try {
      const response = await fetchPost(url.trim());
      const media = response.media || [];
      setPosts(media);
      setProgress(100);
      toast.success(`Fetched ${media.length} post item${media.length === 1 ? "" : "s"}`);
      setHistory(
        pushHistory({
          id: crypto.randomUUID(),
          kind: "post",
          source: url.trim(),
          createdAt: new Date().toISOString(),
        })
      );
    } catch (error) {
      const message = error?.response?.data?.detail || "Failed to fetch post.";
      toast.error(message);
    } finally {
      window.clearInterval(timer);
      setTimeout(() => setProgress(0), 500);
      setLoading(false);
    }
  };

  const copyPostLink = async (value) => {
    await navigator.clipboard.writeText(value);
    toast.success("Link copied");
  };

  const handlePostDownload = async (mediaUrl, mediaType) => {
    const extension = mediaType === "video" ? "mp4" : "jpg";
    try {
      await downloadMedia(mediaUrl, `instagram-post.${extension}`);
      toast.success("Download started");
    } catch {
      toast.error("Unable to download this media file.");
    }
  };

  return (
    <section className="grid gap-6 lg:grid-cols-[2fr,1fr]">
      <div className="min-w-0 space-y-6">
        <div className="card-glass p-5 sm:p-6">
          <h1 className="font-display text-2xl text-white sm:text-3xl">Download Instagram Posts</h1>
          <p className="mt-2 text-slate-300">Paste a public post URL to fetch image/video media and download instantly.</p>

          <form onSubmit={handleSubmit} className="mt-5 space-y-3">
            <input
              type="url"
              inputMode="url"
              placeholder="https://www.instagram.com/p/..."
              className="w-full min-w-0 rounded-xl border border-slate-600 bg-night/80 px-4 py-3 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-aqua/70"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
            />
            <button
              type="submit"
              disabled={loading}
              className="inline-flex w-full items-center justify-center rounded-xl bg-gradient-to-r from-mist/90 to-aqua/85 px-5 py-3 font-medium text-slate-950 transition hover:brightness-110 sm:w-auto disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? <LoadingSpinner label="Fetching" /> : "Get Post"}
            </button>
          </form>

          {progress > 0 && (
            <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-700/80">
              <div className="h-full rounded-full bg-gradient-to-r from-aqua to-mist transition-all" style={{ width: `${progress}%` }} />
            </div>
          )}
        </div>

        {!!posts.length && (
          <div className="grid gap-4 sm:grid-cols-2">
            {posts.map((item) => (
              <article key={item.id} className="card-glass overflow-hidden p-3">
                <div className="overflow-hidden rounded-lg border border-slate-700/70 bg-black/40">
                  {item.media_type === "video" ? (
                    <video controls src={getStreamUrl(item.media_url)} className="h-56 w-full object-cover sm:h-64" />
                  ) : (
                    <img src={getStreamUrl(item.media_url)} alt={item.title || "Instagram post"} className="h-56 w-full object-cover sm:h-64" />
                  )}
                </div>
                <div className="mt-3 flex flex-col gap-2 sm:flex-row">
                  <button
                    type="button"
                    onClick={() => handlePostDownload(item.media_url, item.media_type)}
                    className="rounded-lg border border-aqua/60 bg-aqua/15 px-3 py-1.5 text-sm text-aqua transition hover:bg-aqua/25"
                  >
                    Download
                  </button>
                  <button
                    type="button"
                    onClick={() => copyPostLink(item.media_url)}
                    className="rounded-lg border border-slate-600 px-3 py-1.5 text-sm text-slate-200 transition hover:border-mist/70 hover:text-mist"
                  >
                    Copy Link
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>

      <div className="min-w-0">
        <HistoryPanel items={history.filter((item) => item.kind === "post")} />
      </div>
    </section>
  );
}

export default PostPage;
