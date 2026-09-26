import { createPayment, topUp } from "../api/transaction.js";

export async function handleCreatePayment(account_number, amount) {

    try {
        await createPayment(
            "payment",
            account_number,
            amount,
            "MYR"
        );

        document.getElementById("successHeading").textContent = "Sent " + fmt(state.amount) + " to " + state.name;
        document.getElementById("successTime").textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        panels.forEach(function (p) { p.classList.toggle("active", p.dataset.panel === "success"); });
        document.getElementById("stepIndicator").style.display = "none";
        actionsBar.style.display = "none";

    } catch (error) {

        console.error(error);

        // document
        //     .getElementById("si-notice")
        //     .setAttribute("data-shown", "true");

    }
}

export async function handleTopUp(account_number, amount) {

    try {
        await topUp(
            "topup",
            account_number,
            amount,
            "MYR"
        );

        document.getElementById("successHeading").textContent = "Sent " + fmt(state.amount) + " to " + state.name;
        document.getElementById("successTime").textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
        panels.forEach(function (p) { p.classList.toggle("active", p.dataset.panel === "success"); });
        document.getElementById("stepIndicator").style.display = "none";
        actionsBar.style.display = "none";

    } catch (error) {

        console.error(error);

        // document
        //     .getElementById("si-notice")
        //     .setAttribute("data-shown", "true");

    }
}
