import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getEventDetails, joinEvent, leaveEvent, deleteEvent } from "../api/events";
import { getFriends, sendFriendRequest } from "../api/friends";
import { FiCalendar, FiClock, FiMapPin, FiUsers, FiUser } from "react-icons/fi";
import { GiPerspectiveDiceSixFacesRandom } from "react-icons/gi";
import "../styles/EventDetail.css";

function getInitials(name) {
  if (!name) return "?";
  return name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function formatTime(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function EventDetail() {
  const { id } = useParams();
  const { token, user } = useAuth();
  const navigate = useNavigate();

  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState(false);

  const [friendIds, setFriendIds] = useState(new Set());
  const [pendingIds, setPendingIds] = useState(new Set());

  const fetchData = useCallback(async () => {
    try {
      const [eventRes, friendsRes] = await Promise.all([
        getEventDetails(token, id),
        getFriends(token),
      ]);
      setEvent(eventRes.data);

      const fIds = new Set();
      (friendsRes.data || []).forEach((f) => {
        fIds.add(f.id);
      });
      setFriendIds(fIds);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [token, id]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);
  async function handleJoin() {
    setActionLoading(true);
    try {
      await joinEvent(token, id);
      await fetchData();
    } catch (err) {
      alert(err.message);
    } finally {
      setActionLoading(false);
    }
  }

  async function handleLeave() {
    setActionLoading(true);
    try {
      await leaveEvent(token, id);
      await fetchData();
    } catch (err) {
      alert(err.message);
    } finally {
      setActionLoading(false);
    }
  }

  async function handleDelete() {
    if (!window.confirm("Are you sure you want to delete this event?")) return;
    setActionLoading(true);
    try {
      await deleteEvent(token, id);
      navigate("/events");
    } catch (err) {
      alert(err.message);
    } finally {
      setActionLoading(false);
    }
  }

  async function handleAddFriend(userId) {
    try {
      setPendingIds((prev) => new Set(prev).add(userId));
      await sendFriendRequest(token, userId);
    } catch (err) {
      alert(err.message);
      setPendingIds((prev) => {
        const s = new Set(prev);
        s.delete(userId);
        return s;
      });
    }
  }
  if (loading) {
    return (
      <div className="event-detail">
        <p className="event-detail__loading">Loading event...</p>
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="event-detail">
        <p className="event-detail__error">{error || "Event not found"}</p>
        <button className="btn-brown" onClick={() => navigate("/events")}>
          Back to Events
        </button>
      </div>
    );
  }

  const userId = user ? Number(user.id) : null;
  const isOwner = event.creator_id === userId;
  const participantIds = (event.participants || []).map((p) => p.user_id);
  const isParticipant = participantIds.includes(userId);
  const gameName = event.game?.name || "";

  return (
    <div className="event-detail">
      <button className="event-detail__back" onClick={() => navigate("/events")}>
        ← Back to Events
      </button>

      {event.cover_url && (
        <div className="event-detail__cover">
          <img src={event.cover_url} alt={event.title} />
        </div>
      )}

      <div className="event-detail__card">
        <div className="event-detail__header">
          <h1>{event.title}</h1>
          <span className={`status-pill status-pill--${event.status === "full" ? "confirmed" : event.status === "cancelled" ? "cancelled" : "spots"}`}>
            {event.status === "full" ? "Full" : event.status === "cancelled" ? "Cancelled" : "Open"}
          </span>
        </div>

        {event.description && (
          <p className="event-detail__desc">{event.description}</p>
        )}

        <div className="event-detail__meta-grid">
          <div className="meta-item">
            <span className="meta-item__icon"><FiCalendar size={18} /></span>
            <div>
              <div className="meta-item__label">Date</div>
              <div className="meta-item__value">{formatDate(event.date_time)}</div>
            </div>
          </div>

          <div className="meta-item">
            <span className="meta-item__icon"><FiClock size={18} /></span>
            <div>
              <div className="meta-item__label">Time</div>
              <div className="meta-item__value">{formatTime(event.date_time)}</div>
            </div>
          </div>

          <div className="meta-item">
            <span className="meta-item__icon"><FiMapPin size={18} /></span>
            <div>
              <div className="meta-item__label">Location</div>
              <div className="meta-item__value">{event.location_text}</div>
            </div>
          </div>

          <div className="meta-item">
            <span className="meta-item__icon"><GiPerspectiveDiceSixFacesRandom size={18} /></span>
            <div>
              <div className="meta-item__label">Game</div>
              <div className="meta-item__value">{gameName || "—"}</div>
            </div>
          </div>

          <div className="meta-item">
            <span className="meta-item__icon"><FiUsers size={18} /></span>
            <div>
              <div className="meta-item__label">Players</div>
              <div className="meta-item__value">
                {event.current_players}/{event.max_players}
              </div>
            </div>
          </div>

          {event.creator && (
            <div className="meta-item">
              <span className="meta-item__icon"><FiUser size={18} /></span>
              <div>
                <div className="meta-item__label">Host</div>
                <div className="meta-item__value">{event.creator.username || "—"}</div>
              </div>
            </div>
          )}
        </div>

        <div className="event-detail__actions">
          {isOwner ? (
            <>
              <span className="event-detail__badge">Your event</span>
              <button
                className="btn-danger-sm"
                onClick={handleDelete}
                disabled={actionLoading}
              >
                {actionLoading ? "..." : "Delete Event"}
              </button>
            </>
          ) : isParticipant ? (
            <button
              className="btn-outline"
              onClick={handleLeave}
              disabled={actionLoading}
            >
              {actionLoading ? "..." : "Leave Event"}
            </button>
          ) : event.status === "open" ? (
            <button
              className="btn-brown"
              onClick={handleJoin}
              disabled={actionLoading}
            >
              {actionLoading ? "..." : "Join Event"}
            </button>
          ) : (
            <span className="event-detail__badge">
              {event.status === "full" ? "Event full" : "Event closed"}
            </span>
          )}
        </div>
      </div>

      <div className="event-detail__participants">
        <h2>Participants ({event.participants?.length || 0})</h2>

        {(!event.participants || event.participants.length === 0) ? (
          <p className="event-detail__empty">No participants yet.</p>
        ) : (
          <div className="participants-list">
            {event.participants.map((p) => {
              const isMe = p.user_id === userId;
              const isFriend = friendIds.has(p.user_id);
              const isPending = pendingIds.has(p.user_id);

              return (
                <div key={p.id} className="participant-card">
                  <div className="participant-card__left">
                    {p.profile_image_url ? (
                      <img
                        src={p.profile_image_url}
                        alt={p.username}
                        className="participant-card__avatar"
                      />
                    ) : (
                      <div className="participant-card__avatar-placeholder">
                        {getInitials(p.username)}
                      </div>
                    )}
                    <div>
                      <div className="participant-card__name">
                        {p.username || "User #" + p.user_id}
                        {isMe && <span className="participant-card__you"> (You)</span>}
                      </div>
                      {p.city && (
                        <div className="participant-card__city">{p.city}</div>
                      )}
                    </div>
                  </div>

                  {!isMe && (
                    <div className="participant-card__action">
                      {isFriend ? (
                        <span className="participant-card__badge">Friends ✓</span>
                      ) : isPending ? (
                        <span className="participant-card__badge">Request sent</span>
                      ) : (
                        <button
                          className="btn-brown-sm"
                          onClick={() => handleAddFriend(p.user_id)}
                        >
                          Add Friend
                        </button>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
