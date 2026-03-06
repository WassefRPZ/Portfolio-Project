import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getEvents, joinEvent, leaveEvent } from "../api/events";
import "../styles/Events.css";

/* ── helpers ── */

function parseDate(iso) {
  if (!iso) return { month: "—", day: "--" };
  const d = new Date(iso);
  const month = d.toLocaleString("en-US", { month: "short" }).toUpperCase();
  const day = String(d.getDate()).padStart(2, "0");
  return { month, day };
}

function formatTime(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function DateBadge({ month, day }) {
  return (
    <div className="date-badge">
      <div className="date-badge__month">{month}</div>
      <div className="date-badge__day">{day}</div>
    </div>
  );
}

function StatusPill({ variant, children }) {
  return (
    <span className={`status-pill status-pill--${variant}`}>{children}</span>
  );
}

function IconText({ icon, children }) {
  return (
    <div className="icon-text">
      <span className="icon-text__icon">{icon}</span>
      <span>{children}</span>
    </div>
  );
}

/* ── page ── */

export default function Events() {
  const { token, user } = useAuth();
  const navigate = useNavigate();

  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [actionLoading, setActionLoading] = useState(null);

  const fetchEvents = useCallback(async () => {
    try {
      const res = await getEvents(token);
      setEvents(res.data || []);
    } catch (err) {
      console.error("Failed to load events:", err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  /* Join / leave handlers */
  async function handleJoin(eventId) {
    setActionLoading(eventId);
    try {
      await joinEvent(token, eventId);
      await fetchEvents();
    } catch (err) {
      alert(err.message);
    } finally {
      setActionLoading(null);
    }
  }

  async function handleLeave(eventId) {
    setActionLoading(eventId);
    try {
      await leaveEvent(token, eventId);
      await fetchEvents();
    } catch (err) {
      alert(err.message);
    } finally {
      setActionLoading(null);
    }
  }

  /* Search filter (client-side on loaded events) */
  const filtered = events.filter((e) => {
    if (!query.trim()) return true;
    const hay = `${e.title} ${e.city} ${e.description}`.toLowerCase();
    return hay.includes(query.toLowerCase());
  });

  /* Decide button state per event */
  function getEventAction(event) {
    const userId = user ? Number(user.id) : null;

    if (event.creator_id === userId) return "owner";
    if (event.status === "full") return "full";
    if (event.status === "cancelled") return "cancelled";

    // Check if current user is a participant
    if (event.participants) {
      const isParticipant = event.participants.some(
        (p) => p.user_id === userId && p.status === "confirmed"
      );
      if (isParticipant) return "joined";
    }

    return "join";
  }

  if (loading) {
    return <div className="events-page"><p style={{ padding: 24, color: "#999" }}>Loading events...</p></div>;
  }

  return (
    <div className="events-page">
      {/* Header */}
      <div className="events-header">
        <h1>Events</h1>
        <button onClick={() => navigate("/create-event")} className="events-create-btn">
          <span>＋</span> Create Event
        </button>
      </div>

      {/* Search */}
      <div className="events-search">
        <div className="events-search-bar">
          <span className="events-search-icon">🔎</span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search events..."
          />
        </div>
      </div>

      {/* List */}
      <div className="events-list">
        {filtered.map((event) => {
          const { month, day } = parseDate(event.date_time);
          const action = getEventAction(event);
          const gameName = event.game?.name || "";
          const isLoading = actionLoading === event.id;

          return (
            <div key={event.id} className="event-card">
              <div className="event-card__left">
                <DateBadge month={month} day={day} />

                <div className="event-card__info">
                  <div className="event-card__title">{event.title}</div>
                  <div className="event-card__host">
                    {gameName && <>{gameName} · </>}
                    {event.city}
                  </div>

                  <div className="event-card__meta">
                    <IconText icon="🕒">{formatTime(event.date_time)}</IconText>
                    <IconText icon="📍">{event.location_text}</IconText>
                    <IconText icon="👥">
                      {event.current_players}/{event.max_players} players
                    </IconText>
                  </div>

                  <div className="event-card__status">
                    {event.status === "full" ? (
                      <StatusPill variant="confirmed">Full</StatusPill>
                    ) : event.status === "cancelled" ? (
                      <StatusPill variant="cancelled">Cancelled</StatusPill>
                    ) : (
                      <StatusPill variant="spots">Spots Available</StatusPill>
                    )}
                  </div>
                </div>
              </div>

              <div className="event-card__actions">
                {action === "join" && (
                  <button
                    onClick={() => handleJoin(event.id)}
                    disabled={isLoading}
                    className="btn-brown"
                  >
                    {isLoading ? "..." : "Join Event"}
                  </button>
                )}

                {action === "joined" && (
                  <button
                    onClick={() => handleLeave(event.id)}
                    disabled={isLoading}
                    className="btn-outline"
                  >
                    {isLoading ? "..." : "Leave Event"}
                  </button>
                )}

                {action === "owner" && (
                  <span className="event-card__badge">Your event</span>
                )}

                {action === "full" && (
                  <span className="event-card__badge">Event full</span>
                )}
              </div>
            </div>
          );
        })}

        {filtered.length === 0 && (
          <div className="events-empty">No events found.</div>
        )}
      </div>
    </div>
  );
}