import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import {
  getAllGames,
  getFavoriteGames,
  addFavoriteGame,
  removeFavoriteGame,
} from "../api/games";
import "../styles/Games.css";

export default function Games() {
  const { token } = useAuth();

  const [games, setGames] = useState([]);
  const [favoriteIds, setFavoriteIds] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [toggling, setToggling] = useState(null);

  const reload = useCallback(async () => {
    try {
      const [gamesRes, favRes] = await Promise.all([
        getAllGames(token),
        getFavoriteGames(token),
      ]);
      setGames(gamesRes.data || []);
      const ids = new Set((favRes.data || []).map((g) => g.id));
      setFavoriteIds(ids);
    } catch (err) {
      console.error("Games load error:", err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { reload(); }, [reload]);

  async function toggleFavorite(gameId) {
    setToggling(gameId);
    try {
      if (favoriteIds.has(gameId)) {
        await removeFavoriteGame(token, gameId);
        setFavoriteIds((prev) => { const s = new Set(prev); s.delete(gameId); return s; });
      } else {
        await addFavoriteGame(token, gameId);
        setFavoriteIds((prev) => new Set(prev).add(gameId));
      }
    } catch (err) {
      alert(err.message);
    } finally {
      setToggling(null);
    }
  }

  const filtered = games.filter((g) => {
    if (!query.trim()) return true;
    return g.name.toLowerCase().includes(query.toLowerCase());
  });

  if (loading) {
    return <div className="games-page"><p className="games-loading">Loading games...</p></div>;
  }

  return (
    <div className="games-page">
      <h1>Board Games</h1>

      {/* Search */}
      <div className="games-search-bar">
        <span className="games-search-icon">🔎</span>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search games..."
        />
      </div>

      {/* Grid */}
      <div className="games-grid">
        {filtered.map((game) => {
          const isFav = favoriteIds.has(game.id);
          const isToggling = toggling === game.id;

          return (
            <div key={game.id} className="game-card">
              {game.image_url ? (
                <img
                  src={game.image_url}
                  alt={game.name}
                  className="game-card__img"
                />
              ) : (
                <div className="game-card__placeholder">🎲</div>
              )}

              <div className="game-card__body">
                <div className="game-card__name">{game.name}</div>

                <div className="game-card__meta">
                  <span>👥 {game.min_players}–{game.max_players}</span>
                  <span>⏱ {game.play_time_minutes} min</span>
                </div>

                {game.description && (
                  <p className="game-card__desc">
                    {game.description.length > 100
                      ? game.description.slice(0, 100) + "…"
                      : game.description}
                  </p>
                )}

                <button
                  onClick={() => toggleFavorite(game.id)}
                  disabled={isToggling}
                  className={`game-fav-btn ${isFav ? "game-fav-btn--active" : ""}`}
                >
                  {isFav ? "★ Favorite" : "☆ Add to Favorites"}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {filtered.length === 0 && (
        <p className="games-empty">No games found.</p>
      )}
    </div>
  );
}