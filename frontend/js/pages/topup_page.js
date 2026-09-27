import { getCurrentUser } from "../api/auth.js";
import { goTo } from "../ui/goto.js";

import { setupButtonsTopup } from "../ui/setup-buttons.js";
import { setupTopupAmount } from "../ui/topup-amount.js";
import { handleTopUp } from "../transactions/create_transaction.js";

var state = {
    step: 1,
    name: "",
    detail: "",
    amount: 0,
    accountNumber: "",
    balance: 0
};

var elements = {
    panels: document.querySelectorAll(".step-panel"),
    stepEls: document.querySelectorAll(".steps .step"),
    actionsBar: document.getElementById("actionsBar"),
    stepIndicator: document.getElementById("stepIndicator"),
    btnNext: document.getElementById("btnNext"),
    btnBack: document.getElementById("btnBack")
};

async function initTopUpPage() {
    const token = sessionStorage.getItem("access_token");

    if (!token) {
        window.location.replace("./index.html");
        return;
    }

    try {
        const user = await getCurrentUser();

        state.balance = Number(user.available_balance);
        state.accountNumber = String(user.account_number);

        // Populate dashboard
        document.querySelectorAll(".user-username")
            .forEach(t => t.textContent = user.username);

        document.querySelectorAll(".user-fullname")
            .forEach(t => t.textContent = `${user.firstname} ${user.lastname}`);

        document.querySelectorAll(".user-balance")
            .forEach(t => t.textContent = `RM ${state.balance.toFixed(2)}`);

        document.querySelectorAll(".user-initial")
            .forEach(t =>
                t.textContent =
                `${user.firstname[0].toUpperCase()}${user.lastname[0].toUpperCase()}`
            );

        document.querySelectorAll(".user-handle")
            .forEach(t =>
                t.textContent =
                `@${user.firstname.toLowerCase()}.${user.lastname.toLowerCase()}`
            );

        document.querySelectorAll(".user-email")
            .forEach(t => t.textContent = user.email);

        document.querySelectorAll(".user-phone")
            .forEach(t => t.textContent = user.phone);

        document.body.classList.add("auth-checked");

        setupTopupAmount(state, elements);

        setupButtonsTopup(state, elements);

    } catch (error) {
        sessionStorage.removeItem("access_token");
        window.location.replace("./index.html");
    }
}

initTopUpPage();