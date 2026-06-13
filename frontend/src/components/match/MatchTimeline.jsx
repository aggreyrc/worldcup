/**
 * MatchTimeline — vertical list of match events (goals, cards, subs).
 */
const EVENT_ICONS = {
  Goal:        { icon: "⚽", color: "text-green-400" },
  "Own Goal":  { icon: "⚽", color: "text-red-400" },
  "Yellow Card":{ icon: "🟨", color: "text-amber-400" },
  "Red Card":  { icon: "🟥", color: "text-red-500" },
  subst:       { icon: "🔄", color: "text-blue-400" },
  Var:         { icon: "📺", color: "text-slate-400" },
};

function EventRow({ event }) {
  const cfg = EVENT_ICONS[event.type] || EVENT_ICONS[event.detail] || { icon: "•", color: "text-slate-400" };
  return (
    <div className="flex items-start gap-3 py-2">
      <span className="w-10 text-right text-xs font-mono text-slate-500 shrink-0 pt-0.5">
        {event.time}'
      </span>
      <span className={`text-base shrink-0 ${cfg.color}`}>{cfg.icon}</span>
      <div className="text-sm">
        <span className="text-slate-200 font-medium">{event.player}</span>
        {event.assist && (
          <span className="text-slate-500 ml-1.5 text-xs">(assist: {event.assist})</span>
        )}
        <div className="text-slate-500 text-xs mt-0.5">{event.team} · {event.detail}</div>
      </div>
    </div>
  );
}

export default function MatchTimeline({ events = [] }) {
  if (!events.length) {
    return <p className="text-slate-500 text-sm py-4">No events yet.</p>;
  }

  const firstHalf  = events.filter((e) => e.time <= 45);
  const secondHalf = events.filter((e) => e.time > 45 && e.time <= 90);
  const extra      = events.filter((e) => e.time > 90);

  return (
    <div className="divide-y divide-white/5">
      {firstHalf.length > 0 && (
        <div className="pb-3">
          <div className="text-xs text-slate-500 uppercase tracking-wider mb-2 px-1">First Half</div>
          {firstHalf.map((e, i) => <EventRow key={i} event={e} />)}
        </div>
      )}
      {secondHalf.length > 0 && (
        <div className="py-3">
          <div className="text-xs text-slate-500 uppercase tracking-wider mb-2 px-1">Second Half</div>
          {secondHalf.map((e, i) => <EventRow key={i} event={e} />)}
        </div>
      )}
      {extra.length > 0 && (
        <div className="pt-3">
          <div className="text-xs text-slate-500 uppercase tracking-wider mb-2 px-1">Extra Time</div>
          {extra.map((e, i) => <EventRow key={i} event={e} />)}
        </div>
      )}
    </div>
  );
}
