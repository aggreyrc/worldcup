/**
 * useLiveScores — connects to SSE stream, falls back to polling.
 *
 * Returns: { matches, status, source }
 * status: "connecting" | "live" | "stale" | "error" | "idle"
 */
import { useState, useEffect, useRef, useCallback } from "react";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";
const POLL_INTERVAL_MS = 20_000;

export function useLiveScores(sport = "football") {
  const [matches, setMatches] = useState([]);
  const [status, setStatus] = useState("connecting");
  const [source, setSource] = useState(null);
  const esRef = useRef(null);
  const pollRef = useRef(null);

  const handleData = useCallback((payload) => {
    setMatches(payload.data || []);
    setSource(payload.source);
    setStatus(payload.source === "error" ? "stale" : "live");
  }, []);

  const startPolling = useCallback(() => {
    if (pollRef.current) return;
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${BASE_URL}/api/v1/scores/live?sport=${sport}`);
        const json = await res.json();
        handleData(json);
      } catch {
        setStatus("stale");
      }
    }, POLL_INTERVAL_MS);
  }, [sport, handleData]);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  useEffect(() => {
    setStatus("connecting");

    // Try SSE first
    if (typeof EventSource !== "undefined") {
      const url = `${BASE_URL}/api/v1/scores/live/stream?sport=${sport}`;
      const es = new EventSource(url);
      esRef.current = es;

      es.onmessage = (e) => {
        try {
          handleData(JSON.parse(e.data));
        } catch {
          setStatus("stale");
        }
      };

      es.onerror = () => {
        setStatus("stale");
        es.close();
        esRef.current = null;
        // Fall back to polling
        startPolling();
      };

      return () => {
        es.close();
        stopPolling();
      };
    }

    // SSE not supported — use polling
    startPolling();
    return stopPolling;
  }, [sport, handleData, startPolling, stopPolling]);

  return { matches, status, source };
}
