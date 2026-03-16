/**
 * Barre laterale de navigation et actions utilisateur.
 */

import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "../styles/Sidebar.css";

export default function Sidebar({ onNavigate }) {
  const navigate = useNavigate();
  const { logout } = useAuth();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <aside className="sidebar">
      <div className="sidebar__brand">BoardGame Hub</div>

      <NavLink to="/home" onClick={onNavigate} className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>Home</NavLink>
      <NavLink to="/friends" onClick={onNavigate} className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>Friends</NavLink>
      <NavLink to="/events" onClick={onNavigate} className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>Events</NavLink>
      <NavLink to="/games" onClick={onNavigate} className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>Games</NavLink>
      <NavLink to="/profile" onClick={onNavigate} className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>Profile</NavLink>

      <div className="sidebar__create">
        <NavLink to="/create-event" onClick={onNavigate} className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}>+ Create Event</NavLink>
      </div>

      <button onClick={handleLogout} className="sidebar__logout">
        Logout
      </button>
    </aside>
  );
}