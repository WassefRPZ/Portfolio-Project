/**
 * Fonctions API utilisateur : profil, recherche et jeux favoris.
 */

import { apiRequest } from "./client";

export async function getMe(token) {
  return apiRequest("/users/me", { token });
}

export async function updateProfile(token, formData) {
  return apiRequest("/users/me", {
    token,
    method: "PUT",
    body: formData,
  });
}
