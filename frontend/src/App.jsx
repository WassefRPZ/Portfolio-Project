import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import Home from "./pages/Home";
import Friends from "./pages/Friends";
import Events from "./pages/Events";
import Games from "./pages/Games";
import CreateEvent from "./pages/CreateEvent";
import Signup from "./pages/Signup";

import AppLayout from "./components/AppLayout";
import ProtectedRoute from "./routes/ProtectedRoute";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Arrivée sur le site => /login */}
        <Route path="/" element={<Navigate to="/login" replace />} />

        {/* Page publique */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Pages protégées + layout (sidebar) */}
        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/home" element={<Home />} />
          <Route path="/friends" element={<Friends />} />
          <Route path="/events" element={<Events />} />
          <Route path="/games" element={<Games />} />
          <Route path="/create-event" element={<CreateEvent />} />
        </Route>

        {/* 404 */}
        <Route path="*" element={<h2 style={{ padding: 24 }}>404 Not Found</h2>} />
      </Routes>
    </BrowserRouter>
  );
}
