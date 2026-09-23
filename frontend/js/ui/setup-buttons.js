import { verifyRecipient } from "../auth/verify-recipient.js";
import { goTo } from "./goto.js"

export function setupButtons(state, elements) {

    elements.btnNext.addEventListener("click", function () {
        if (state.step == 1) {
            verifyRecipient(state, elements);
        } else if (state.step < 3) {
            goTo(state.step + 1, state, elements);
        } else {
            document.getElementById("successHeading").textContent = "Sent " + fmt(state.amount) + " to " + state.name;
            document.getElementById("successTime").textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
            panels.forEach(function (p) { p.classList.toggle("active", p.dataset.panel === "success"); });
            document.getElementById("stepIndicator").style.display = "none";
            actionsBar.style.display = "none";
        }
    });

    btnBack.addEventListener("click", function () {
        if (state.step > 1)
            goTo(state.step - 1, state, elements);
    });

}

