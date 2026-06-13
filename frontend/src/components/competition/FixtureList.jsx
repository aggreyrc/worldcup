/**
 * FixtureList — grouped fixture list with date headers and in-feed ads.
 */
import MatchCard, { MatchCardSkeleton } from "@/components/match/MatchCard";
import AdSlot from "@/components/ads/AdSlot";
import { groupByDate } from "@/lib/time";

export default function FixtureList({ fixtures = [], isLoading = false, sport = "football" }) {
  if (isLoading) {
    return (
      <div className="space-y-2">
        {Array.from({ length: 6 }).map((_, i) => <MatchCardSkeleton key={i} />)}
      </div>
    );
  }

  if (!fixtures.length) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-400">No fixtures found.</p>
      </div>
    );
  }

  const grouped = groupByDate(fixtures);
  const dates = Object.keys(grouped);

  return (
    <div className="space-y-6">
      {dates.map((dateLabel, di) => (
        <div key={dateLabel}>
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-2 mb-2">
            {dateLabel}
          </h3>
          <div className="space-y-1">
            {grouped[dateLabel].map((match) => (
              <MatchCard key={match.match_id} match={match} sport={sport} />
            ))}
          </div>
          {(di + 1) % 3 === 0 && (
            <div className="mt-4">
              <AdSlot slot="in_feed" index={Math.floor(di / 3)} />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
