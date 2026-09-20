import { API_URL } from "../config.js";

export async function apiRequest(endpoint, options = {}) {

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers
        }
    });
    
    const data = await response.json();
    console.log("API error:", data);
    if (!response.ok) {
        throw new Error(data.detail || "Request failed");
    }

    return data;
}