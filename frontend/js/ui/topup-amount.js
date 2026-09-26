import { refreshNextStateTopup, goToTopup } from "./goto.js";

export function setupTopupAmount(state, elements) {

    var amountInput = document.getElementById("amountInput");
    amountInput.addEventListener("input", function () {
        var digits = amountInput.value.replace(/[^\d.]/g, "");
        amountInput.value = digits;
        state.amount = parseFloat(digits) || 0;
        refreshNextStateTopup(elements.btnNext, state);
    });

    document.querySelectorAll(".amt-chip").forEach(function (chip) {
        chip.addEventListener("click", function () {
            amountInput.value = chip.dataset.amt + ".00";
            state.amount = parseFloat(chip.dataset.amt);
            refreshNextStateTopup(elements.btnNext, state);
        });
    });

    document.querySelectorAll("[data-goto]").forEach(function (el) {

        el.addEventListener("click", function () {
            goToTopup(parseInt(el.dataset.goto, 10), state, elements);
        });

    });

}