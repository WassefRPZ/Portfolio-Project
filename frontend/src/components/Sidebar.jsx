import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const linkStyle = ({ isActive }) => ({
  display: "block",
  padding: "12px 14px",
  marginBottom: 8,
  borderRadius: 10,
  textDecoration: "none",
  color: isActive ? "#FFFFFF" : "#2E2E2E",
  background: isActive ? "#6D4C41" : "transparent",
});

export default function Sidebar() {
  const navigate = useNavigate();
  const { logout } = useAuth();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <aside style={{ width: 260, padding: 16, background: "#F5F1E6" }}>
      <div style={{ fontWeight: 800, color: "#6D4C41", marginBottom: 16 }}>
        🎲 BoardGame
      </div>

      <NavLink to="/home" style={linkStyle}>Home</NavLink>
      <NavLink to="/friends" style={linkStyle}>Friends</NavLink>
      <NavLink to="/events" style={linkStyle}>Events</NavLink>
      <NavLink to="/games" style={linkStyle}>Games</NavLink>

      <div style={{ marginTop: 16 }}>
        <NavLink to="/create-event" style={linkStyle}>+ Create Event</NavLink>
      </div>

      <button
        onClick={handleLogout}
        style={{
          marginTop: 16,
          padding: 12,
          width: "100%",
          borderRadius: 10,
          border: "none",
          background: "#6D4C41",
          color: "#FFFFFF",
          fontWeight: 600,
          cursor: "pointer",
        }}
      >
        Logout
      </button>
    </aside>
  );
}