import { API_URL } from "../config.js";
import { apiRequest } from "./client.js";

export async function createPayment(userData, idempotencyKey) {

    return apiRequest("/transactions/createpayment", {
        method: "POST",
        body: JSON.stringify(userData),
        headers: {
            "Idempotency-Key": idempotencyKey
        }
    });
}

export async function topUp(userData, idempotencyKey) {

    return apiRequest("/transactions/topup", {
        method: "POST",
        body: JSON.stringify(userData),
        headers: {
            "Idempotency-Key": idempotencyKey
        }
    });
}

export async function waitForTransaction(transaction_id) {
    while (true) {

        const transaction =
            await getTransaction(transaction_id);

        if (
            transaction.status === "succeeded" ||
            transaction.status === "failed"
        ) {
            return transaction;
        }

        await new Promise(resolve =>
            setTimeout(resolve, 1000)
        );
    }
}

export async function getTransaction(transaction_id) {

    return apiRequest(`/transactions/get/${transaction_id}`, {
        method: "GET",
    });
}



