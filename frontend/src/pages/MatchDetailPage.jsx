/**
 * Match Detail Page — score header, timeline, stats, lineups.
 */
import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useMatchDetail, useLineups } from "@/hooks/useData";
import MatchTimeline from "@/components/match/MatchTimeline";
import MatchStats from "@/components/match/MatchStats";
import LineupDisplay from "@/components/match/LineupDisplay";
import StatusBadge from "@/components/ui/StatusBadge";
import TeamLogo from "@/components/ui/TeamLogo";
import AdSlot from "@/components/ads/AdSlot";
import Spinner from "@/components/ui/Spinner";
import ErrorMessage from "@/components/ui/ErrorMessage";
import { formatKickoffFull, formatKickoffUtc } from "@/lib/time";
import { injectMatchStructuredData, setPageMeta, matchPageTitle } from "@/lib/seo";

const TABS = ["Overview", "Timeline", "Stats", "Lineups"];

const STATUS_LABELS = {
  ns: "Scheduled",
  live: "Live",
  ht: "Half-time",
  ft: "Finished",
  postponed: "Postponed",
  cancelled: "Cancelled",
  abandoned: "Abandoned",
};

function valueOrFallback(value, fallback = "TBC") {
  return value === null || value === undefined || value === "" ? fallback : value;
}

function DetailCard({ label, value, subValue, icon }) {
  return (
    <div className="rounded-xl bg-pitch-dark/70 border border-white/5 p-4">
      <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-slate-500 mb-1">
        <span>{icon}</span>
        <span>{label}</span>
      </div>
      <div className="text-sm font-semibold text-slate-100">{value}</div>
      {subValue && <div className="text-xs text-slate-500 mt-1">{subValue}</div>}
    </div>
  );
}

function MatchOverview({ match, lineups }) {
  const venue = match.venue_detail?.full_name || match.venue || match.venue_detail?.name;
  const venueSub = [match.venue_detail?.city, match.venue_detail?.country].filter(Boolean).join(", ");
  const statusLabel = STATUS_LABELS[match.status] || match.status || "Unknown";
  const hasEvents = (match.events || []).length > 0;
  const lineupTeams = Object.keys(lineups || {});

  return (
    <div className="space-y-5">
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <DetailCard
          icon="🕒"
          label="Kickoff"
          value={formatKickoffFull(match.kickoff_utc)}
          subValue={`UTC: ${formatKickoffUtc(match.kickoff_utc)}`}
        />
        <DetailCard
          icon="🏟️"
          label="Stadium / Venue"
          value={valueOrFallback(venue, "Venue TBC")}
          subValue={venueSub}
        />
        <DetailCard
          icon="🧑‍⚖️"
          label="Referee"
          value={valueOrFallback(match.referee, "Not announced")}
        />
        <DetailCard
          icon="📡"
          label="Match status"
          value={statusLabel}
          subValue={match.minute ? `${match.minute}' played` : null}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl bg-pitch-dark/50 border border-white/5 p-4">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">Goals, cards & substitutions</h3>
          {hasEvents ? (
            <MatchTimeline events={(match.events || []).slice(0, 6)} compact />
          ) : (
            <p className="text-slate-500 text-sm">No goals, cards, or substitutions have been reported yet.</p>
          )}
        </div>
        <div className="rounded-xl bg-pitch-dark/50 border border-white/5 p-4">
          <h3 className="text-sm font-semibold text-slate-200 mb-3">Team lineups</h3>
          {lineupTeams.length >= 2 ? (
            <div className="space-y-2 text-sm text-slate-300">
              {lineupTeams.map((team) => (
                <div key={team} className="flex justify-between gap-3">
                  <span>{team}</span>
                  <span className="text-slate-500">{lineups[team]?.formation || "Formation TBC"}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 text-sm">Lineups are usually published around an hour before kickoff.</p>
          )}
        </div>
      </div>
    </div>
  );
}

function ScoreHeader({ match, isLive }) {
  return (
    <div className="bg-pitch-mid border border-white/5 rounded-2xl p-6 mb-6">
      <div className="flex items-center gap-2 justify-center mb-4">
        {match.competition_logo && (
          <img src={match.competition_logo} alt={match.competition} className="w-5 h-5 object-contain" />
        )}
        <span className="text-slate-400 text-sm">{match.competition}</span>
        <StatusBadge status={match.status} minute={match.minute} />
      </div>
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 flex flex-col items-center gap-2">
          <TeamLogo src={match.home_logo} name={match.home_team} size={56} />
          <span className="text-center font-semibold text-slate-200 text-sm leading-tight">{match.home_team}</span>
        </div>
        <div className="flex flex-col items-center gap-1 shrink-0">
          {match.home_score != null ? (
            <div className="flex items-center gap-3">
              <span className={`font-display text-5xl font-bold tabular-nums ${isLive ? "text-green-400" : "text-white"}`}>{match.home_score}</span>
              <span className="text-slate-600 text-3xl">—</span>
              <span className={`font-display text-5xl font-bold tabular-nums ${isLive ? "text-green-400" : "text-white"}`}>{match.away_score}</span>
            </div>
          ) : (
            <div className="font-display text-2xl font-bold text-slate-400">{formatKickoffFull(match.kickoff_utc)}</div>
          )}
          {match.ht_home != null && <span className="text-slate-500 text-xs">HT: {match.ht_home}–{match.ht_away}</span>}
          {match.venue && <span className="text-slate-500 text-xs mt-1">📍 {match.venue}</span>}
        </div>
        <div className="flex-1 flex flex-col items-center gap-2">
          <TeamLogo src={match.away_logo} name={match.away_team} size={56} />
          <span className="text-center font-semibold text-slate-200 text-sm leading-tight">{match.away_team}</span>
        </div>
      </div>
    </div>
  );
}

export default function MatchDetailPage() {
  const { matchId, sport = "football" } = useParams();
  const { match, isLive, isLoading, isError } = useMatchDetail(matchId, sport);
  const { lineups } = useLineups(matchId, sport);
  const [activeTab, setActiveTab] = useState("Overview");

  useEffect(() => {
    if (match) {
      setPageMeta(matchPageTitle(match));
      injectMatchStructuredData(match);
    }
  }, [match]);

  if (isLoading) return <div className="flex justify-center py-20"><Spinner size={40} /></div>;
  if (isError || !match) return <ErrorMessage message="Match not found or data unavailable." />;

  return (
    <div className="animate-fade-in">
      <nav className="flex items-center gap-1.5 text-xs text-slate-500 mb-4">
        <Link to="/" className="hover:text-slate-300 transition-colors">Home</Link><span>›</span>
        <Link to={`/${sport}/scores/live`} className="hover:text-slate-300 transition-colors">Scores</Link><span>›</span>
        <span className="text-slate-400">{match.home_team} vs {match.away_team}</span>
      </nav>

      <ScoreHeader match={match} isLive={isLive} />
      <div className="mb-4"><AdSlot slot="in_article" /></div>

      <div className="flex gap-1 bg-pitch-mid rounded-xl p-1 mb-4">
        {TABS.map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)} className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab ? "bg-pitch-dark text-white shadow" : "text-slate-400 hover:text-white"}`}>{tab}</button>
        ))}
      </div>

      <div className="bg-pitch-mid border border-white/5 rounded-xl p-4">
        {activeTab === "Overview" && <MatchOverview match={match} lineups={lineups} />}
        {activeTab === "Timeline" && <MatchTimeline events={match.events || []} />}
        {activeTab === "Stats" && <MatchStats statistics={match.statistics || {}} homeTeam={match.home_team} awayTeam={match.away_team} />}
        {activeTab === "Lineups" && <LineupDisplay lineups={lineups} />}
      </div>
    </div>
  );
}
