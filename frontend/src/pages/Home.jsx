/**
 * Page d'accueil : conteneur principal des contenus du tableau de bord.
 */

import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getMe } from "../api/users";
import { getFeed, createPost, deletePost } from "../api/posts";
import { getEvents } from "../api/events";
import { getFriends } from "../api/friends";
import { getAllGames } from "../api/games";
import { FiSearch } from "react-icons/fi";
import "../styles/Home.css";

function timeAgo(iso) {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

function getInitials(name) {
  if (!name) return "?";
  return name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

function formatEventDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function Home() {
  const { token, user } = useAuth();
  const navigate = useNavigate();

  const [posts, setPosts] = useState([]);
  const [events, setEvents] = useState([]);
  const [friends, setFriends] = useState([]);
  const [games, setGames] = useState([]);
  const [newPost, setNewPost] = useState("");
  const [posting, setPosting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [myAvatar, setMyAvatar] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [showResults, setShowResults] = useState(false);
  const searchRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setShowResults(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    async function load() {
      try {
        const [feedRes, eventsRes, meRes, friendsRes, gamesRes] = await Promise.all([
          getFeed(token),
          getEvents(token, { limit: 4 }),
          getMe(token),
          getFriends(token),
          getAllGames(token),
        ]);
        setPosts(feedRes.data || []);
        setEvents(eventsRes.data || []);
        setMyAvatar(meRes.data?.profile_image_url || null);
        setFriends(friendsRes.data || []);
        setGames(gamesRes.data || []);
      } catch (err) {
        console.error("Home load error:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [token]);

  const searchResults = searchQuery.trim().length > 0 ? {
    friends: friends.filter((f) =>
      f.username?.toLowerCase().includes(searchQuery.toLowerCase())
    ).slice(0, 4),
    games: games.filter((g) =>
      g.name?.toLowerCase().includes(searchQuery.toLowerCase())
    ).slice(0, 4),
    events: events.filter((e) =>
      e.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      e.city?.toLowerCase().includes(searchQuery.toLowerCase())
    ).slice(0, 4),
  } : null;

  const hasResults = searchResults && (
    searchResults.friends.length > 0 ||
    searchResults.games.length > 0 ||
    searchResults.events.length > 0
  );

  async function handlePost() {
    if (!newPost.trim() || posting) return;
    setPosting(true);
    try {
      const res = await createPost(token, newPost.trim());
      const newPostData = {
        ...res.data,
        username: res.data.username || user?.username,
        profile_image_url: res.data.profile_image_url || myAvatar,
      };
      setPosts((prev) => [newPostData, ...prev]);
      setNewPost("");
    } catch (err) {
      console.error("Post error:", err);
    } finally {
      setPosting(false);
    }
  }

  async function handleDeletePost(postId) {
    if (!window.confirm("Delete this post?")) return;
    try {
      await deletePost(token, postId);
      setPosts((prev) => prev.filter((p) => p.id !== postId));
    } catch (err) {
      alert(err.message);
    }
  }

  const myInitials = user ? getInitials(user.username || user.email) : "?";

  if (loading) {
    return <div className="home-loading">Loading...</div>;
  }

  return (
    <div className="home-layout">

      <div className="home-main">

        <div className="home-search" ref={searchRef}>
          <div className="home-search-bar">
            <FiSearch size={18} className="home-search-icon" />
            <input
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setShowResults(true);
              }}
              onFocus={() => searchQuery.trim() && setShowResults(true)}
              placeholder="Search friends, games, events..."
              className="home-search-input"
            />
          </div>

          {showResults && searchQuery.trim() && (
            <div className="home-search-dropdown">
              {!hasResults && (
                <div className="search-no-results">No results found</div>
              )}

              {searchResults.friends.length > 0 && (
                <div className="search-section">
                  <div className="search-section__title">Friends</div>
                  {searchResults.friends.map((f) => (
                    <div
                      key={f.id}
                      className="search-result-item"
                      onClick={() => { navigate("/friends"); setShowResults(false); }}
                    >
                      {f.username}
                    </div>
                  ))}
                </div>
              )}

              {searchResults.games.length > 0 && (
                <div className="search-section">
                  <div className="search-section__title">Games</div>
                  {searchResults.games.map((g) => (
                    <div
                      key={g.id}
                      className="search-result-item"
                      onClick={() => { navigate("/games"); setShowResults(false); }}
                    >
                      {g.name}
                    </div>
                  ))}
                </div>
              )}

              {searchResults.events.length > 0 && (
                <div className="search-section">
                  <div className="search-section__title">Events</div>
                  {searchResults.events.map((e) => (
                    <div
                      key={e.id}
                      className="search-result-item"
                      onClick={() => { navigate(`/events/${e.id}`); setShowResults(false); }}
                    >
                      {e.title}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="share-box">
          {myAvatar ? (
            <img src={myAvatar} alt="avatar" className="avatar avatar--img" />
          ) : (
            <div className="avatar">{myInitials}</div>
          )}

          <input
            value={newPost}
            onChange={(e) => setNewPost(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handlePost()}
            placeholder="Share your gaming experience..."
            className="share-input"
          />

          <button
            onClick={handlePost}
            disabled={posting || !newPost.trim()}
            className="share-btn"
          >
            {posting ? "..." : "Post"}
          </button>
        </div>

        {posts.length === 0 && (
          <div className="post-empty">
            No posts yet. Be the first to share!
          </div>
        )}

        {posts.map((post) => (
          <div key={post.id} className="post-card">
            <div className="post-header">
              {post.profile_image_url ? (
                <img src={post.profile_image_url} alt="avatar" className="avatar avatar--lg avatar--img" />
              ) : (
                <div className="avatar avatar--lg">
                  {getInitials(post.username)}
                </div>
              )}

              <div>
                <div className="post-username">{post.username || "User"}</div>
                <div className="post-time">
                  {timeAgo(post.created_at)}
                </div>
              </div>
            </div>

            <div className="post-content">{post.content}</div>

            {post.author_id === Number(user?.id) && (
              <button
                className="post-delete-btn"
                onClick={() => handleDeletePost(post.id)}
              >
                Delete
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="home-sidebar">
        <h3>Upcoming Events</h3>

        {events.length === 0 && (
          <div className="sidebar-empty">No upcoming events.</div>
        )}

        {events.map((event) => (
          <div
            key={event.id}
            className="event-mini"
            onClick={() => navigate(`/events/${event.id}`)}
            style={{ cursor: "pointer" }}
          >
            <div className="event-mini__title">{event.title}</div>
            <div className="event-mini__date">
              {formatEventDate(event.date_time)}
            </div>
            <div className="event-mini__players">
              {event.current_players}/{event.max_players} players
            </div>
          </div>
        ))}

        <button onClick={() => navigate("/events")} className="btn-primary">
          View All Events
        </button>
      </div>
    </div>
  );
}