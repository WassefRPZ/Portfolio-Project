import { apiRequest } from "./client";

export async function getFriends(token) {
  return apiRequest("/friends", { token });
}

export async function getPendingRequests(token) {
  return apiRequest("/friends/pending", { token });
}

export async function getSentRequests(token) {
  return apiRequest("/friends/sent", { token });
}

export async function sendFriendRequest(token, userId) {
  return apiRequest(`/friends/request/${userId}`, { token, method: "POST" });
}

export async function acceptFriendRequest(token, requesterId) {
  return apiRequest(`/friends/accept/${requesterId}`, { token, method: "POST" });
}

export async function declineFriendRequest(token, requesterId) {
  return apiRequest(`/friends/reject/${requesterId}`, { token, method: "POST" });
}

export async function removeFriend(token, friendId) {
  return apiRequest(`/friends/${friendId}`, { token, method: "DELETE" });
}

export async function searchUsers(token, query) {
  return apiRequest(`/users/search?q=${encodeURIComponent(query)}`, { token });
}
