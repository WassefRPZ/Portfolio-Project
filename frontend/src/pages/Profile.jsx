/**
 * Page profil : consultation et modification des informations utilisateur.
 */

import { useState, useEffect, useRef } from "react";
import { useAuth } from "../context/AuthContext";
import { getMe, updateProfile } from "../api/users";
import { getFavoriteGames } from "../api/games";
import "../styles/Profile.css";

function getInitials(name) {
  if (!name) return "?";
  return name
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export default function Profile() {
  const { token, user } = useAuth();
  const fileInputRef = useRef(null);

  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [username, setUsername] = useState("");
  const [bio, setBio] = useState("");
  const [city, setCity] = useState("");
  const [region, setRegion] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [favoriteGames, setFavoriteGames] = useState([]);

  useEffect(() => {
    async function fetchData() {
      try {
        const [profileRes, favRes] = await Promise.all([
          getMe(token),
          getFavoriteGames(token),
        ]);
        const data = profileRes.data;
        setProfile(data);
        setUsername(data.username || "");
        setBio(data.bio || "");
        setCity(data.city || "");
        setRegion(data.region || "");
        setFavoriteGames(favRes.data || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [token]);

  function handleImageChange(e) {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  }

  function handleCancel() {
    setEditing(false);
    setError("");
    setSuccess("");
    setImageFile(null);
    setImagePreview(null);
    if (profile) {
      setUsername(profile.username || "");
      setBio(profile.bio || "");
      setCity(profile.city || "");
      setRegion(profile.region || "");
    }
  }

  async function handleSave(e) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setSaving(true);

    try {
      const formData = new FormData();
      formData.append("username", username);
      formData.append("bio", bio);
      formData.append("city", city);
      formData.append("region", region);
      if (imageFile) {
        formData.append("image", imageFile);
      }

      const res = await updateProfile(token, formData);
      setProfile(res.data);
      setEditing(false);
      setImageFile(null);
      setImagePreview(null);
      setSuccess("Profile updated!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="profile-page">
        <p className="profile-loading">Loading profile...</p>
      </div>
    );
  }

  const avatarUrl = imagePreview || profile?.profile_image_url;

  return (
    <div className="profile-page">
      <h1>My Profile</h1>

      {error && <div className="profile-msg profile-msg--error">{error}</div>}
      {success && <div className="profile-msg profile-msg--success">{success}</div>}

      <div className="profile-card">
        <div className="profile-avatar-section">
          {avatarUrl ? (
            <img src={avatarUrl} alt="avatar" className="profile-avatar-img" />
          ) : (
            <div className="profile-avatar-placeholder">
              {getInitials(profile?.username)}
            </div>
          )}

          {editing && (
            <>
              <button
                type="button"
                className="btn-outline-sm"
                onClick={() => fileInputRef.current?.click()}
              >
                Change photo
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                hidden
              />
            </>
          )}
        </div>

        {!editing ? (
          <div className="profile-info">
            <div className="profile-field">
              <span className="profile-label">Username</span>
              <span className="profile-value">{profile?.username}</span>
            </div>
            <div className="profile-field">
              <span className="profile-label">Email</span>
              <span className="profile-value">{user?.email || "—"}</span>
            </div>
            <div className="profile-field">
              <span className="profile-label">City</span>
              <span className="profile-value">{profile?.city || "—"}</span>
            </div>
            <div className="profile-field">
              <span className="profile-label">Region</span>
              <span className="profile-value">{profile?.region || "—"}</span>
            </div>
            <div className="profile-field">
              <span className="profile-label">Bio</span>
              <span className="profile-value">{profile?.bio || "No bio yet."}</span>
            </div>

            <button className="btn-primary" onClick={() => setEditing(true)}>
              Edit Profile
            </button>
          </div>
        ) : (
          <form className="profile-form" onSubmit={handleSave}>
            <div className="profile-field">
              <label className="profile-label">Username</label>
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="profile-field">
              <label className="profile-label">City</label>
              <input
                value={city}
                onChange={(e) => setCity(e.target.value)}
              />
            </div>
            <div className="profile-field">
              <label className="profile-label">Region</label>
              <input
                value={region}
                onChange={(e) => setRegion(e.target.value)}
              />
            </div>
            <div className="profile-field">
              <label className="profile-label">Bio</label>
              <textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                rows={3}
                placeholder="Tell us about yourself..."
              />
            </div>

            <div className="profile-form-actions">
              <button type="submit" className="btn-primary" disabled={saving}>
                {saving ? "Saving..." : "Save"}
              </button>
              <button type="button" className="btn-outline-sm" onClick={handleCancel}>
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>

      <div className="profile-favorites">
        <h2>Favorite Games</h2>
        {favoriteGames.length === 0 ? (
          <p className="profile-favorites-empty">
            No favorites yet — head to the Games page to add some!
          </p>
        ) : (
          <div className="profile-favorites-grid">
            {favoriteGames.map((game) => (
              <div key={game.id} className="profile-fav-card">
                {game.image_url ? (
                  <img
                    src={game.image_url}
                    alt={game.name}
                    className="profile-fav-card__img"
                  />
                ) : (
                  <div className="profile-fav-card__placeholder">?</div>
                )}
                <span className="profile-fav-card__name">{game.name}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
