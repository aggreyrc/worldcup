/**
 * SWR hooks for all data fetching.
 * Each hook handles loading, error, and stale states consistently.
 */
import useSWR from "swr";
import { fetcher } from "@/lib/api";

// ── Fixtures ─────────────────────────────────────────────
export function useFixtures(sport = "football", from = null, to = null) {
  const params = new URLSearchParams({ sport });
  if (from) params.set("from", from);
  if (to) params.set("to", to);
  const { data, error, isLoading } = useSWR(
    `/api/v1/fixtures?${params}`,
    fetcher,
    { refreshInterval: 60_000 }
  );
  return {
    fixtures: data?.data || [],
    isLoading,
    isError: !!error,
  };
}

// ── Match Detail ─────────────────────────────────────────
export function useMatchDetail(matchId, sport = "football") {
  const { data, error, isLoading } = useSWR(
    matchId ? `/api/v1/match/${matchId}?sport=${sport}` : null,
    fetcher,
    { refreshInterval: 20_000, revalidateOnFocus: true }
  );
  const match = data?.data || null;
  return {
    match,
    isLive: match?.status === "live" || match?.status === "ht",
    isLoading,
    isError: !!error,
  };
}

// ── Lineups ──────────────────────────────────────────────
export function useLineups(matchId, sport = "football") {
  const { data, error, isLoading } = useSWR(
    matchId ? `/api/v1/match/${matchId}/lineups?sport=${sport}` : null,
    fetcher,
    { refreshInterval: 300_000 }
  );
  return { lineups: data?.data || {}, isLoading, isError: !!error };
}

// ── Standings ────────────────────────────────────────────
export function useStandings(competitionId, season = "2025", sport = "football") {
  const { data, error, isLoading } = useSWR(
    competitionId
      ? `/api/v1/standings/${competitionId}?season=${season}&sport=${sport}`
      : null,
    fetcher,
    { refreshInterval: 300_000 }
  );
  return { standings: data?.data || null, isLoading, isError: !!error };
}

// ── Featured Competitions ─────────────────────────────────
export function useFeaturedCompetitions() {
  const { data, error, isLoading } = useSWR(
    `/api/v1/competitions/featured`,
    fetcher,
    { refreshInterval: 3_600_000 }
  );
  return {
    competitions: data?.data || [],
    isLoading,
    isError: !!error,
  };
}

// ── Team ─────────────────────────────────────────────────
export function useTeam(teamId, sport = "football") {
  const { data, error, isLoading } = useSWR(
    teamId ? `/api/v1/team/${teamId}?sport=${sport}` : null,
    fetcher,
    { refreshInterval: 86_400_000 }
  );
  return { team: data?.data || null, isLoading, isError: !!error };
}

export function useTeamFixtures(teamId, sport = "football") {
  const { data, error, isLoading } = useSWR(
    teamId ? `/api/v1/team/${teamId}/fixtures?sport=${sport}` : null,
    fetcher,
    { refreshInterval: 300_000 }
  );
  return { fixtures: data?.data || { last: [], next: [] }, isLoading, isError: !!error };
}
