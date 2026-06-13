/**
 * AdSlot — lazy-loads ad units only when they enter the viewport.
 *
 * Props:
 *   slot    — ad slot identifier (maps to GPT unit ID)
 *   sticky  — stick to viewport top on scroll (sidebar use)
 *   className — extra classes for wrapper
 *
 * UX rules enforced:
 *   - Reserved min-height prevents CLS
 *   - Loads only when visible (IntersectionObserver)
 *   - Premium users (tier !== "free") see no ads
 */
import { useEffect, useRef, useState } from "react";

// Slot configuration — maps slot key → ad unit dimensions
const SLOT_CONFIG = {
  header_banner:  { width: "100%", height: 50, unit: "header-banner" },
  in_feed:        { width: "100%", height: 90, unit: "in-feed" },
  sidebar_top:    { width: 300, height: 250, unit: "sidebar-top" },
  sidebar_sticky: { width: 160, height: 600, unit: "sidebar-sticky" },
  in_article:     { width: 300, height: 250, unit: "in-article" },
  mobile_footer:  { width: "100%", height: 50, unit: "mobile-footer" },
};

// Check user tier from localStorage (set on login)
function isAdFree() {
  try {
    const tier = localStorage.getItem("user_tier");
    return tier === "plus" || tier === "pro";
  } catch {
    return false;
  }
}

export default function AdSlot({ slot, sticky = false, className = "", index = 0 }) {
  const ref = useRef(null);
  const [loaded, setLoaded] = useState(false);
  const config = SLOT_CONFIG[slot];

  useEffect(() => {
    if (!config || isAdFree()) return;
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !loaded) {
          setLoaded(true);
          // Push to Google Publisher Tag
          if (window.googletag) {
            window.googletag.cmd.push(() => {
              window.googletag.display(`${slot}-${index}`);
            });
          }
          observer.disconnect();
        }
      },
      { rootMargin: "200px" }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [slot, index, config, loaded]);

  if (!config || isAdFree()) return null;

  const isDev = import.meta.env.DEV;

  return (
    <div
      className={`${sticky ? "sticky top-4" : ""} ${className}`}
      style={{
        width: config.width,
        minHeight: config.height,
      }}
    >
      <div
        ref={ref}
        id={`${slot}-${index}`}
        className="ad-slot"
        aria-label="Advertisement"
        style={{ minHeight: config.height, width: config.width }}
      >
        {/* In development, show a visible placeholder */}
        {isDev && (
          <div className="flex flex-col items-center justify-center w-full h-full text-slate-600 text-xs gap-1">
            <span className="font-mono opacity-50">AD</span>
            <span className="opacity-30">{slot} • {config.width}×{config.height}</span>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Mobile sticky footer ad — shown only on mobile, hides on scroll-up.
 */
export function MobileStickyAd() {
  const [visible, setVisible] = useState(true);
  const lastY = useRef(0);

  useEffect(() => {
    const handler = () => {
      const currentY = window.scrollY;
      setVisible(currentY <= lastY.current || currentY < 100);
      lastY.current = currentY;
    };
    window.addEventListener("scroll", handler, { passive: true });
    return () => window.removeEventListener("scroll", handler);
  }, []);

  if (isAdFree()) return null;

  return (
    <div
      className={`fixed bottom-0 left-0 right-0 z-30 xl:hidden transition-transform duration-300 ${
        visible ? "translate-y-0" : "translate-y-full"
      }`}
      style={{ minHeight: 50 }}
    >
      <AdSlot slot="mobile_footer" />
    </div>
  );
}
