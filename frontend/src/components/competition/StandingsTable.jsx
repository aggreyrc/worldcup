/**
 * StandingsTable — renders a league table or World Cup group table.
 */
import { Link } from "react-router-dom";
import TeamLogo from "@/components/ui/TeamLogo";


function normalizeStandings(standings) {
  if (!standings) return [];
  if (Array.isArray(standings.groups)) return standings.groups;
  if (Array.isArray(standings)) return [standings];
  if (Array.isArray(standings.table)) return [standings.table];
  if (Array.isArray(standings.standings)) return [standings.standings];
  return [];
}

function normalizeRow(row, index) {
  return {
    ...row,
    rank: row.rank ?? row.position ?? index + 1,
    goal_difference: row.goal_difference ?? row.goals_diff ?? row.goalDiff ?? 0,
  };
}

function FormPip({ result }) {
  const cls = result === "W" ? "form-w" : result === "D" ? "form-d" : "form-l";
  return (
    <span className={`inline-flex items-center justify-center w-5 h-5 rounded text-xs font-bold ${cls}`}>
      {result}
    </span>
  );
}

export default function StandingsTable({ standings, sport = "football" }) {
  const groups = normalizeStandings(standings).filter((group) => group.length);

  if (!groups.length) {
    return <p className="text-slate-500 text-sm py-4">No standings available.</p>;
  }

  const isGroupStage = groups.length > 1;

  return (
    <div className="space-y-6">
      {groups.map((group, gi) => (
        <div key={gi}>
          {isGroupStage && (
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2 px-1">
              Group {String.fromCharCode(65 + gi)}
            </h3>
          )}
          <div className="overflow-x-auto">
            <table className="w-full text-sm min-w-[480px]">
              <thead>
                <tr className="text-xs text-slate-500 uppercase tracking-wider border-b border-white/5">
                  <th className="py-2 px-2 text-left w-7">#</th>
                  <th className="py-2 px-2 text-left">Team</th>
                  <th className="py-2 px-2 text-center">P</th>
                  <th className="py-2 px-2 text-center">W</th>
                  <th className="py-2 px-2 text-center">D</th>
                  <th className="py-2 px-2 text-center">L</th>
                  <th className="py-2 px-2 text-center">GD</th>
                  <th className="py-2 px-2 text-center font-bold text-slate-300">Pts</th>
                  <th className="py-2 px-2 text-center hidden md:table-cell">Form</th>
                </tr>
              </thead>
              <tbody>
                {group.map((rawRow, i) => {
                  const row = normalizeRow(rawRow, i);
                  const isQualify = row.description?.toLowerCase().includes("champion") ||
                                    row.description?.toLowerCase().includes("qualif");
                  const isRelegate = row.description?.toLowerCase().includes("relegat");
                  return (
                    <tr
                      key={row.team_id}
                      className="border-b border-white/5 hover:bg-white/5 transition-colors"
                    >
                      <td className="py-2.5 px-2">
                        <span className="text-slate-500 text-xs">{row.rank}</span>
                        {isQualify && (
                          <div className="w-0.5 h-full bg-green-500 absolute left-0 top-0" />
                        )}
                      </td>
                      <td className="py-2.5 px-2">
                        <Link
                          to={`/${sport}/team/${row.team_id}`}
                          className="flex items-center gap-2 hover:text-brand-400 transition-colors"
                        >
                          <TeamLogo src={row.team_logo} name={row.team_name} size={20} />
                          <span className="text-slate-200 font-medium">{row.team_name}</span>
                        </Link>
                      </td>
                      <td className="py-2.5 px-2 text-center text-slate-400">{row.played}</td>
                      <td className="py-2.5 px-2 text-center text-slate-400">{row.won}</td>
                      <td className="py-2.5 px-2 text-center text-slate-400">{row.drawn}</td>
                      <td className="py-2.5 px-2 text-center text-slate-400">{row.lost}</td>
                      <td className="py-2.5 px-2 text-center text-slate-400">
                        {row.goal_difference > 0 ? `+${row.goal_difference}` : row.goal_difference}
                      </td>
                      <td className="py-2.5 px-2 text-center font-bold text-white">{row.points}</td>
                      <td className="py-2.5 px-2 hidden md:table-cell">
                        <div className="flex gap-0.5 justify-center">
                          {(row.form || "").split("").map((r, fi) => (
                            <FormPip key={fi} result={r} />
                          ))}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}
