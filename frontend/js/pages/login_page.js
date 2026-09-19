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