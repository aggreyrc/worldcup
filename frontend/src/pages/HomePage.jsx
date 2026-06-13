/**
 * Home Page — featured competitions, live ticker, upcoming fixtures.
 */
import { useEffect } from "react";
import { Link } from "react-router-dom";
import { useFixtures, useFeaturedCompetitions } from "@/hooks/useData";
import { useLiveScores } from "@/hooks/useLiveScores";
import MatchCard, { MatchCardSkeleton } from "@/components/match/MatchCard";
import FixtureList from "@/components/competition/FixtureList";
import AdSlot from "@/components/ads/AdSlot";
import { setPageMeta } from "@/lib/seo";

function HeroBanner({ liveCount }) {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-pitch-light to-pitch-mid border border-white/5 p-6 mb-6">
      <div className="absolute inset-0 opacity-5">
        <div className="absolute top-4 right-8 text-9xl">⚽</div>
      </div>
      <div className="relative">
        <h1 className="font-display text-4xl md:text-5xl font-bold text-white mb-2">
          LIVE <span className="text-brand-500">SCORES</span>
        </h1>
        <p className="text-slate-400 text-sm md:text-base">
          Real-time scores for World Cup 2026, Premier League, Champions League and more.
        </p>
        {liveCount > 0 && (
          <Link
            to="/football/scores/live"
            className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-sm font-medium transition-colors"
          >
            <span className="live-dot" />
            {liveCount} matches live now →
          </Link>
        )}
      </div>
    </div>
  );
}

function FeaturedCompetitions({ competitions }) {
  const featured = [
    { id: "1",   name: "World Cup",         flag: "🌍", season: "2026" },
    { id: "2",   name: "Champions League",  flag: "🏆", season: "2025" },
    { id: "39",  name: "Premier League",    flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿", season: "2025" },
    { id: "140", name: "La Liga",           flag: "🇪🇸", season: "2025" },
    { id: "78",  name: "Bundesliga",        flag: "🇩🇪", season: "2025" },
    { id: "135", name: "Serie A",           flag: "🇮🇹", season: "2025" },
    { id: "61",  name: "Ligue 1",           flag: "🇫🇷", season: "2025" },
    { id: "197", name: "AFCON",             flag: "🌍", season: "2025" },
  ];

  return (
    <div className="mb-6">
      <h2 className="font-display text-xl font-bold text-white mb-3">Competitions</h2>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {featured.map((comp) => (
          <Link
            key={comp.id}
            to={`/football/competition/${comp.id}`}
            className="flex items-center gap-2.5 bg-pitch-mid hover:bg-pitch-light border border-white/5 rounded-xl px-3 py-2.5 transition-colors group"
          >
            <span className="text-xl">{comp.flag}</span>
            <div className="min-w-0">
              <div className="text-sm font-medium text-slate-200 group-hover:text-white truncate transition-colors">
                {comp.name}
              </div>
              <div className="text-xs text-slate-500">{comp.season}</div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default function HomePage() {
  const { matches: liveMatches, status } = useLiveScores("football");
  const { fixtures, isLoading: fixturesLoading } = useFixtures("football");

  useEffect(() => {
    setPageMeta(
      "LiveScore — Live Football Scores & Fixtures",
      "Real-time football scores, fixtures and standings for World Cup 2026, Premier League, Champions League and all major competitions."
    );
  }, []);

  return (
    <div className="space-y-8 animate-fade-in">
      <HeroBanner liveCount={liveMatches.length} />

      <AdSlot slot="in_article" />

      <FeaturedCompetitions />

      {/* Live Scores Section */}
      {(status !== "connecting" || liveMatches.length > 0) && (
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-display text-xl font-bold text-white flex items-center gap-2">
              <span className="live-dot" />
              Live Now
            </h2>
            {liveMatches.length > 0 && (
              <Link to="/football/scores/live" className="text-sm text-brand-500 hover:text-brand-400 transition-colors">
                View all →
              </Link>
            )}
          </div>

          {status === "connecting" ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => <MatchCardSkeleton key={i} />)}
            </div>
          ) : liveMatches.length === 0 ? (
            <div className="bg-pitch-mid border border-white/5 rounded-xl px-4 py-8 text-center">
              <p className="text-slate-400 text-sm">No matches live right now. Check fixtures below.</p>
            </div>
          ) : (
            <div className="space-y-1">
              {liveMatches.slice(0, 6).map((match) => (
                <MatchCard key={match.match_id} match={match} />
              ))}
              {liveMatches.length > 6 && (
                <Link
                  to="/football/scores/live"
                  className="flex items-center justify-center py-3 text-sm text-brand-500 hover:text-brand-400 transition-colors bg-pitch-mid rounded-xl border border-white/5"
                >
                  +{liveMatches.length - 6} more live matches →
                </Link>
              )}
            </div>
          )}
        </section>
      )}

      {/* Upcoming Fixtures */}
      <section>
        <h2 className="font-display text-xl font-bold text-white mb-3">Upcoming Fixtures</h2>
        <FixtureList
          fixtures={fixtures.filter((f) => f.status === "ns")}
          isLoading={fixturesLoading}
        />
      </section>
    </div>
  );
}
