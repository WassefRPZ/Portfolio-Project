import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Events.css";

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
    <span className={`status-pill status-pill--${variant}`}>
      {children}
    </span>
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

export default function Events() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  const events = useMemo(
    () => [
      {
        id: 1,
        month: "JAN",
        day: "08",
        title: "D&D Campaign - Session 12",
        host: "Alice Martinez",
        time: "7:00 PM",
        location: "Gaming Knights Club",
        players: "6/6 players",
        status: "confirmed",
        canJoin: false,
      },
      {
        id: 2,
        month: "JAN",
        day: "10",
        title: "Catan Tournament Finals",
        host: "Ben Kim",
        time: "6:30 PM",
        location: "Board Game Café",
        players: "12/16 players",
        status: "spots",
        canJoin: true,
      },
      {
        id: 3,
        month: "JAN",
        day: "12",
        title: "Board Game Night",
        host: "Gaming Knights Club",
        time: "5:00 PM",
        location: "Community Center",
        players: "8/20 players",
        status: "spots",
        canJoin: true,
      },
    ],
    []
  );

  const filtered = events.filter((e) => {
    const hay = `${e.title} ${e.host} ${e.location}`.toLowerCase();
    return hay.includes(query.toLowerCase());
  });

  return (
    <div className="events-page">
      {/* Header row */}
      <div className="events-header">
        <h1>Events</h1>

        <button onClick={() => navigate("/create-event")} className="events-create-btn">
          <span>＋</span>
          Create Event
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
        {filtered.map((e) => (
          <div key={e.id} className="event-card">
            {/* Left content */}
            <div className="event-card__left">
              <DateBadge month={e.month} day={e.day} />

              <div className="event-card__info">
                <div className="event-card__title">{e.title}</div>
                <div className="event-card__host">
                  Hosted by <strong>{e.host}</strong>
                </div>

                <div className="event-card__meta">
                  <IconText icon="🕒">{e.time}</IconText>
                  <IconText icon="📍">{e.location}</IconText>
                  <IconText icon="👥">{e.players}</IconText>
                </div>

                <div className="event-card__status">
                  {e.status === "confirmed" ? (
                    <StatusPill variant="confirmed">Confirmed</StatusPill>
                  ) : (
                    <StatusPill variant="spots">Spots Available</StatusPill>
                  )}
                </div>
              </div>
            </div>

            {/* Right buttons */}
            <div className="event-card__actions">
              <button
                onClick={() => alert("Details page later (MVP)")}
                className="btn-brown"
              >
                View Details
              </button>

              {e.canJoin && (
                <button
                  onClick={() => alert("Join logic later (backend)")}
                  className="btn-outline"
                >
                  Join Event
                </button>
              )}
            </div>
          </div>
        ))}

        {filtered.length === 0 && (
          <div className="events-empty">No events found.</div>
        )}
      </div>
    </div>
  );
}