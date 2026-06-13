/**
 * StatusBadge — shows match status (LIVE, HT, FT, etc.)
 */
export default function StatusBadge({ status, minute }) {
  const config = {
    live:      { label: minute ? `${minute}'` : "LIVE", cls: "status-live" },
    ht:        { label: "HT",         cls: "status-ht" },
    ft:        { label: "FT",         cls: "status-ft" },
    aet:       { label: "AET",        cls: "status-ft" },
    pen:       { label: "PEN",        cls: "status-ft" },
    ns:        { label: "Soon",       cls: "status-ns" },
    postponed: { label: "PST",        cls: "status-ft" },
    cancelled: { label: "CANC",       cls: "status-ft" },
  };

  const { label, cls } = config[status] || { label: status?.toUpperCase(), cls: "status-ns" };

  return (
    <span className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${cls}`}>
      {status === "live" && <span className="live-dot w-1.5 h-1.5" />}
      {label}
    </span>
  );
}
