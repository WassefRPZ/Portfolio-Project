/**
 * Page d'inscription : formulaire et logique de creation de compte.
 */

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { registerUser } from "../api/auth";
import D20Fantasy from "../components/D20Fantasy";
import "../styles/Auth.css";

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
    <div className="auth-page">
      <div className="auth-left">
        <div className="auth-brand">
          <h1>BoardGame Hub</h1>
          <p>Create your account to start organizing game nights</p>
        </div>

        {error && (
          <div className="auth-error auth-error--signup">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-field">
            <label>Username</label>
            <input
              placeholder="Choose a username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="auth-field">
            <label>City</label>
            <input
              placeholder="Enter your city"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              required
            />
          </div>

          <div className="auth-field">
            <label>Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="auth-field">
            <label>Password</label>
            <input
              type="password"
              placeholder="Create a password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <small className="auth-hint">
              Min. 8 characters, with uppercase, lowercase, number &amp; special character
            </small>
          </div>

          <div className="auth-field">
            <label>Confirm Password</label>
            <input
              type="password"
              placeholder="Confirm password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>

          <button type="submit" className="auth-submit">
            Create Account
          </button>

          <div className="auth-switch">
            Already have an account?{" "}
            <Link to="/login">Log in</Link>
          </div>
        </form>
      </div>

      <div className="auth-right">
        <D20Fantasy />
        <h2>Join the Adventure</h2>
      </div>
    </div>
  );
}