import { API_URL } from "../config.js";

export async function login(username, password) {

  const response = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: new URLSearchParams({
      username,
      password
    })
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Login failed");
  }

  return data;
}

export async function register(userData) {

  return apiRequest("/register", {
    method: "POST",
    body: JSON.stringify(userData)
  });
}
