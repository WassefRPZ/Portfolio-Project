/**
 * Client API centralisé.
 * - Ajoute automatiquement le header Authorization si un token est fourni.
 * - Intercepte les réponses 401 → supprime le token et redirige vers /login.
 */

const API = "/api/v1";

export async function apiRequest(endpoint, { token, ...options } = {}) {
  const headers = { ...options.headers };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API}${endpoint}`, { ...options, headers });

  // Token expiré ou invalide → on déconnecte
  if (res.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "/login";
    throw new Error("Session expirée");
  }

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.error || data.message || `Erreur ${res.status}`);
  }

  return data;
}
