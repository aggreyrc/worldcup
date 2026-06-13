/**
 * MatchStats — possession bar, shots, corners, etc.
 */
function numericValue(value) {
  if (value == null) return 0;
  const match = String(value).match(/-?\d+(\.\d+)?/);
  return match ? Number(match[0]) : 0;
}

function StatRow({ label, home, away }) {
  const homeVal = numericValue(home);
  const awayVal = numericValue(away);
  const total = homeVal + awayVal || 1;
  const homePct = Math.round((homeVal / total) * 100);

  return (
    <div className="py-2.5">
      <div className="flex justify-between text-sm mb-1.5">
        <span className="font-semibold text-slate-200">{home ?? "—"}</span>
        <span className="text-slate-500 text-xs uppercase tracking-wider text-center px-2">{label}</span>
        <span className="font-semibold text-slate-200">{away ?? "—"}</span>
      </div>
      <div className="flex h-1.5 rounded-full overflow-hidden bg-white/5">
        <div className="bg-brand-500 rounded-l-full transition-all duration-700" style={{ width: `${homePct}%` }} />
        <div className="bg-blue-500 rounded-r-full transition-all duration-700" style={{ width: `${100 - homePct}%` }} />
      </div>
    </div>
  );
}

const STAT_LABELS = {
  "Ball Possession": "Possession",
  possessionPct: "Possession",
  Possession: "Possession",
  "Total Shots": "Shots",
  totalShots: "Shots",
  Shots: "Shots",
  "Shots on Goal": "Shots on Target",
  shotsOnTarget: "Shots on Target",
  "Shots on Target": "Shots on Target",
  "Corner Kicks": "Corners",
  cornerKicks: "Corners",
  Corners: "Corners",
  Fouls: "Fouls",
  foulsCommitted: "Fouls",
  "Yellow Cards": "Yellow Cards",
  yellowCards: "Yellow Cards",
  "Red Cards": "Red Cards",
  redCards: "Red Cards",
  Offsides: "Offsides",
  offsides: "Offsides",
  "Goalkeeper Saves": "Saves",
  saves: "Saves",
  "Total passes": "Passes",
  totalPasses: "Passes",
  "Passes %": "Pass Accuracy",
  passAccuracy: "Pass Accuracy",
};

const PREFERRED_ORDER = [
  "Possession",
  "Shots",
  "Shots on Target",
  "Corners",
  "Fouls",
  "Yellow Cards",
  "Red Cards",
  "Offsides",
  "Saves",
  "Passes",
  "Pass Accuracy",
];

function displayLabel(key) {
  return STAT_LABELS[key] || key.replace(/([a-z])([A-Z])/g, "$1 $2");
}

export default function MatchStats({ statistics = {}, homeTeam, awayTeam }) {
  const homeStats = statistics[homeTeam] || {};
  const awayStats = statistics[awayTeam] || {};
  const statKeys = Array.from(new Set([...Object.keys(homeStats), ...Object.keys(awayStats)]));

  const rows = statKeys
    .map((key) => ({ key, label: displayLabel(key), home: homeStats[key], away: awayStats[key] }))
    .sort((a, b) => {
      const aIndex = PREFERRED_ORDER.indexOf(a.label);
      const bIndex = PREFERRED_ORDER.indexOf(b.label);
      if (aIndex === -1 && bIndex === -1) return a.label.localeCompare(b.label);
      if (aIndex === -1) return 1;
      if (bIndex === -1) return -1;
      return aIndex - bIndex;
    });

  if (!rows.length) {
    return <p className="text-slate-500 text-sm py-4">Stats not available yet.</p>;
  }

  return (
    <div className="divide-y divide-white/5">
      {rows.map((row) => (
        <StatRow key={row.key} label={row.label} home={row.home} away={row.away} />
      ))}
    </div>
  );
}
