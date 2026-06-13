import { useState, useEffect, useRef } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { api } from "@/lib/api";

export default function Navbar() {
  const [liveCount, setLiveCount] = useState(0);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [searchOpen, setSearchOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const searchRef = useRef(null);

  // Poll live count for nav badge
  useEffect(() => {
    const fetchCount = async () => {
      try {
        const data = await api.getLiveCount("football");
        setLiveCount(data.count || 0);
      } catch { /* silent */ }
    };
    fetchCount();
    const id = setInterval(fetchCount, 30_000);
    return () => clearInterval(id);
  }, []);

  // Search with debounce
  useEffect(() => {
    if (!query.trim() || query.length < 2) { setResults([]); return; }
    const id = setTimeout(async () => {
      try {
        const data = await api.search(query);
        setResults(data.data || []);
      } catch { setResults([]); }
    }, 300);
    return () => clearTimeout(id);
  }, [query]);

  // Close search on outside click
  useEffect(() => {
    const handler = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setSearchOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleResultClick = (result) => {
    setSearchOpen(false);
    setQuery("");
    navigate(`/football/competition/${result.id}`);
  };

  const navLinks = [
    { label: "Home", to: "/" },
    { label: "Live", to: "/football/scores/live", badge: liveCount },
    { label: "Scores", to: "/football/scores/live" },
    { label: "World Cup", to: "/football/competition/1" },
    { label: "Premier League", to: "/football/competition/39" },
  ];

  return (
    <nav className="sticky top-0 z-40 bg-pitch-mid/95 backdrop-blur border-b border-white/5">
      <div className="max-w-screen-xl mx-auto px-4">
        <div className="flex items-center h-14 gap-4">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 shrink-0">
            <span className="text-2xl font-display font-bold text-brand-500 tracking-wide">
              LIVE<span className="text-white">SCORE</span>
            </span>
          </Link>

          {/* Desktop nav links */}
          <div className="hidden md:flex items-center gap-1 flex-1">
            {navLinks.map((link) => (
              <Link
                key={link.to + link.label}
                to={link.to}
                className="relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-slate-300 hover:text-white hover:bg-white/5 transition-colors"
              >
                {link.label}
                {link.badge > 0 && (
                  <span className="flex items-center gap-1 bg-green-500/20 text-green-400 text-xs px-1.5 py-0.5 rounded-full font-mono leading-none">
                    <span className="live-dot w-1.5 h-1.5" />
                    {link.badge}
                  </span>
                )}
              </Link>
            ))}
          </div>

          {/* Search */}
          <div ref={searchRef} className="relative ml-auto">
            {searchOpen ? (
              <div className="absolute right-0 top-0 w-72">
                <input
                  autoFocus
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onBlur={() => setTimeout(() => setSearchOpen(false), 150)}
                  placeholder="Search competitions..."
                  className="w-full bg-pitch-dark border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500/50"
                />
                {results.length > 0 && (
                  <div className="absolute top-full mt-1 w-full bg-pitch-mid border border-white/10 rounded-lg shadow-xl overflow-hidden z-50">
                    {results.map((r) => (
                      <button
                        key={r.id}
                        onClick={() => handleResultClick(r)}
                        className="w-full flex items-center gap-3 px-3 py-2.5 text-left text-sm hover:bg-white/5 transition-colors"
                      >
                        <span className="text-slate-300">{r.name}</span>
                        <span className="text-slate-500 text-xs ml-auto">{r.country}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={() => setSearchOpen(true)}
                className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
                aria-label="Search"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="md:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
            aria-label="Menu"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={menuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
            </svg>
          </button>
        </div>

        {/* Mobile nav */}
        {menuOpen && (
          <div className="md:hidden pb-3 border-t border-white/5 pt-2 animate-slide-up">
            {navLinks.map((link) => (
              <Link
                key={link.to + link.label}
                to={link.to}
                onClick={() => setMenuOpen(false)}
                className="flex items-center justify-between px-3 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-white/5"
              >
                {link.label}
                {link.badge > 0 && (
                  <span className="text-green-400 text-xs font-mono">{link.badge} live</span>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
}
