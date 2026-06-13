/**
 * TeamLogo — displays team crest with fallback initials.
 */
export default function TeamLogo({ src, name = "", size = 24, className = "" }) {
  const initials = name
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  if (src) {
    return (
      <img
        src={src}
        alt={name}
        width={size}
        height={size}
        className={`object-contain shrink-0 ${className}`}
        onError={(e) => { e.target.style.display = "none"; }}
        loading="lazy"
      />
    );
  }

  return (
    <div
      className={`shrink-0 rounded-full bg-pitch-light flex items-center justify-center text-slate-400 font-bold ${className}`}
      style={{ width: size, height: size, fontSize: size * 0.38 }}
      aria-label={name}
    >
      {initials}
    </div>
  );
}
