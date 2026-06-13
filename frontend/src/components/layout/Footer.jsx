import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="mt-12 border-t border-white/5 bg-pitch-mid">
      <div className="max-w-screen-xl mx-auto px-4 py-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div>
            <div className="font-display font-bold text-lg text-brand-500 mb-3">
              LIVE<span className="text-white">SCORE</span>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed">
              Real-time scores for all major football competitions worldwide.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-300 mb-3">Competitions</h4>
            <ul className="space-y-1.5 text-sm text-slate-400">
              <li><Link to="/football/competition/1" className="hover:text-white transition-colors">World Cup 2026</Link></li>
              <li><Link to="/football/competition/2" className="hover:text-white transition-colors">Champions League</Link></li>
              <li><Link to="/football/competition/39" className="hover:text-white transition-colors">Premier League</Link></li>
              <li><Link to="/football/competition/140" className="hover:text-white transition-colors">La Liga</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-300 mb-3">Quick Links</h4>
            <ul className="space-y-1.5 text-sm text-slate-400">
              <li><Link to="/football/scores/live" className="hover:text-white transition-colors">Live Scores</Link></li>
              <li><Link to="/" className="hover:text-white transition-colors">Fixtures</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-slate-300 mb-3">Legal</h4>
            <ul className="space-y-1.5 text-sm text-slate-400">
              <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Cookie Policy</a></li>
            </ul>
          </div>
        </div>
        <div className="mt-8 pt-6 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-3">
          <p className="text-slate-500 text-xs">© {new Date().getFullYear()} LiveScore. All rights reserved.</p>
          <p className="text-slate-600 text-xs">Data provided by API-Football. Not affiliated with FIFA or any football organisation.</p>
        </div>
      </div>
    </footer>
  );
}
