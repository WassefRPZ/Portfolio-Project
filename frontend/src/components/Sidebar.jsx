import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "../styles/Sidebar.css";

export default function Sidebar() {
  const navigate = useNavigate();
  const { logout } = useAuth();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">🎲 BoardGame</div>

      <NavLink to="/home" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>Home</NavLink>
      <NavLink to="/friends" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>Friends</NavLink>
      <NavLink to="/events" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>Events</NavLink>
      <NavLink to="/games" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>Games</NavLink>

      <div className="sidebar__create">
        <NavLink to="/create-event" className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>+ Create Event</NavLink>
      </div>

      <button onClick={handleLogout} className="sidebar__logout">
        Logout
      </button>
    </aside>
  );
}