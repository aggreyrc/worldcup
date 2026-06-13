/**
 * Competition Page — fixtures + standings for a league or cup.
 */
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useFixtures, useStandings } from "@/hooks/useData";
import FixtureList from "@/components/competition/FixtureList";
import StandingsTable from "@/components/competition/StandingsTable";
import AdSlot from "@/components/ads/AdSlot";
import { setPageMeta } from "@/lib/seo";

const TABS = ["Fixtures", "Standings"];

// Map competition IDs to display info
const COMPETITION_META = {
  "1":   { name: "World Cup 2026",       flag: "🌍" },
  "2":   { name: "Champions League",     flag: "🏆" },
  "39":  { name: "Premier League",       flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿" },
  "140": { name: "La Liga",              flag: "🇪🇸" },
  "78":  { name: "Bundesliga",           flag: "🇩🇪" },
  "135": { name: "Serie A",              flag: "🇮🇹" },
  "61":  { name: "Ligue 1",             flag: "🇫🇷" },
  "197": { name: "AFCON",               flag: "🌍" },
};

export default function CompetitionPage() {
  const { competitionId, sport = "football" } = useParams();
  const [activeTab, setActiveTab] = useState("Fixtures");
  const meta = COMPETITION_META[competitionId] || { name: "Competition", flag: "🏆" };

  const { fixtures, isLoading: fixturesLoading } = useFixtures(sport);
  const { standings, isLoading: standingsLoading } = useStandings(competitionId, "2025", sport);

  // Filter fixtures for this competition
  const compFixtures = fixtures.filter(
    (f) => f.competition_id === competitionId || f.competition?.id === competitionId
  );

  useEffect(() => {
    setPageMeta(
      `${meta.name} — Scores, Fixtures & Standings`,
      `Live scores, fixtures and standings for ${meta.name}. Updated in real time.`
    );
  }, [meta.name]);

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <span className="text-4xl">{meta.flag}</span>
        <div>
          <h1 className="font-display text-3xl font-bold text-white">{meta.name}</h1>
          <p className="text-slate-500 text-sm">Season 2025/26</p>
        </div>
      </div>

      <AdSlot slot="in_article" className="mb-4" />

      {/* Tabs */}
      <div className="flex gap-1 bg-pitch-mid rounded-xl p-1 mb-4">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab
                ? "bg-pitch-dark text-white shadow"
                : "text-slate-400 hover:text-white"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeTab === "Fixtures" && (
        <FixtureList
          fixtures={compFixtures.length ? compFixtures : fixtures}
          isLoading={fixturesLoading}
          sport={sport}
        />
      )}

      {activeTab === "Standings" && (
        <div className="bg-pitch-mid border border-white/5 rounded-xl p-4">
          {standingsLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="skeleton h-8 rounded" />
              ))}
            </div>
          ) : (
            <StandingsTable standings={standings} sport={sport} />
          )}
        </div>
      )}
    </div>
  );
}
