/**
 * Contexte d'authentification React (provider + hooks d'accès).
 * 
 * Gère de manière centralisée:
 * - Stockage du token JWT dans localStorage
 * - Décodage du token pour extraction des données utilisateur
 * - Vérification de l'expiration du token
 * - État global d'authentification accessible via useAuth() partout
 */

import { createContext, useContext, useMemo, useState } from "react";

const AuthContext = createContext(null);

/**
 * Décode un token JWT en extr ayant sa charge utile (payload).
 * Le payload contient user_id, username, email, role, exp (expiration).
 * 
 * @param {string} token - Token JWT complet
 * @returns {object|null} Payload décodé ou null en cas d'erreur
 */
function decodeToken(token) {
  try {
    const payload = token.split(".")[1];  /** Récupère la partie payload (2eme segment) */
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));  /** Décodage base64 */
    return JSON.parse(json);  /** Parse en objet */
  } catch {
    return null;  /** Erreur de parsing → retourne null */
  }
}

/**
 * Vérifie si un token JWT est expiré en comparant son timestamp d'expiration.
 * 
 * @param {string} token - Token JWT
 * @returns {boolean} true si expiré, false sinon
 */
function isTokenExpired(token) {
  const decoded = decodeToken(token);
  if (!decoded?.exp) return true;  /** Pas de champ exp → considéré expiré */
  return decoded.exp * 1000 < Date.now();  /** exp est en secondes, Date.now() en ms */
}

export function AuthProvider({ children }) {
  /**
   * État du token JWT avec initialisation depuis localStorage.
   * Si le token stocké est expiré, il est supprimé automatiquement au chargement.
   */
  const [token, setToken] = useState(() => {
    const stored = localStorage.getItem("token");  /** Récupère le token du stockage */
    if (stored && isTokenExpired(stored)) {
      localStorage.removeItem("token");  /** Nettoie si expiré */
      return null;
    }
    return stored;  /** Retourne le token valide ou null */
  });

  /** Détermine si l'utilisateur est authentifié (a un token valide) */
  const isAuthenticated = Boolean(token);

  /**
   * Décode le token et extrait les données utilisateur.
   * Dérivé de 'token' et recalculé lors de chaque changement pour éviter
   * les données obsolètes après une modification du token.
   */
  const user = useMemo(() => {
    if (!token) return null;  /** Pas de token → pas d'utilisateur */
    const decoded = decodeToken(token);  /** Décode le JWT */
    if (!decoded) return null;  /** Erreur de décodage */
    return {
      id: decoded.sub,  /** Subject (ID utilisateur) du token */
      username: decoded.username ?? null,  /** Pseudonyme */
      email: decoded.email ?? null,  /** Email */
      role: decoded.role ?? "user",  /** Rôle (user ou admin) */
    };
  }, [token]);

  /**
   * Enregistre un nouvel utilisateur lors de la connexion.
   * Sauvegarde le token en localStorage ET met à jour l'état React.
   * @param {string} newToken - Token JWT reçu du serveur
   */
  function login(newToken) {
    localStorage.setItem("token", newToken);  /** Persiste en localStorage */
    setToken(newToken);  /** Met à jour l'état React */
  }

  /**
   * Déconnecte l'utilisateur.
   * Supprime le token du stockage et du state.
   */
  function logout() {
    localStorage.removeItem("token");  /** Nettoie le localStorage */
    setToken(null);  /** Vide l'état */
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
