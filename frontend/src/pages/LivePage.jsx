/**
 * Live Scores Page — full live ticker with competition filter.
 */
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useLiveScores } from "@/hooks/useLiveScores";
import LiveScoreTicker from "@/components/match/LiveScoreTicker";
import { MobileStickyAd } from "@/components/ads/AdSlot";
import { setPageMeta } from "@/lib/seo";

export default function LivePage() {
  const { sport = "football" } = useParams();
  const { matches } = useLiveScores(sport);

  useEffect(() => {
    setPageMeta(
      `Live ${sport.charAt(0).toUpperCase() + sport.slice(1)} Scores`,
      `Real-time live ${sport} scores for all major competitions. Updated every 15 seconds.`
    );
  }, [sport]);

  return (
    <div className="animate-fade-in">
      <div className="flex items-center gap-3 mb-6">
        <h1 className="font-display text-3xl font-bold text-white">
          LIVE SCORES
        </h1>
        {matches.length > 0 && (
          <span className="flex items-center gap-1.5 bg-green-500/15 text-green-400 border border-green-500/20 text-sm px-3 py-1 rounded-full font-medium">
            <span className="live-dot" />
            {matches.length} matches
          </span>
        )}
      </div>

      <LiveScoreTicker sport={sport} />
      <MobileStickyAd />
    </div>
  );
}
