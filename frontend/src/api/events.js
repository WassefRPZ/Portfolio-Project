import { apiRequest } from "./client";

export async function getEvents() {
  return apiRequest("/events");
}
