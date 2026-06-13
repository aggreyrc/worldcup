/**
 * LineupDisplay — shows starting XIs side by side with formation.
 */
function PlayerList({ players = [], title }) {
  return (
    <div>
      <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{title}</h4>
      <div className="space-y-1.5">
        {players.map((p, i) => (
          <div key={i} className="flex items-center gap-2 text-sm">
            <span className="w-6 text-right text-slate-500 font-mono text-xs shrink-0">{p.number}</span>
            <span className="text-slate-300">{p.name}</span>
            {p.pos && (
              <span className="ml-auto text-xs text-slate-600 bg-white/5 px-1.5 py-0.5 rounded">{p.pos}</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function LineupDisplay({ lineups = {} }) {
  const teams = Object.keys(lineups);
  if (teams.length < 2) {
    return <p className="text-slate-500 text-sm py-4">Lineups not yet available.</p>;
  }

  const [home, away] = teams;
  const homeData = lineups[home];
  const awayData = lineups[away];

  return (
    <div>
      <div className="flex justify-between text-xs text-slate-400 mb-4">
        <span>{home} <strong className="text-white">{homeData?.formation}</strong></span>
        <span><strong className="text-white">{awayData?.formation}</strong> {away}</span>
      </div>
      <div className="grid grid-cols-2 gap-6">
        <div className="space-y-6">
          <PlayerList players={homeData?.start_xi} title="Starting XI" />
          {homeData?.substitutes?.length > 0 && (
            <PlayerList players={homeData.substitutes} title="Substitutes" />
          )}
          {homeData?.coach && (
            <p className="text-xs text-slate-500">Coach: <span className="text-slate-300">{homeData.coach}</span></p>
          )}
        </div>
        <div className="space-y-6">
          <PlayerList players={awayData?.start_xi} title="Starting XI" />
          {awayData?.substitutes?.length > 0 && (
            <PlayerList players={awayData.substitutes} title="Substitutes" />
          )}
          {awayData?.coach && (
            <p className="text-xs text-slate-500">Coach: <span className="text-slate-300">{awayData.coach}</span></p>
          )}
        </div>
      </div>
    </div>
  );
}
