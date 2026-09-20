import { API_URL } from "../config.js";
import { apiRequest } from "./client.js";

export async function login(username, password) {

  const response = await fetch(`${API_URL}/auth/login`, {
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

  return apiRequest("/auth/register", {
    method: "POST",
    body: JSON.stringify(userData)
  });
}

export async function getCurrentUser() {
    const token = localStorage.getItem("access_token");

    const response = await fetch(
        `${API_URL}/api/v1/users/me`,
        {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "Failed to load user");
    }

    return data;
}
