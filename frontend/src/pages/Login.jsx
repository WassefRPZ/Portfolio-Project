import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { loginUser } from "../api/auth";
import D20Fantasy from "../components/D20Fantasy";
import "../styles/Auth.css";

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
    <div className="auth-page">

      <div className="auth-left">
        <div className="auth-brand">
          <h1>BoardGame Hub</h1>
          <p>Welcome back! Please enter your details to sign in</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && (
            <div className="auth-error auth-error--login">
              {error}
            </div>
          )}
          <div className="auth-field">
            <label>Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="auth-field">
            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <div className="auth-remember">
            <label>
              <input type="checkbox" /> Remember me
            </label>
          </div>

          <button type="submit" className="auth-submit">
            Sign In
          </button>

          <div className="auth-switch">
            Don't have an account?{" "}
            <Link to="/signup">Sign up</Link>
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