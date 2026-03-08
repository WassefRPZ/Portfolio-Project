import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { createEvent } from "../api/events";
import { getAllGames } from "../api/games";
import "../styles/CreateEvent.css";

export default function CreateEvent() {
  const { token } = useAuth();
  const navigate = useNavigate();

  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [title, setTitle] = useState("");
  const [gameId, setGameId] = useState("");
  const [location, setLocation] = useState("");
  const [dateTime, setDateTime] = useState("");
  const [maxPlayers, setMaxPlayers] = useState("");
  const [description, setDescription] = useState("");
  const [coverFile, setCoverFile] = useState(null);

  useEffect(() => {
    async function loadGames() {
      try {
        const res = await getAllGames(token);
        setGames(res.data || []);
      } catch (err) {
        console.error("Failed to load games:", err);
      }
    }
    loadGames();
  }, [token]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (!title.trim() || !gameId || !location.trim() || !dateTime || !maxPlayers) {
      setError("All fields marked with * are required.");
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("title", title.trim());
      formData.append("game_id", Number(gameId));
      formData.append("location_text", location.trim());
      formData.append("date_time", dateTime);
      formData.append("max_players", Number(maxPlayers));
      if (description.trim()) formData.append("description", description.trim());
      if (coverFile) formData.append("cover", coverFile);

      await createEvent(token, formData);
      navigate("/events");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="create-event-page">
      <h1>Create Event</h1>

      <form onSubmit={handleSubmit} className="create-event-form">
        {error && <div className="create-event-error">{error}</div>}

        <div className="form-field">
          <label>Title *</label>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Catan Night at the café"
            required
          />
        </div>

        <div className="form-field">
          <label>Game *</label>
          <select value={gameId} onChange={(e) => setGameId(e.target.value)} required>
            <option value="">Select a game...</option>
            {games.map((g) => (
              <option key={g.id} value={g.id}>
                {g.name} ({g.min_players}–{g.max_players} players)
              </option>
            ))}
          </select>
        </div>

        <div className="form-field">
          <label>Location (full address) *</label>
          <input
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="e.g. 12 rue de Rivoli, Paris"
            required
          />
        </div>

        <div className="form-row">
          <div className="form-field">
            <label>Date & Time *</label>
            <input
              type="datetime-local"
              value={dateTime}
              onChange={(e) => setDateTime(e.target.value)}
              required
            />
          </div>

          <div className="form-field">
            <label>Max Players *</label>
            <input
              type="number"
              min="2"
              max="100"
              value={maxPlayers}
              onChange={(e) => setMaxPlayers(e.target.value)}
              placeholder="e.g. 6"
              required
            />
          </div>
        </div>

        <div className="form-field">
          <label>Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional details about the event..."
            rows={4}
          />
        </div>

        <div className="form-field">
          <label>Cover Image (optional)</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setCoverFile(e.target.files[0] || null)}
          />
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="btn-brown">
            {loading ? "Creating..." : "Create Event"}
          </button>
          <button type="button" onClick={() => navigate("/events")} className="btn-outline">
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}