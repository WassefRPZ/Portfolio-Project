import { apiRequest } from "./client";

export async function getAllGames(token) {
  return apiRequest("/games", { token });
}

export async function searchGames(token, query) {
  return apiRequest(`/games/search?q=${encodeURIComponent(query)}`, { token });
}

export async function getFavoriteGames(token) {
  return apiRequest("/users/me/favorite-games", { token });
}

export async function addFavoriteGame(token, gameId) {
  return apiRequest("/users/me/favorite-games", {
    token,
    method: "POST",
    body: JSON.stringify({ game_id: gameId }),
  });
}

export async function removeFavoriteGame(token, gameId) {
  return apiRequest(`/users/me/favorite-games/${gameId}`, {
    token,
    method: "DELETE",
  });
}
