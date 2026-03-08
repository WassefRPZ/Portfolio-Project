import { useState, useEffect } from "react";
import { Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getMe } from "../api/users";
import Sidebar from "./Sidebar";
import "../styles/AppLayout.css";

function getInitials(name) {
  if (!name) return "?";
  return name.split(" ").map((w) => w[0]).join("").toUpperCase().slice(0, 2);
}

export default function AppLayout() {
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const [isSidebarOpen, setIsSidebarOpen] = useState(window.innerWidth > 768);
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [avatarUrl, setAvatarUrl] = useState(null);

  useEffect(() => {
    function handleResize() {
      const mobile = window.innerWidth <= 768;
      setIsMobile(mobile);
      if (mobile) setIsSidebarOpen(false);
    }
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  function closeSidebarOnMobile() {
    if (window.innerWidth <= 768) setIsSidebarOpen(false);
  }

  useEffect(() => {
    async function loadAvatar() {
      try {
        const res = await getMe(token);
        setAvatarUrl(res.data?.profile_image_url || null);
      } catch { /* ignore */ }
    }
    if (token) loadAvatar();
  }, [token]);

  return (
    <div className="app-layout">

      {isSidebarOpen && isMobile && (
        <div className="app-layout__overlay" onClick={() => setIsSidebarOpen(false)} />
      )}
      <div
        className={`app-layout__sidebar ${
          isSidebarOpen ? "app-layout__sidebar--open" : "app-layout__sidebar--closed"
        }`}
      >
        <Sidebar onNavigate={closeSidebarOnMobile} />
      </div>

      <div className={`app-layout__main ${isSidebarOpen ? "app-layout__main--shifted" : ""}`}>
        <div className="app-topbar">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="app-layout__toggle"
          >
            ☰
          </button>

          <div className="app-topbar__profile" onClick={() => navigate("/profile")}>
            {avatarUrl ? (
              <img src={avatarUrl} alt="profile" className="app-topbar__avatar-img" />
            ) : (
              <div className="app-topbar__avatar">
                {getInitials(user?.username)}
              </div>
            )}
          </div>
        </div>

        <Outlet />
      </div>
    </div>
  );
}