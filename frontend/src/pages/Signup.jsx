import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { registerUser } from "../api/auth";
import D20Fantasy from "../components/D20Fantasy";

export default function Signup() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [city, setCity] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      const res = await registerUser(username, email, password, city);
      login(res.data.access_token);
      navigate("/home", { replace: true });
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* LEFT SIDE */}
      <div
        style={{
          flex: 1,
          background: "#ECECEC",
          padding: "80px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <div style={{ marginBottom: 40 }}>
          <h1 style={{ color: "#6D4C41", fontSize: 36, marginBottom: 10 }}>
            🎲 BoardGame
          </h1>
          <p style={{ color: "#555" }}>
            Create your account to start organizing game nights
          </p>
        </div>

        {error && (
          <div
            style={{
              maxWidth: 400,
              marginBottom: 16,
              padding: 12,
              borderRadius: 10,
              border: "1px solid #C62828",
              background: "#fff",
              color: "#C62828",
              fontWeight: 700,
            }}
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ maxWidth: 400 }}>
          <div style={{ marginBottom: 20 }}>
            <label>Username</label>
            <input
              placeholder="Choose a username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: "100%",
                padding: 14,
                marginTop: 6,
                borderRadius: 10,
                border: "1px solid #D5CFCB",
                background: "#F8F8F8",
              }}
              required
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label>City</label>
            <input
              placeholder="Enter your city"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              style={{
                width: "100%",
                padding: 14,
                marginTop: 6,
                borderRadius: 10,
                border: "1px solid #D5CFCB",
                background: "#F8F8F8",
              }}
              required
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label>Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{
                width: "100%",
                padding: 14,
                marginTop: 6,
                borderRadius: 10,
                border: "1px solid #D5CFCB",
                background: "#F8F8F8",
              }}
              required
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label>Password</label>
            <input
              type="password"
              placeholder="Create a password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: "100%",
                padding: 14,
                marginTop: 6,
                borderRadius: 10,
                border: "1px solid #D5CFCB",
                background: "#F8F8F8",
              }}
              required
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label>Confirm Password</label>
            <input
              type="password"
              placeholder="Confirm password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              style={{
                width: "100%",
                padding: 14,
                marginTop: 6,
                borderRadius: 10,
                border: "1px solid #D5CFCB",
                background: "#F8F8F8",
              }}
              required
            />
          </div>

          <button
            type="submit"
            style={{
              width: "100%",
              padding: 16,
              borderRadius: 12,
              border: "none",
              background: "#6D4C41",
              color: "white",
              fontWeight: "bold",
              fontSize: 16,
              cursor: "pointer",
            }}
          >
            Create Account
          </button>

          <div style={{ marginTop: 30, textAlign: "center" }}>
            Already have an account?{" "}
            <Link to="/login" style={{ color: "#C62828", cursor: "pointer" }}>
              Log in
            </Link>
          </div>
        </form>
      </div>

      {/* RIGHT SIDE */}
      <div
        style={{
          flex: 1,
          background: "#E8E3D8",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <D20Fantasy />
        <h2 style={{ marginTop: 40, color: "#6D4C41" }}>Join the Adventure</h2>
      </div>
    </div>
  );
}