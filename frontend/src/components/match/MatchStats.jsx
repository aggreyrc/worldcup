/**
 * MatchStats — possession bar, shots, corners, etc.
 */
function StatRow({ label, home, away }) {
  const homeVal = parseInt(home) || 0;
  const awayVal = parseInt(away) || 0;
  const total = homeVal + awayVal || 1;
  const homePct = Math.round((homeVal / total) * 100);

  return (
    <div className="py-2.5">
      <div className="flex justify-between text-sm mb-1.5">
        <span className="font-semibold text-slate-200">{home ?? "—"}</span>
        <span className="text-slate-500 text-xs uppercase tracking-wider">{label}</span>
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
  "Total Shots": "Shots",
  "Shots on Goal": "Shots on Target",
  "Corner Kicks": "Corners",
  "Fouls": "Fouls",
  "Yellow Cards": "Yellow Cards",
  "Red Cards": "Red Cards",
  "Offsides": "Offsides",
  "Goalkeeper Saves": "Saves",
  "Total passes": "Passes",
  "Passes %": "Pass Accuracy",
};

export default function MatchStats({ statistics = {}, homeTeam, awayTeam }) {
  const homeStats = statistics[homeTeam] || {};
  const awayStats = statistics[awayTeam] || {};

  const keys = Object.keys(STAT_LABELS).filter(
    (k) => homeStats[k] != null || awayStats[k] != null
  );

  if (!keys.length) {
    return <p className="text-slate-500 text-sm py-4">Stats not available yet.</p>;
  }

  return (
    <div className="divide-y divide-white/5">
      {keys.map((key) => (
        <StatRow
          key={key}
          label={STAT_LABELS[key]}
          home={homeStats[key]}
          away={awayStats[key]}
        />
      ))}
    </div>
  );
}
