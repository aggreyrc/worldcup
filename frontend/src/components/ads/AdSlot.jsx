/**
 * AdSlot — Google AdSense ad unit component.
 *
 * Uses your publisher ID: ca-pub-7758251123781202
 * Ad slot: 1804601486
 *
 * Features:
 *  - Lazy loads via IntersectionObserver (only when visible)
 *  - Reserved min-height prevents CLS (layout shift)
 *  - Hidden for premium users (tier !== "free")
 *  - Shows placeholder in development mode
 *  - Mobile sticky footer ad hides on scroll-up
 */
import { useEffect, useRef, useState } from "react";

const PUBLISHER_ID = "ca-pub-7758251123781202";
const AD_SLOT      = "1804601486";

// Minimum heights per slot to prevent CLS
const SLOT_HEIGHTS = {
  header_banner:  90,
  in_feed:        90,
  in_article:     250,
  sidebar_top:    250,
  sidebar_sticky: 600,
  mobile_footer:  60,
};

function isAdFree() {
  try {
    const tier = localStorage.getItem("user_tier");
    return tier === "plus" || tier === "pro";
  } catch {
    return false;
  }
}

export default function AdSlot({ slot = "in_feed", index = 0, className = "", sticky = false }) {
  const ref      = useRef(null);
  const pushed   = useRef(false);
  const [visible, setVisible] = useState(false);
  const isDev    = import.meta.env.DEV;
  const minH     = SLOT_HEIGHTS[slot] || 90;

  useEffect(() => {
    if (isAdFree() || pushed.current) return;
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !pushed.current) {
          setVisible(true);
          pushed.current = true;
          // Push ad to AdSense
          try {
            (window.adsbygoogle = window.adsbygoogle || []).push({});
          } catch (e) {
            console.warn("AdSense push error:", e);
          }
          observer.disconnect();
        }
      },
      { rootMargin: "200px" }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  if (isAdFree()) return null;

  return (
    <div
      className={`${sticky ? "sticky top-4" : ""} ${className}`}
      style={{ minHeight: minH }}
      aria-label="Advertisement"
    >
      {isDev ? (
        /* Dev placeholder — shows slot name and size */
        <div
          style={{
            minHeight: minH,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(255,255,255,0.03)",
            border: "1px dashed rgba(255,255,255,0.08)",
            borderRadius: 8,
            color: "rgba(255,255,255,0.2)",
            fontSize: 11,
            fontFamily: "monospace",
            gap: 4,
          }}
        >
          <span>AD SLOT</span>
          <span style={{ opacity: 0.5 }}>{slot} · {minH}px</span>
          <span style={{ opacity: 0.3 }}>{PUBLISHER_ID}</span>
        </div>
      ) : (
        /* Production — real AdSense unit */
        <ins
          ref={ref}
          className="adsbygoogle"
          style={{ display: "block", minHeight: minH }}
          data-ad-client={PUBLISHER_ID}
          data-ad-slot={AD_SLOT}
          data-ad-format="auto"
          data-full-width-responsive="true"
        />
      )}
    </div>
  );
}

/**
 * MobileStickyAd — fixed footer ad on mobile.
 * Hides when user scrolls down (shows when scrolling back up).
 */
export function MobileStickyAd() {
  const [visible, setVisible] = useState(true);
  const lastY  = useRef(0);
  const pushed = useRef(false);
  const isDev  = import.meta.env.DEV;

  useEffect(() => {
    const handler = () => {
      const y = window.scrollY;
      setVisible(y < lastY.current || y < 100);
      lastY.current = y;
    };
    window.addEventListener("scroll", handler, { passive: true });
    return () => window.removeEventListener("scroll", handler);
  }, []);

  useEffect(() => {
    if (isAdFree() || pushed.current || isDev) return;
    if (visible && !pushed.current) {
      pushed.current = true;
      try {
        (window.adsbygoogle = window.adsbygoogle || []).push({});
      } catch (e) {
        console.warn("AdSense mobile footer push error:", e);
      }
    }
  }, [visible, isDev]);

  if (isAdFree()) return null;

  return (
    <div
      className={`fixed bottom-0 left-0 right-0 z-30 xl:hidden transition-transform duration-300 bg-pitch-mid border-t border-white/5 ${
        visible ? "translate-y-0" : "translate-y-full"
      }`}
      style={{ minHeight: 60 }}
      aria-label="Advertisement"
    >
      {isDev ? (
        <div style={{
          height: 60,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "rgba(255,255,255,0.2)",
          fontSize: 11,
          fontFamily: "monospace",
        }}>
          AD · mobile_footer · 60px
        </div>
      ) : (
        <ins
          className="adsbygoogle"
          style={{ display: "block", minHeight: 60 }}
          data-ad-client={PUBLISHER_ID}
          data-ad-slot={AD_SLOT}
          data-ad-format="auto"
          data-full-width-responsive="true"
        />
      )}
    </div>
  );
}