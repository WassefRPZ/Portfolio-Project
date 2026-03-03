import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { loginUser } from "../api/auth";
import D20Fantasy from "../components/D20Fantasy";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      const res = await loginUser(email, password);
      login(res.data.access_token);
      navigate("/home");
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
            Welcome back! Please enter your details to sign in
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ maxWidth: 400 }}>
          {error && (
            <div style={{
              padding: 12,
              marginBottom: 16,
              borderRadius: 10,
              background: "#FDECEA",
              color: "#C62828",
              fontSize: 14,
            }}>
              {error}
            </div>
          )}
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
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
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
            />
          </div>

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: 20,
              fontSize: 14,
            }}
          >
            <label>
              <input type="checkbox" /> Remember me
            </label>
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
            Sign In
          </button>

          <div style={{ marginTop: 30, textAlign: "center" }}>
            Don't have an account?{" "}
            <Link to="/signup" style={{ color: "#C62828", cursor: "pointer" }}>
              Sign up
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

        <h2 style={{ marginTop: 40, color: "#6D4C41" }}>
          Join the Adventure
        </h2>
      </div>
    </div>
  );
}