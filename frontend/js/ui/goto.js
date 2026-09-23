export function goTo(step, state, elements) {

    const {
        panels,
        stepEls,
        actionsBar,
        btnNext,
        btnBack
    } = elements;

    // Leaving step 1
    if (state.step === 1 && step !== 1) {
        document.getElementById("recipientSearch").value = "";
        state.accountNumber = "";
    }
    // Leaving step 2
    if (state.step === 2 && step !== 2) {
        document.getElementById("amountInput").value = "";
        state.amount = 0;
    }

    state.step = step;

    panels.forEach(function (p) {
        p.classList.toggle("active", p.dataset.panel === String(step));
    });

    stepEls.forEach(function (s) {
        var n = parseInt(s.dataset.step, 10);
        s.classList.toggle("active", n === step);
        s.classList.toggle("done", n < step);
    });

    btnBack.style.display = step > 1 ? "inline-block" : "none";
    actionsBar.style.display = "flex";

    if (step === 1) {
        btnNext.textContent = "Continue";
        refreshNextState(btnNext, state);
    } else if (step === 2) {
        btnNext.textContent = "Review";
        refreshNextState(btnNext, state);
    } else if (step === 3) {
        document.getElementById("reviewName").textContent = state.name;
        document.getElementById("reviewDetail").textContent = state.detail;
        document.getElementById("reviewNote").textContent = state.note || "—";
        document.getElementById("reviewAmount").textContent = fmt(state.amount);
        document.getElementById("reviewTotal").textContent = fmt(state.amount);
        btnNext.textContent = "Send RM " + state.amount.toFixed(2);
        btnNext.disabled = false;
    }
}

export function refreshNextState(btnNext, state) {
    if (state.step === 1) {
        btnNext.disabled = !/^\d{12}$/.test(state.accountNumber);
    }
    else if (state.step === 2) {
        btnNext.disabled = !(state.amount > 0 && state.amount <= state.balance);
    }
}

export function fmt(n) {
    return "RM " + n.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

export function initials(name) {
    return name.split(" ").map(function (w) { return w[0]; }).join("").slice(0, 2).toUpperCase();
}

