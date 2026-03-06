import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getFeed, createPost } from "../api/posts";
import { getEvents } from "../api/events";
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
  const [newPost, setNewPost] = useState("");
  const [posting, setPosting] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [feedRes, eventsRes] = await Promise.all([
          getFeed(token),
          getEvents(token, { limit: 4 }),
        ]);
        setPosts(feedRes.data || []);
        setEvents(eventsRes.data || []);
      } catch (err) {
        console.error("Home load error:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [token]);

  async function handlePost() {
    if (!newPost.trim() || posting) return;
    setPosting(true);
    try {
      const res = await createPost(token, newPost.trim());
      setPosts((prev) => [res.data, ...prev]);
      setNewPost("");
    } catch (err) {
      console.error("Post error:", err);
    } finally {
      setPosting(false);
    }
  }

  const myInitials = user ? getInitials(user.username || user.email) : "?";

  if (loading) {
    return <div className="home-loading">Loading...</div>;
  }

  return (
    <div className="home-layout">

      {/* MAIN CENTER */}
      <div className="home-main">

        {/* Share box */}
        <div className="share-box">
          <div className="avatar">{myInitials}</div>

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

        {/* Posts */}
        {posts.length === 0 && (
          <div className="post-empty">
            No posts yet. Be the first to share!
          </div>
        )}

        {posts.map((post) => (
          <div key={post.id} className="post-card">
            <div className="post-header">
              <div className="avatar avatar--lg">
                {getInitials(post.username)}
              </div>

              <div>
                <div className="post-username">{post.username || "User"}</div>
                <div className="post-time">
                  {timeAgo(post.created_at)}
                </div>
              </div>
            </div>

            <div className="post-content">{post.content}</div>

            <div className="post-stats">
              <span>{post.likes_count || 0} likes</span>
              <span>{post.comments_count || 0} comments</span>
            </div>
          </div>
        ))}
      </div>

      {/* RIGHT COLUMN */}
      <div className="home-sidebar">
        <h3>Upcoming Events</h3>

        {events.length === 0 && (
          <div className="sidebar-empty">No upcoming events.</div>
        )}

        {events.map((event) => (
          <div key={event.id} className="event-mini">
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