/**
 * Team Page — profile, recent results, upcoming fixtures.
 */
import { useEffect } from "react";
import { useParams } from "react-router-dom";
import { useTeam, useTeamFixtures } from "@/hooks/useData";
import MatchCard, { MatchCardSkeleton } from "@/components/match/MatchCard";
import TeamLogo from "@/components/ui/TeamLogo";
import AdSlot from "@/components/ads/AdSlot";
import Spinner from "@/components/ui/Spinner";
import { setPageMeta } from "@/lib/seo";

export default function TeamPage() {
  const { teamId, sport = "football" } = useParams();
  const { team, isLoading: teamLoading } = useTeam(teamId, sport);
  const { fixtures, isLoading: fixturesLoading } = useTeamFixtures(teamId, sport);

  useEffect(() => {
    if (team) {
      setPageMeta(
        `${team.name} — Fixtures, Results & Stats`,
        `Latest results and upcoming fixtures for ${team.name}.`
      );
    }
  }, [team]);

  if (teamLoading) {
    return (
      <div className="flex justify-center py-20">
        <Spinner size={40} />
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      {/* Team header */}
      {team && (
        <div className="flex items-center gap-4 mb-6 bg-pitch-mid border border-white/5 rounded-2xl p-5">
          <TeamLogo src={team.logo} name={team.name} size={64} />
          <div>
            <h1 className="font-display text-3xl font-bold text-white">{team.name}</h1>
            <div className="flex items-center gap-2 text-slate-400 text-sm mt-1">
              {team.country && <span>{team.country}</span>}
              {team.founded && <><span>·</span><span>Founded {team.founded}</span></>}
            </div>
            {team.venue?.name && (
              <p className="text-slate-500 text-xs mt-1">📍 {team.venue.name}, {team.venue.city}</p>
            )}
          </div>
        </div>
      )}

      <AdSlot slot="in_article" className="mb-6" />

      {/* Recent results */}
      <section className="mb-6">
        <h2 className="font-display text-xl font-bold text-white mb-3">Recent Results</h2>
        {fixturesLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => <MatchCardSkeleton key={i} />)}
          </div>
        ) : fixtures.last?.length ? (
          <div className="space-y-1">
            {fixtures.last.map((match) => (
              <MatchCard key={match.match_id} match={match} sport={sport} />
            ))}
          </div>
        ) : (
          <p className="text-slate-500 text-sm">No recent results.</p>
        )}
      </section>

      {/* Upcoming fixtures */}
      <section>
        <h2 className="font-display text-xl font-bold text-white mb-3">Upcoming Fixtures</h2>
        {fixturesLoading ? (
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => <MatchCardSkeleton key={i} />)}
          </div>
        ) : fixtures.next?.length ? (
          <div className="space-y-1">
            {fixtures.next.map((match) => (
              <MatchCard key={match.match_id} match={match} sport={sport} />
            ))}
          </div>
        ) : (
          <p className="text-slate-500 text-sm">No upcoming fixtures.</p>
        )}
      </section>
    </div>
  );
}
