export default function Spinner({ size = 24, className = "" }) {
  return (
    <svg
      className={`animate-spin text-brand-500 ${className}`}
      width={size} height={size}
      viewBox="0 0 24 24" fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeOpacity="0.2" />
      <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}
