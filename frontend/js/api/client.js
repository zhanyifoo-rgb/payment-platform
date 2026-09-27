import { API_URL } from "../config.js";

export async function apiRequest(endpoint, options = {}) {
    const token = sessionStorage.getItem("access_token");

    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers
    });

    const data = await response.json();

    if (!response.ok) {
        console.log("API response:", data);

        const error = new Error(data.detail || "Request failed");
        error.status = response.status;
        throw error;
    }

    return data;
}