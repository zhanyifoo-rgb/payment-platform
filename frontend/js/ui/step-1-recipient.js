import { goTo, refreshNextState, initials } from "./goto.js"

export function setupStep1Recipient(state, elements) {
    function selectRecipient(name, detail) {
        state.name = name;
        state.detail = detail;
        document.getElementById("pillAvatar").textContent = initials(name);
        document.getElementById("pillName").textContent = name;
        document.getElementById("pillDetail").textContent = detail;

        document.querySelectorAll(".recent-chip").forEach(function (c) {
            c.setAttribute("aria-pressed", c.dataset.name === name ? "true" : "false");
        });
        goTo(2, state, elements);
    }

    document.querySelectorAll(".recent-chip").forEach(function (el) {
        el.addEventListener("click", function () {
            selectRecipient(el.dataset.name, el.dataset.detail);
        });
    });

    var accountNumberInput = document.getElementById("recipientSearch");
    accountNumberInput.addEventListener("input", function () {
        var digits = accountNumberInput.value.replace(/[^\d]/g, "");
        accountNumberInput.value = digits;
        state.accountNumber = digits;
        refreshNextState(elements.btnNext, state);

        const errorElement =
            document.getElementById("recipientSearch-err");

        errorElement.setAttribute("data-shown", "false");
    });

}