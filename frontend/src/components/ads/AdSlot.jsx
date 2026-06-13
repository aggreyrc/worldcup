/**
 * AdSlot — lazy-loads AdSense units only when they enter the viewport.
 *
 * Props:
 *   slot      — ad slot identifier (maps to an AdSense slot ID)
 *   sticky    — stick to viewport top on scroll (sidebar use)
 *   className — extra classes for wrapper
 *
 * UX rules enforced:
 *   - Reserved min-height prevents CLS
 *   - Loads only when visible (IntersectionObserver)
 *   - Premium users (tier !== "free") see no ads
 */
import { useEffect, useMemo, useRef, useState } from "react";

const ADSENSE_SRC = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js";

// Slot configuration — maps slot key → ad unit dimensions and AdSense slot env vars.
const SLOT_CONFIG = {
  header_banner: {
    width: "100%",
    height: 50,
    format: "auto",
    fullWidthResponsive: true,
    slotEnv: "VITE_ADSENSE_HEADER_BANNER_SLOT",
  },
  in_feed: {
    width: "100%",
    height: 90,
    format: "fluid",
    layoutKey: "-fb+5w+4e-db+86",
    slotEnv: "VITE_ADSENSE_IN_FEED_SLOT",
  },
  sidebar_top: {
    width: 300,
    height: 250,
    format: "auto",
    fullWidthResponsive: false,
    slotEnv: "VITE_ADSENSE_SIDEBAR_TOP_SLOT",
  },
  sidebar_sticky: {
    width: 160,
    height: 600,
    format: "auto",
    fullWidthResponsive: false,
    slotEnv: "VITE_ADSENSE_SIDEBAR_STICKY_SLOT",
  },
  in_article: {
    width: 300,
    height: 250,
    format: "fluid",
    layout: "in-article",
    slotEnv: "VITE_ADSENSE_IN_ARTICLE_SLOT",
  },
  mobile_footer: {
    width: "100%",
    height: 50,
    format: "auto",
    fullWidthResponsive: true,
    slotEnv: "VITE_ADSENSE_MOBILE_FOOTER_SLOT",
  },
};

function getEnv(name) {
  return import.meta.env[name];
}

function getClientId() {
  return getEnv("VITE_ADSENSE_CLIENT");
}

function getSlotId(config) {
  return getEnv(config.slotEnv) || getEnv("VITE_ADSENSE_DEFAULT_SLOT");
}

function ensureAdSenseScript(clientId) {
  if (!clientId || typeof document === "undefined") return;

  const scriptId = "adsense-script";
  if (document.getElementById(scriptId)) return;

  const script = document.createElement("script");
  script.id = scriptId;
  script.async = true;
  script.crossOrigin = "anonymous";
  script.src = `${ADSENSE_SRC}?client=${encodeURIComponent(clientId)}`;
  document.head.appendChild(script);
}

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
  const clientId = getClientId();
  const adSlotId = config ? getSlotId(config) : null;
  const isDev = import.meta.env.DEV;
  const canRequestAd = Boolean(config && clientId && adSlotId && !isAdFree());

  const adStyle = useMemo(
    () => ({
      display: "block",
      minHeight: config?.height,
      width: config?.width,
    }),
    [config]
  );

  useEffect(() => {
    if (!canRequestAd) return;
    ensureAdSenseScript(clientId);
  }, [canRequestAd, clientId]);

  useEffect(() => {
    if (!canRequestAd) return;
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !loaded) {
          setLoaded(true);
          window.adsbygoogle = window.adsbygoogle || [];
          window.adsbygoogle.push({});
          observer.disconnect();
        }
      },
      { rootMargin: "200px" }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [canRequestAd, loaded]);

  if (!config || isAdFree()) return null;

  return (
    <div
      className={`${sticky ? "sticky top-4" : ""} ${className}`}
      style={{
        width: config.width,
        minHeight: config.height,
      }}
    >
      {canRequestAd ? (
        <ins
          ref={ref}
          id={`${slot}-${index}`}
          className="adsbygoogle ad-slot"
          aria-label="Advertisement"
          style={adStyle}
          data-ad-client={clientId}
          data-ad-slot={adSlotId}
          data-ad-format={config.format}
          data-ad-layout={config.layout}
          data-ad-layout-key={config.layoutKey}
          data-full-width-responsive={String(config.fullWidthResponsive ?? true)}
        />
      ) : (
        <div
          ref={ref}
          id={`${slot}-${index}`}
          className="ad-slot"
          aria-label="Advertisement"
          style={{ minHeight: config.height, width: config.width }}
        >
          {isDev && (
            <div className="flex flex-col items-center justify-center w-full h-full text-slate-600 text-xs gap-1">
              <span className="font-mono opacity-50">AD</span>
              <span className="opacity-30">
                Configure VITE_ADSENSE_CLIENT and {config.slotEnv}
              </span>
            </div>
          )}
        </div>
      )}
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
