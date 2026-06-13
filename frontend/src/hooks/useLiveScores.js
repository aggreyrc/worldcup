/**
 * useLiveScores — connects to SSE stream, falls back to polling.
 *
 * Returns: { matches, status, source }
 * status: "connecting" | "live" | "stale" | "error" | "idle"
 */
import { useState, useEffect, useRef, useCallback } from "react";
import { api, buildUrl } from "@/lib/api";

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

  const fetchSnapshot = useCallback(async () => {
    try {
      const json = await api.getLiveScores(sport);
      handleData(json);
    } catch {
      setStatus("stale");
    }
  }, [sport, handleData]);

  const startPolling = useCallback(() => {
    if (pollRef.current) return;
    fetchSnapshot();
    pollRef.current = setInterval(fetchSnapshot, POLL_INTERVAL_MS);
  }, [fetchSnapshot]);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  useEffect(() => {
    setStatus("connecting");
    setMatches([]);
    setSource(null);

    // Fetch a snapshot immediately. The snapshot endpoint falls back to the
    // provider on Redis cold starts, while the SSE stream only reads Redis.
    fetchSnapshot();

    // Try SSE first for Redis-backed live updates.
    if (typeof EventSource !== "undefined") {
      const url = buildUrl(`/api/v1/scores/live/stream?sport=${encodeURIComponent(sport)}`);
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
        // Fall back to polling the snapshot endpoint, which can fetch directly.
        startPolling();
      };

      return () => {
        es.close();
        stopPolling();
      };
    }

    // SSE not supported — use polling.
    startPolling();
    return stopPolling;
  }, [sport, handleData, fetchSnapshot, startPolling, stopPolling]);

  return { matches, status, source };
}
