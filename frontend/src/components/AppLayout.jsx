import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import "../styles/AppLayout.css";

export default function AppLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="app-layout">

      {/* SIDEBAR */}
      <div
        className={`app-layout__sidebar ${
          isSidebarOpen ? "app-layout__sidebar--open" : "app-layout__sidebar--closed"
        }`}
      >
        <Sidebar />
      </div>

      {/* MAIN CONTENT */}
      <div className={`app-layout__main ${isSidebarOpen ? "app-layout__main--shifted" : ""}`}>
        {/* Toggle Button */}
        <button
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="app-layout__toggle"
        >
          ☰
        </button>

        <Outlet />
      </div>
    </div>
  );
}