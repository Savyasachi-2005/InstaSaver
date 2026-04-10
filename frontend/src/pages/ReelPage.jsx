import { useMemo, useState } from "react";
import toast from "react-hot-toast";

import HistoryPanel from "../components/HistoryPanel";
import LoadingSpinner from "../components/LoadingSpinner";
import { fetchReel } from "../services/api";
import { downloadMedia, getStreamUrl } from "../utils/download";
import { pushHistory, loadHistory } from "../utils/storage";
import { isValidReelUrl } from "../utils/validators";

function ReelPage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [media, setMedia] = useState([]);
  const [history, setHistory] = useState(loadHistory());

  const activeMedia = useMemo(() => media[0], [media]);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!isValidReelUrl(url)) {
      toast.error("Please enter a valid Instagram Reel URL.");
      return;
    }

    setLoading(true);
    setMedia([]);
    setProgress(15);

    const timer = window.setInterval(() => {
      setProgress((prev) => (prev >= 90 ? 90 : prev + 8));
    }, 220);

    try {
      const response = await fetchReel(url.trim());
      setMedia(response.media || []);
      setProgress(100);
      toast.success("Reel fetched successfully");
      setHistory(
        pushHistory({
          id: crypto.randomUUID(),
          kind: "reel",
          source: url.trim(),
          createdAt: new Date().toISOString(),
        })
      );
    } catch (error) {
      const message = error?.response?.data?.detail || "Failed to fetch reel.";
      toast.error(message);
    } finally {
      window.clearInterval(timer);
      setTimeout(() => setProgress(0), 500);
      setLoading(false);
    }
  };

  const copyLink = async () => {
    if (!activeMedia?.media_url) return;
    await navigator.clipboard.writeText(activeMedia.media_url);
    toast.success("Download link copied");
  };

  const handleDownload = async () => {
    if (!activeMedia?.media_url) return;
    try {
      await downloadMedia(activeMedia.media_url, "instagram-reel.mp4");
      toast.success("Download started");
    } catch {
      toast.error("Unable to download this media file.");
    }
  };

  return (
    <section className="grid gap-6 lg:grid-cols-[2fr,1fr]">
      <div className="min-w-0 space-y-6">
        <div className="card-glass p-5 sm:p-6">
          <h1 className="font-display text-2xl text-white sm:text-3xl">Download Instagram Reels</h1>
          <p className="mt-2 text-slate-300">Paste a Reel URL, preview instantly, then save the video.</p>

          <form onSubmit={handleSubmit} className="mt-5 space-y-3">
            <input
              type="url"
              inputMode="url"
              placeholder="https://www.instagram.com/reel/..."
              className="w-full min-w-0 rounded-xl border border-slate-600 bg-night/80 px-4 py-3 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-aqua/70"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
            />
            <button
              type="submit"
              disabled={loading}
              className="inline-flex w-full items-center justify-center rounded-xl bg-gradient-to-r from-aqua/85 to-mist/90 px-5 py-3 font-medium text-slate-950 transition hover:brightness-110 sm:w-auto disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? <LoadingSpinner label="Processing" /> : "Download Reel"}
            </button>
          </form>

          {progress > 0 && (
            <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-700/80">
              <div className="h-full rounded-full bg-gradient-to-r from-aqua to-mist transition-all" style={{ width: `${progress}%` }} />
            </div>
          )}
        </div>

        {activeMedia && (
          <div className="card-glass animate-[fadeIn_300ms_ease-in-out] p-5 sm:p-6">
            <h2 className="font-display text-xl text-white">Preview</h2>
            <video controls className="mt-4 max-h-[520px] w-full rounded-xl border border-slate-700/70" src={getStreamUrl(activeMedia.media_url)} />
            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <button
                type="button"
                onClick={handleDownload}
                className="rounded-xl border border-aqua/60 bg-aqua/20 px-4 py-2 text-sm text-aqua transition hover:bg-aqua/30"
              >
                Download Video
              </button>
              <button
                type="button"
                onClick={copyLink}
                className="rounded-xl border border-slate-600 px-4 py-2 text-sm text-slate-200 transition hover:border-mist/70 hover:text-mist"
              >
                Copy Link
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="min-w-0">
        <HistoryPanel items={history.filter((item) => item.kind === "reel")} />
      </div>
    </section>
  );
}

export default ReelPage;
