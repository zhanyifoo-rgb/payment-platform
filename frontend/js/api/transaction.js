import { API_URL } from "../config.js";
import { apiRequest } from "./client.js";

export async function createPayment(userData) {

    return apiRequest("/transactions/createpayment", {
        method: "POST",
        body: JSON.stringify(userData)
    });
}

export async function topUp(userData) {

    return apiRequest("/transactions/topup", {
        method: "POST",
        body: JSON.stringify(userData)
    });
}