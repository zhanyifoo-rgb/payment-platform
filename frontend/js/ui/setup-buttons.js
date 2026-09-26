import { verifyRecipient } from "../auth/verify-recipient.js";
import { goTo, goToTopup } from "./goto.js"
import { handleCreatePayment, handleTopUp } from "../transactions/create_transaction.js";

export function setupButtons(state, elements) {

    elements.btnNext.addEventListener("click", function () {
        if (state.step == 1) {
            verifyRecipient(state, elements);
        } else if (state.step < 3) {
            goTo(state.step + 1, state, elements);
        } else {
            handleCreatePayment(state.accountNumber, state.amount)
        }
    });

    btnBack.addEventListener("click", function () {
        if (state.step > 1)
            goTo(state.step - 1, state, elements);
    });

}

export function setupButtonsTopup(state, elements) {

    elements.btnNext.addEventListener("click", function () {
        if (state.step == 1) {
            goToTopup(state.step + 1, state, elements);
        } else {
            handleTopUp(state.accountNumber, state.amount)
        }
    });

    btnBack.addEventListener("click", function () {
        if (state.step > 1)
            goToTopup(state.step - 1, state, elements);
    });

}
