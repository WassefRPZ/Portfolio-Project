const API = "/api/v1";

export async function loginUser(email, password) {
  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Erreur de connexion");
  return data;
}

export async function registerUser(username, email, password, city) {
  const res = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password, city }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Erreur lors de l'inscription");
  return data;
}
