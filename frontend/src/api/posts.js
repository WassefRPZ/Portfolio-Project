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
