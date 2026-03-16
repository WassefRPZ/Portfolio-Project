/**
 * Fonctions API des posts : gestion du fil social et operations CRUD.
 */

import { apiRequest } from "./client";

export async function getFeed(token, { limit = 20, offset = 0 } = {}) {
  return apiRequest(`/posts?limit=${limit}&offset=${offset}`, { token });
}

export async function createPost(token, content) {
  return apiRequest("/posts", {
    token,
    method: "POST",
    body: JSON.stringify({ content, post_type: "text" }),
  });
}

export async function deletePost(token, postId) {
  return apiRequest(`/posts/${postId}`, {
    token,
    method: "DELETE",
  });
}
