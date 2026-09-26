import { getCurrentUser } from "../api/auth.js";
import { goTo } from "../ui/goto.js";

import { setupStep1Recipient } from "../ui/step-1-recipient.js";
import { setupStep2Amount } from "../ui/step-2-amount.js";
import { setupButtons } from "../ui/setup-buttons.js";


var state = {
    step: 1,
    name: "",
    detail: "",
    amount: 0,
    note: "",
    accountNumber: "",
    balance: 0
};

var elements = {
    panels: document.querySelectorAll(".step-panel"),
    stepEls: document.querySelectorAll(".steps .step"),
    actionsBar: document.getElementById("actionsBar"),
    btnNext: document.getElementById("btnNext"),
    btnBack: document.getElementById("btnBack")
};

async function initCreatePaymentPage() {
    const token = sessionStorage.getItem("access_token");

    if (!token) {
        window.location.replace("./login.html");
        return;
    }

    try {
        const user = await getCurrentUser();

        state.balance = Number(user.available_balance);

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

        setupStep1Recipient(state, elements);

        setupStep2Amount(state, elements);

        setupButtons(state, elements);

        goTo(1, state, elements);

    } catch (error) {
        sessionStorage.removeItem("access_token");
        window.location.replace("./login.html");
    }
}

initCreatePaymentPage();



