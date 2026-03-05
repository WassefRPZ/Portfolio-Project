import { createContext, useContext, useMemo, useState } from "react";

const AuthContext = createContext(null);

/**
 * Decode le payload d'un JWT sans librairie externe.
 * Retourne { username, email, role, sub, exp, ... } ou null si invalide.
 */
function decodeToken(token) {
  try {
    const payload = token.split(".")[1];
    // atob ne gère pas le base64url → on remplace les caractères
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json);
  } catch {
    return null;
  }
}

/**
 * Vérifie si un token est expiré en lisant le champ `exp`.
 */
function isTokenExpired(token) {
  const decoded = decodeToken(token);
  if (!decoded?.exp) return true;
  // exp est en secondes, Date.now() en millisecondes
  return decoded.exp * 1000 < Date.now();
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => {
    const stored = localStorage.getItem("token");
    // Si le token stocké est expiré, on le supprime directement
    if (stored && isTokenExpired(stored)) {
      localStorage.removeItem("token");
      return null;
    }
    return stored;
  });

  const isAuthenticated = Boolean(token);

  // Infos utilisateur extraites du token (username, email, role)
  const user = useMemo(() => {
    if (!token) return null;
    const decoded = decodeToken(token);
    if (!decoded) return null;
    return {
      id: decoded.sub,
      username: decoded.username ?? null,
      email: decoded.email ?? null,
      role: decoded.role ?? "user",
    };
  }, [token]);

  function login(newToken) {
    localStorage.setItem("token", newToken);
    setToken(newToken);
  }

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
  }

  const value = useMemo(
    () => ({ token, user, isAuthenticated, login, logout }),
    [token, user, isAuthenticated]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
