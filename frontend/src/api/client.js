/**
 * Client API centralisé pour communiquer avec le backend.
 * 
 * Responsabilités:
 * - Ajouter automatiquement le header Authorization avec le token JWT
 * - Gérer les réponses 401 (token expiré/invalide) et rediriger vers login
 * - Parser les réponses JSON et gérer les erreurs
 * - Supporter les uploads multipart (FormData) et les requêtes JSON
 */

const API = "/api/v1";  /** Prefix de base pour toutes les routes */

/**
 * Effectue une requête HTTP au backend avec support du JWT.
 * 
 * @param {string} endpoint - Route relative (ex: /events, /users/me)
 * @param {object} options - Options fetch (method, body, headers, token...)
 * @param {string} options.token - Token JWT à transmettre en Authorization
 * @returns {Promise<object>} Données JSON de la réponse
 * @throws {Error} Si la réponse n'est pas ok ou en cas d'erreur réseau
 */
export async function apiRequest(endpoint, { token, ...options } = {}) {
  const headers = { ...options.headers };  /**  Copie les en-têtes fournis */

  /** Si un token est fourni, l'ajoute en Authorization */
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;  /** Format: Bearer <token> */
  }

  /** Pour les requêtes JSON (non FormData), définit Content-Type si absent */
  if (options.body && !(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";  /** Signale du JSON au serveur */
  }

  /** Effectue la requête */
  const res = await fetch(`${API}${endpoint}`, { ...options, headers });

  /** Token expiré ou invalide → déconnexion automatique */
  if (res.status === 401) {
    localStorage.removeItem("token");  /** Nettoie le token expiré */
    window.location.href = "/login";  /** Redirige vers la page de connexion */
    throw new Error("Session expirée");  /** Signale l'erreur */
  }

  /** Parse la réponse en JSON */
  const data = await res.json();

  /** Si la réponse n'est pas ok (status >= 400), lance une erreur */
  if (!res.ok) {
    throw new Error(data.error || data.message || `Erreur ${res.status}`);
  }

  return data;  /** Retourne les données de succès */
}
