function LoadingSpinner({ label = "Loading..." }) {
  return (
    <div className="inline-flex items-center gap-2 text-sm text-slate-300">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-mist/60 border-t-transparent" />
      <span>{label}</span>
    </div>
  );
}

export default LoadingSpinner;
