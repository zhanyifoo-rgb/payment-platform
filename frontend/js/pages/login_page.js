import { setupTabs } from "../ui/tabs.js";
import { setupPasswordToggles } from "../ui/password-toggle.js";
import { setupFormStack } from "../ui/form-stack.js";

import { handleSignIn } from "../auth/login.js";
import { handleRegistration } from "../auth/register.js";


setupTabs();

setupPasswordToggles();

setupFormStack();


document
    .querySelector('[data-form="signin"]')
    .addEventListener("click", handleSignIn);


document
    .querySelector('[data-form="register"]')
    .addEventListener("click", handleRegistration);

const registrationSuccess = sessionStorage.getItem("registrationSuccess");

if (registrationSuccess) {
    const notice = document.getElementById("si-notice");

    notice.dataset.alertType = "success";
    notice.textContent = "Registration successful.";
    notice.dataset.shown = "true";

    sessionStorage.removeItem("registrationSuccess");

}