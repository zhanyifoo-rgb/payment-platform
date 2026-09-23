import { refreshNextState } from "./goto.js";

export function setupStep2Amount(state, elements) {
    var amountInput = document.getElementById("amountInput");
    amountInput.addEventListener("input", function () {
        var digits = amountInput.value.replace(/[^\d.]/g, "");
        amountInput.value = digits;
        state.amount = parseFloat(digits) || 0;
        refreshNextState(elements.btnNext, state);
    });

    document.querySelectorAll(".amt-chip").forEach(function (chip) {
        chip.addEventListener("click", function () {
            amountInput.value = chip.dataset.amt + ".00";
            state.amount = parseFloat(chip.dataset.amt);
            refreshNextState(elements.btnNext, state);
        });
    });

    document.getElementById("noteInput").addEventListener("input", function (e) {
        state.note = e.target.value;
    });

    document.querySelectorAll("[data-goto]").forEach(function (el) {

        el.addEventListener("click", function () {
            goTo(parseInt(el.dataset.goto, 10), state, elements);
        });

    });

}