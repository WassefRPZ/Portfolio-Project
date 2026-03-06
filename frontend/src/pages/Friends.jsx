import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import {
  getFriends,
  getPendingRequests,
  getSentRequests,
  acceptFriendRequest,
  declineFriendRequest,
  removeFriend,
  sendFriendRequest,
  searchUsers,
} from "../api/friends";
import "../styles/Friends.css";

function getInitials(name) {
  if (!name) return "?";
  return name.split(" ").map((w) => w[0]).join("").toUpperCase().slice(0, 2);
}

export default function Friends() {
  const { token, user } = useAuth();
  const [tab, setTab] = useState("friends");

  /* Data */
  const [friends, setFriends] = useState([]);
  const [pending, setPending] = useState([]);
  const [sent, setSent] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);

  const reload = useCallback(async () => {
    try {
      const [fRes, pRes, sRes] = await Promise.all([
        getFriends(token),
        getPendingRequests(token),
        getSentRequests(token),
      ]);
      setFriends(fRes.data || []);
      setPending(pRes.data || []);
      setSent(sRes.data || []);
    } catch (err) {
      console.error("Friends load error:", err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { reload(); }, [reload]);

  /* Actions */
  async function handleAccept(requesterId) {
    setActionLoading(requesterId);
    try {
      await acceptFriendRequest(token, requesterId);
      await reload();
    } catch (err) { alert(err.message); }
    finally { setActionLoading(null); }
  }

  async function handleDecline(requesterId) {
    setActionLoading(requesterId);
    try {
      await declineFriendRequest(token, requesterId);
      await reload();
    } catch (err) { alert(err.message); }
    finally { setActionLoading(null); }
  }

  async function handleRemove(friendId) {
    if (!confirm("Remove this friend?")) return;
    setActionLoading(friendId);
    try {
      await removeFriend(token, friendId);
      await reload();
    } catch (err) { alert(err.message); }
    finally { setActionLoading(null); }
  }

  async function handleSearch(e) {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    try {
      const res = await searchUsers(token, searchQuery.trim());
      setSearchResults(res.data || []);
    } catch (err) {
      console.error("Search error:", err);
    }
  }

  async function handleSendRequest(userId) {
    setActionLoading(userId);
    try {
      await sendFriendRequest(token, userId);
      setSearchResults((prev) => prev.filter((u) => u.id !== userId));
      await reload();
    } catch (err) { alert(err.message); }
    finally { setActionLoading(null); }
  }

  /* Helpers */
  const friendIds = new Set(friends.map((f) => f.id));
  const sentIds = new Set(sent.map((s) => s.receiver?.id));
  const pendingIds = new Set(pending.map((p) => p.requester?.id));
  const currentId = user ? Number(user.id) : null;

  if (loading) {
    return <div className="friends-page"><p className="friends-loading">Loading...</p></div>;
  }

  return (
    <div className="friends-page">
      <h1>Friends</h1>

      {/* Tabs */}
      <div className="friends-tabs">
        <button className={`tab ${tab === "friends" ? "tab--active" : ""}`} onClick={() => setTab("friends")}>
          Friends ({friends.length})
        </button>
        <button className={`tab ${tab === "pending" ? "tab--active" : ""}`} onClick={() => setTab("pending")}>
          Requests ({pending.length})
        </button>
        <button className={`tab ${tab === "sent" ? "tab--active" : ""}`} onClick={() => setTab("sent")}>
          Sent ({sent.length})
        </button>
        <button className={`tab ${tab === "search" ? "tab--active" : ""}`} onClick={() => setTab("search")}>
          🔎 Find players
        </button>
      </div>

      {/* Friends list */}
      {tab === "friends" && (
        <div className="friends-list">
          {friends.length === 0 && <p className="friends-empty">No friends yet. Search for players!</p>}
          {friends.map((f) => (
            <div key={f.id} className="friend-card">
              <div className="friend-card__left">
                <div className="friend-avatar">{getInitials(f.username)}</div>
                <div>
                  <div className="friend-name">{f.username}</div>
                  <div className="friend-city">{f.city || ""}</div>
                </div>
              </div>
              <button
                onClick={() => handleRemove(f.id)}
                disabled={actionLoading === f.id}
                className="btn-danger-sm"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Pending requests received */}
      {tab === "pending" && (
        <div className="friends-list">
          {pending.length === 0 && <p className="friends-empty">No pending requests.</p>}
          {pending.map((p) => {
            const requester = p.requester;
            if (!requester) return null;
            return (
              <div key={requester.id} className="friend-card">
                <div className="friend-card__left">
                  <div className="friend-avatar">{getInitials(requester.username)}</div>
                  <div>
                    <div className="friend-name">{requester.username}</div>
                    <div className="friend-city">{requester.city || ""}</div>
                  </div>
                </div>
                <div className="friend-card__actions">
                  <button
                    onClick={() => handleAccept(requester.id)}
                    disabled={actionLoading === requester.id}
                    className="btn-brown-sm"
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => handleDecline(requester.id)}
                    disabled={actionLoading === requester.id}
                    className="btn-outline-sm"
                  >
                    Decline
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Sent requests */}
      {tab === "sent" && (
        <div className="friends-list">
          {sent.length === 0 && <p className="friends-empty">No sent requests.</p>}
          {sent.map((s) => {
            const receiver = s.receiver;
            if (!receiver) return null;
            return (
              <div key={receiver.id} className="friend-card">
                <div className="friend-card__left">
                  <div className="friend-avatar">{getInitials(receiver.username)}</div>
                  <div>
                    <div className="friend-name">{receiver.username}</div>
                    <div className="friend-city">{receiver.city || ""}</div>
                  </div>
                </div>
                <span className="friend-badge">Pending...</span>
              </div>
            );
          })}
        </div>
      )}

      {/* Search */}
      {tab === "search" && (
        <div className="friends-search">
          <form onSubmit={handleSearch} className="friends-search-form">
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by username..."
              className="friends-search-input"
            />
            <button type="submit" className="btn-brown-sm">Search</button>
          </form>

          <div className="friends-list">
            {searchResults
              .filter((u) => u.id !== currentId)
              .map((u) => {
                const isFriend = friendIds.has(u.id);
                const isSent = sentIds.has(u.id);
                const isPending = pendingIds.has(u.id);

                return (
                  <div key={u.id} className="friend-card">
                    <div className="friend-card__left">
                      <div className="friend-avatar">{getInitials(u.username)}</div>
                      <div>
                        <div className="friend-name">{u.username}</div>
                        <div className="friend-city">{u.city || ""}</div>
                      </div>
                    </div>

                    {isFriend ? (
                      <span className="friend-badge friend-badge--ok">Already friends</span>
                    ) : isSent ? (
                      <span className="friend-badge">Request sent</span>
                    ) : isPending ? (
                      <span className="friend-badge">Waiting your response</span>
                    ) : (
                      <button
                        onClick={() => handleSendRequest(u.id)}
                        disabled={actionLoading === u.id}
                        className="btn-brown-sm"
                      >
                        Add friend
                      </button>
                    )}
                  </div>
                );
              })}
          </div>
        </div>
      )}
    </div>
  );
}