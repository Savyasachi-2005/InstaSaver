import { Link, useLocation } from "react-router-dom";

const navItems = [
  { to: "/", label: "Home" },
  { to: "/reels", label: "Reels" },
  { to: "/posts", label: "Posts" },
];

const repoUrl = "https://github.com/Savyasachi-2005/InstaSaver";

function ShellLayout({ children }) {
  const location = useLocation();

  return (
    <div className="soft-grid min-h-screen">
      <header className="sticky top-0 z-20 border-b border-slate-700/50 bg-ink/70 backdrop-blur-lg">
        <div className="mx-auto flex w-full min-w-0 max-w-6xl flex-col items-start gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <Link to="/" className="font-display text-xl font-semibold tracking-wide text-aqua">
            InstaSaver
          </Link>
          <div className="flex w-full min-w-0 items-center gap-2 sm:w-auto">
            <nav className="flex min-w-0 flex-1 items-center gap-2 overflow-x-auto rounded-full border border-slate-700/70 bg-night/60 p-1 sm:w-auto sm:flex-none">
              {navItems.map((item) => {
                const isActive = location.pathname === item.to;
                return (
                  <Link
                    key={item.to}
                    to={item.to}
                    className={`whitespace-nowrap rounded-full px-4 py-1.5 text-sm transition ${
                      isActive
                        ? "bg-gradient-to-r from-aqua/30 to-mist/35 text-white"
                        : "text-slate-300 hover:text-white"
                    }`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
            <a
              href={repoUrl}
              target="_blank"
              rel="noreferrer"
              aria-label="Open GitHub repository"
              className="inline-flex h-10 w-10 flex-none items-center justify-center rounded-full border border-slate-700/70 bg-night/60 text-slate-300 transition hover:border-aqua/60 hover:text-aqua"
            >
              <svg viewBox="0 0 24 24" className="h-5 w-5" fill="currentColor" aria-hidden="true">
                <path d="M12 .5C5.65.5.5 5.65.5 12a11.5 11.5 0 0 0 7.86 10.92c.57.1.78-.25.78-.55v-2.13c-3.2.7-3.88-1.36-3.88-1.36-.52-1.3-1.27-1.65-1.27-1.65-1.04-.7.08-.69.08-.69 1.15.08 1.75 1.18 1.75 1.18 1.02 1.76 2.68 1.25 3.33.95.1-.74.4-1.25.72-1.54-2.55-.29-5.24-1.27-5.24-5.64 0-1.25.45-2.27 1.18-3.07-.12-.3-.51-1.5.11-3.12 0 0 .97-.31 3.17 1.17a10.97 10.97 0 0 1 5.77 0c2.2-1.48 3.17-1.17 3.17-1.17.62 1.62.23 2.82.11 3.12.73.8 1.18 1.82 1.18 3.07 0 4.38-2.69 5.35-5.26 5.64.41.35.78 1.05.78 2.12v3.14c0 .3.21.65.79.55A11.5 11.5 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z" />
              </svg>
            </a>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 sm:py-10">{children}</main>
    </div>
  );
}

export default ShellLayout;
