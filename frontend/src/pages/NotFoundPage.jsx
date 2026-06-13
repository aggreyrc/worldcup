import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <div className="text-7xl mb-4">🔍</div>
      <h1 className="font-display text-4xl font-bold text-white mb-2">404</h1>
      <p className="text-slate-400 mb-6">This page doesn't exist.</p>
      <Link
        to="/"
        className="px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg font-medium transition-colors"
      >
        Back to Live Scores
      </Link>
    </div>
  );
}
