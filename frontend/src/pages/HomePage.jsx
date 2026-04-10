import { Link } from "react-router-dom";

const cards = [
  {
    title: "Download Reels",
    description: "Paste any supported Reel link and instantly get a preview with direct download.",
    to: "/reels",
  },
  {
    title: "Download Posts",
    description: "Paste a public post URL and save image or video media in one click.",
    to: "/posts",
  },
];

function HomePage() {
  return (
    <section className="space-y-8">
      <div className="card-glass relative overflow-hidden p-6 sm:p-10">
        <div className="absolute -left-10 -top-16 h-44 w-44 rounded-full bg-aqua/15 blur-3xl" />
        <div className="absolute -bottom-14 -right-8 h-40 w-40 rounded-full bg-mist/20 blur-3xl" />
        <p className="relative text-xs uppercase tracking-[0.25em] text-mist">Fast • Private • Clean</p>
        <h1 className="relative mt-3 max-w-3xl font-display text-3xl font-bold leading-tight text-white sm:text-5xl">
          Save Instagram Reels and Posts with a focused, modern workflow.
        </h1>
        <p className="relative mt-4 max-w-2xl text-slate-300 sm:text-lg">
          InstaSaver separates Reels and Posts into dedicated tools so your downloads stay quick and predictable.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        {cards.map((card) => (
          <Link
            key={card.to}
            to={card.to}
            className="card-glass group p-6 transition duration-300 hover:-translate-y-1 hover:border-aqua/50 hover:shadow-glow"
          >
            <h2 className="font-display text-2xl text-white">{card.title}</h2>
            <p className="mt-3 text-slate-300">{card.description}</p>
            <span className="mt-5 inline-block rounded-full border border-slate-600 px-4 py-1 text-sm text-slate-200 transition group-hover:border-aqua/70 group-hover:text-aqua">
              Open Tool
            </span>
          </Link>
        ))}
      </div>
    </section>
  );
}

export default HomePage;
