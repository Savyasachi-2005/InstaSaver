function HistoryPanel({ items }) {
  if (!items.length) {
    return (
      <section className="card-glass p-4 sm:p-5">
        <h3 className="font-display text-lg text-slate-100">Recent Downloads</h3>
        <p className="mt-2 text-sm text-slate-400">No downloads yet. Your latest successful downloads will appear here.</p>
      </section>
    );
  }

  return (
    <section className="card-glass p-4 sm:p-5">
      <h3 className="font-display text-lg text-slate-100">Recent Downloads</h3>
      <div className="mt-3 space-y-2">
        {items.slice(0, 6).map((item) => (
          <div key={item.id} className="rounded-xl border border-slate-700/60 bg-night/60 p-3">
            <p className="text-xs uppercase tracking-wide text-mist">{item.kind}</p>
            <p className="mt-1 truncate text-sm text-slate-200">{item.source}</p>
            <p className="mt-1 text-xs text-slate-400">{new Date(item.createdAt).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default HistoryPanel;
