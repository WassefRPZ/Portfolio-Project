/**
 * Garde de route React Router : redirige les utilisateurs non authentifiés.
 * 
 * Usage:
 * <Route path="/events" element={
 *   <ProtectedRoute>
 *     <EventsPage />
 *   </ProtectedRoute>
 * } />
 * 
 * Comportement:
 * - Si isAuthenticated est true: affiche normalement le composant enfant
 * - Sinon: redirige silencieusement vers /login avec <Navigate>
 */

import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";  /** Hook pour accéder à l'authentification */

export default function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();  /** Vérifie si l'utilisateur est connecté */

  /** Si l'utilisateur n'est pas authentifié, le redirige vers la page de connexion */
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;  /** replace: supprime l'historique de navigation */
  }
  
  /** Sinon, affiche normalement le composant enfant */
  return children;
}
