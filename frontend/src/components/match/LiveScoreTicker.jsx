/**
 * LiveScoreTicker — real-time score list grouped by competition.
 * Connects via SSE, falls back to polling.
 * Injects AdSlot every AD_INTERVAL competitions.
 */
import { useMemo } from "react";
import { useLiveScores } from "@/hooks/useLiveScores";
import MatchCard, { MatchCardSkeleton } from "./MatchCard";
import AdSlot from "@/components/ads/AdSlot";
import TeamLogo from "@/components/ui/TeamLogo";

const AD_INTERVAL = 4; // Insert ad after every N competitions

function groupByCompetition(matches) {
  return matches.reduce((groups, match) => {
    const key = match.competition || "Other";
    if (!groups[key]) groups[key] = { name: key, logo: match.competition_logo, matches: [] };
    groups[key].matches.push(match);
    return groups;
  }, {});
}

export default function LiveScoreTicker({ sport = "football" }) {
  const { matches, status } = useLiveScores(sport);

  const grouped = useMemo(() => {
    const g = groupByCompetition(matches);
    return Object.values(g);
  }, [matches]);

  if (status === "connecting") {
    return (
      <div className="space-y-2">
        {Array.from({ length: 4 }).map((_, i) => <MatchCardSkeleton key={i} />)}
      </div>
    );
  }

  if (grouped.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="text-5xl mb-4">⚽</div>
        <p className="text-slate-400 text-lg">No live matches right now.</p>
        <p className="text-slate-500 text-sm mt-1">Check back during kick-off times.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Status bar */}
      <div className="flex items-center gap-2 text-xs text-slate-500">
        {status === "live" && (
          <>
            <span className="live-dot" />
            <span className="text-green-400">Live</span>
          </>
        )}
        {status === "stale" && <span className="text-amber-400">⚠ Data may be delayed</span>}
        <span className="ml-auto">{matches.length} matches</span>
      </div>

      {grouped.map((group, groupIdx) => (
        <div key={group.name}>
          {/* Competition header */}
          <div className="flex items-center gap-2 px-2 mb-2">
            {group.logo && (
              <img src={group.logo} alt={group.name} className="w-4 h-4 object-contain opacity-80" />
            )}
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              {group.name}
            </h3>
            <div className="flex-1 h-px bg-white/5 ml-2" />
          </div>

          {/* Match cards */}
          <div className="space-y-1">
            {group.matches.map((match) => (
              <MatchCard key={match.match_id} match={match} sport={sport} />
            ))}
          </div>

          {/* In-feed ad after every AD_INTERVAL groups */}
          {(groupIdx + 1) % AD_INTERVAL === 0 && (
            <div className="mt-4">
              <AdSlot slot="in_feed" index={Math.floor(groupIdx / AD_INTERVAL)} />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
