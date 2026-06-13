/**
 * API client — all backend calls go through here.
 * Base URL is set via VITE_API_BASE_URL env variable.
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function apiFetch(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(body.error || `HTTP ${res.status}`, res.status);
  }
  return res.json();
}

// ── Scores ───────────────────────────────────────────────
export const api = {
  getLiveScores: (sport = "football") =>
    apiFetch(`/api/v1/scores/live?sport=${sport}`),

  getLiveCount: (sport = "football") =>
    apiFetch(`/api/v1/scores/live/count?sport=${sport}`),

  getFixtures: (sport = "football", from, to) => {
    const params = new URLSearchParams({ sport });
    if (from) params.set("from", from);
    if (to) params.set("to", to);
    return apiFetch(`/api/v1/fixtures?${params}`);
  },

  getMatchDetail: (matchId, sport = "football") =>
    apiFetch(`/api/v1/match/${matchId}?sport=${sport}`),

  getLineups: (matchId, sport = "football") =>
    apiFetch(`/api/v1/match/${matchId}/lineups?sport=${sport}`),

  getStandings: (competitionId, season = "2025", sport = "football") =>
    apiFetch(`/api/v1/standings/${competitionId}?season=${season}&sport=${sport}`),

  getFeaturedCompetitions: () =>
    apiFetch("/api/v1/competitions/featured"),

  getTeam: (teamId, sport = "football") =>
    apiFetch(`/api/v1/team/${teamId}?sport=${sport}`),

  getTeamFixtures: (teamId, sport = "football") =>
    apiFetch(`/api/v1/team/${teamId}/fixtures?sport=${sport}`),

  search: (q) =>
    apiFetch(`/api/v1/search?q=${encodeURIComponent(q)}`),
};

// SWR fetcher (used in useSWR hooks)
export const fetcher = (url) => apiFetch(url);

export { ApiError };
