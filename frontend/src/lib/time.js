import { format, formatDistanceToNow, isToday, isTomorrow, parseISO } from "date-fns";

/**
 * Format a UTC kickoff time to the user's local timezone.
 * @param {string} isoString - ISO 8601 UTC string
 * @returns {string} e.g. "20:45" or "Sat 15:00"
 */
export function formatKickoff(isoString) {
  if (!isoString) return "--:--";
  try {
    const date = parseISO(isoString);
    if (isToday(date)) return format(date, "HH:mm");
    if (isTomorrow(date)) return `Tomorrow ${format(date, "HH:mm")}`;
    return format(date, "EEE HH:mm");
  } catch {
    return "--:--";
  }
}

/**
 * Full kickoff display: "Sat 15 Jun, 20:45"
 */
export function formatKickoffFull(isoString) {
  if (!isoString) return "TBC";
  try {
    return format(parseISO(isoString), "EEE d MMM, HH:mm");
  } catch {
    return "TBC";
  }
}

/**
 * Returns the date label for grouping fixtures:
 * "Today", "Tomorrow", or "Mon 16 Jun"
 */
export function getDateLabel(isoString) {
  if (!isoString) return "Unknown";
  try {
    const date = parseISO(isoString);
    if (isToday(date)) return "Today";
    if (isTomorrow(date)) return "Tomorrow";
    return format(date, "EEE d MMM");
  } catch {
    return "Unknown";
  }
}

/**
 * Human-readable relative time: "2 hours ago"
 */
export function timeAgo(isoString) {
  if (!isoString) return "";
  try {
    return formatDistanceToNow(parseISO(isoString), { addSuffix: true });
  } catch {
    return "";
  }
}

/**
 * Group an array of fixtures by date label.
 */
export function groupByDate(fixtures) {
  return fixtures.reduce((groups, fixture) => {
    const label = getDateLabel(fixture.kickoff_utc);
    if (!groups[label]) groups[label] = [];
    groups[label].push(fixture);
    return groups;
  }, {});
}

/**
 * UTC kickoff display for detail pages.
 */
export function formatKickoffUtc(isoString) {
  if (!isoString) return "TBC";
  try {
    return new Intl.DateTimeFormat("en-GB", {
      weekday: "short",
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
      hour12: false,
      timeZone: "UTC",
      timeZoneName: "short",
    }).format(parseISO(isoString));
  } catch {
    return "TBC";
  }
}
