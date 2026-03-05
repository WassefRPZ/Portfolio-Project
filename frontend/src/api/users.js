import { apiRequest } from "./client";

export async function getMe(token) {
  return apiRequest("/users/me", { token });
}
