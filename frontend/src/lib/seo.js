/**
 * SEO utilities — structured data (schema.org) and meta tag helpers.
 */

/**
 * Inject schema.org SportsEvent JSON-LD into <head>.
 * Call this in useEffect on match detail pages.
 */
export function injectMatchStructuredData(match) {
  if (!match) return;
  const existing = document.getElementById("match-structured-data");
  if (existing) existing.remove();

  const data = {
    "@context": "https://schema.org",
    "@type": "SportsEvent",
    name: `${match.home_team} vs ${match.away_team}`,
    startDate: match.kickoff_utc,
    sport: "Football",
    location: match.venue
      ? { "@type": "Place", name: match.venue }
      : undefined,
    competitor: [
      { "@type": "SportsTeam", name: match.home_team },
      { "@type": "SportsTeam", name: match.away_team },
    ],
    organizer: {
      "@type": "Organization",
      name: match.competition,
    },
  };

  const script = document.createElement("script");
  script.id = "match-structured-data";
  script.type = "application/ld+json";
  script.textContent = JSON.stringify(data);
  document.head.appendChild(script);
}

/**
 * Update document title and meta description.
 */
export function setPageMeta(title, description) {
  document.title = title ? `${title} | LiveScore` : "LiveScore";
  const desc = document.querySelector('meta[name="description"]');
  if (desc && description) desc.setAttribute("content", description);
}

/**
 * Match detail page title builder.
 */
export function matchPageTitle(match) {
  if (!match) return "Match";
  const score =
    match.home_score != null
      ? ` ${match.home_score}-${match.away_score}`
      : "";
  return `${match.home_team}${score} vs ${match.away_team} — ${match.competition}`;
}
