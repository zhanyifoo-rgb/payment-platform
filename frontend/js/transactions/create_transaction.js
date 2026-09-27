import { createPayment, topUp, waitForTransaction } from "../api/transaction.js";
import { goTo, goToTopup, fmt } from "../ui/goto.js";

function updateTransactionStatus(result, state) {
    if (result.status === "succeeded") {
        document.querySelector(".cross").classList.add("hide");
        document.querySelector(".check").classList.remove("hide");

        document.getElementById("statusHeading").textContent = result.transaction_type == "topup" ?
            "Successfully top up " + fmt(state.amount) : "Sent " + fmt(state.amount) + " to ";
    } else {
        document.querySelector(".check").classList.add("hide");
        document.querySelector(".cross").classList.remove("hide");

        document.getElementById("statusHeading").textContent =
            "Transaction failed";
    }

    document.getElementById("statusTime").textContent =
        new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        });
}

export async function handleCreatePayment(state, elements) {
    const overlay = document.getElementById("overlay");

    overlay.classList.remove("hidden");

    try {
        const idempotencyKey = crypto.randomUUID();
        const accountNumber = state.accountNumber;
        const amount = state.amount;

        const transaction = await createPayment(
            {
                transaction_type: "payment",
                recipient_account_number: accountNumber,
                amount: amount,
                currency: "MYR"
            },
            idempotencyKey
        );

        const result = await waitForTransaction(
            transaction.transaction_id
        );

        updateTransactionStatus(result, state);
        goTo("status", state, elements);

    } catch (error) {
        console.error(error);

    } finally {
        overlay.classList.add("hidden");
    }
}

export async function handleTopUp(state, elements) {
    const overlay = document.getElementById("overlay");

    overlay.classList.remove("hidden");

    try {
        const idempotencyKey = crypto.randomUUID();
        const accountNumber = state.accountNumber;
        const amount = state.amount;

        const transaction = await topUp(
            {
                transaction_type: "topup",
                recipient_account_number: accountNumber,
                amount: amount,
                currency: "MYR"
            },
            idempotencyKey
        );

        const result = await waitForTransaction(
            transaction.transaction_id
        );

        updateTransactionStatus(result, state);
        goToTopup("status", state, elements);

    } catch (error) {
        console.error(error);

    } finally {
        overlay.classList.add("hidden");
    }
}