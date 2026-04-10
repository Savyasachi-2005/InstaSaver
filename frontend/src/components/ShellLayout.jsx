import { Link, useLocation } from "react-router-dom";

const navItems = [
  { to: "/", label: "Home" },
  { to: "/reels", label: "Reels" },
  { to: "/posts", label: "Posts" },
];

function ShellLayout({ children }) {
  const location = useLocation();

  return (
    <div className="soft-grid min-h-screen">
      <header className="sticky top-0 z-20 border-b border-slate-700/50 bg-ink/70 backdrop-blur-lg">
        <div className="mx-auto flex w-full min-w-0 max-w-6xl flex-col items-start gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <Link to="/" className="font-display text-xl font-semibold tracking-wide text-aqua">
            InstaSaver
          </Link>
          <nav className="flex w-full min-w-0 items-center gap-2 overflow-x-auto rounded-full border border-slate-700/70 bg-night/60 p-1 sm:w-auto">
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
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 sm:py-10">{children}</main>
    </div>
  );
}

export default ShellLayout;
