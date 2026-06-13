/**
 * MatchCard — displays a single match in score lists.
 * Used on Home, Live, and Competition pages.
 */
import { Link } from "react-router-dom";
import { formatKickoff } from "@/lib/time";
import StatusBadge from "@/components/ui/StatusBadge";
import TeamLogo from "@/components/ui/TeamLogo";

export default function MatchCard({ match, sport = "football" }) {
  const isLive = match.status === "live" || match.status === "ht";
  const isFinished = match.status === "ft" || match.status === "aet" || match.status === "pen";
  const hasScore = match.home_score != null && match.away_score != null;

  return (
    <Link
      to={`/${sport}/match/${match.match_id}`}
      className="match-card flex items-center gap-4 px-4 py-3 group"
    >
      {/* Status / time */}
      <div className="w-14 shrink-0 flex flex-col items-center">
        {isLive ? (
          <div className="flex flex-col items-center gap-0.5">
            <span className="live-dot" />
            <span className="text-green-400 text-xs font-mono font-semibold">
              {match.minute ? `${match.minute}'` : "LIVE"}
            </span>
          </div>
        ) : match.status === "ht" ? (
          <span className="text-amber-400 text-xs font-semibold">HT</span>
        ) : isFinished ? (
          <span className="text-slate-400 text-xs">FT</span>
        ) : (
          <span className="text-slate-400 text-sm font-mono">
            {formatKickoff(match.kickoff_utc)}
          </span>
        )}
      </div>

      {/* Teams + score */}
      <div className="flex-1 min-w-0">
        {/* Home team */}
        <div className="flex items-center gap-2 mb-1">
          <TeamLogo src={match.home_logo} name={match.home_team} size={18} />
          <span className={`text-sm truncate ${hasScore && match.home_score > match.away_score ? "text-white font-semibold" : "text-slate-300"}`}>
            {match.home_team}
          </span>
          {hasScore && (
            <span className={`ml-auto text-lg font-display font-bold tabular-nums ${isLive ? "text-green-400" : "text-white"}`}>
              {match.home_score}
            </span>
          )}
        </div>

        {/* Away team */}
        <div className="flex items-center gap-2">
          <TeamLogo src={match.away_logo} name={match.away_team} size={18} />
          <span className={`text-sm truncate ${hasScore && match.away_score > match.home_score ? "text-white font-semibold" : "text-slate-300"}`}>
            {match.away_team}
          </span>
          {hasScore && (
            <span className={`ml-auto text-lg font-display font-bold tabular-nums ${isLive ? "text-green-400" : "text-white"}`}>
              {match.away_score}
            </span>
          )}
        </div>
      </div>

      {/* Arrow indicator */}
      <div className="shrink-0 text-slate-600 group-hover:text-slate-400 transition-colors">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </Link>
  );
}

/**
 * Skeleton placeholder while loading.
 */
export function MatchCardSkeleton() {
  return (
    <div className="match-card flex items-center gap-4 px-4 py-3">
      <div className="skeleton w-14 h-8 rounded" />
      <div className="flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <div className="skeleton w-5 h-5 rounded-full" />
          <div className="skeleton h-4 rounded flex-1 max-w-[180px]" />
          <div className="skeleton w-6 h-5 rounded ml-auto" />
        </div>
        <div className="flex items-center gap-2">
          <div className="skeleton w-5 h-5 rounded-full" />
          <div className="skeleton h-4 rounded flex-1 max-w-[140px]" />
          <div className="skeleton w-6 h-5 rounded ml-auto" />
        </div>
      </div>
    </div>
  );
}
