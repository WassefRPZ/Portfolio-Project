/**
 * Fonctions API des evenements : CRUD, participation et commentaires.
 */

import { apiRequest } from "./client";

export async function getEvents(token, { city, date, limit = 50, offset = 0 } = {}) {
  const params = new URLSearchParams();
  if (city) params.set("city", city);
  if (date) params.set("date", date);
  params.set("limit", limit);
  params.set("offset", offset);
  return apiRequest(`/events?${params}`, { token });
}

export async function getEventDetails(token, eventId) {
  return apiRequest(`/events/${eventId}`, { token });
}

export async function createEvent(token, data) {
  const isFormData = data instanceof FormData;
  return apiRequest("/events", {
    token,
    method: "POST",
    body: isFormData ? data : JSON.stringify(data),
  });
}

export async function joinEvent(token, eventId) {
  return apiRequest(`/events/${eventId}/join`, { token, method: "POST" });
}

export async function leaveEvent(token, eventId) {
  return apiRequest(`/events/${eventId}/leave`, { token, method: "POST" });
}

export async function deleteEvent(token, eventId) {
  return apiRequest(`/events/${eventId}`, { token, method: "DELETE" });
}
