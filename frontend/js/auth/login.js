import { show } from "../ui/validation.js";
import { login } from "../api/auth.js";
import { saveToken } from "./session.js";

export async function handleSignIn() {

    const usernameInput =
        document.getElementById("si-username");

    const passwordInput =
        document.getElementById("si-pass");

    let ok = true;
    let first = null;


    const usernameValid =
        usernameInput.value.trim().length > 0;

    if (!show(
        usernameInput,
        "si-username-err",
        usernameValid
    )) {
        ok = false;
        first = first || usernameInput;
    }


    const passwordValid =
        passwordInput.value.trim().length > 0;

    if (!show(
        passwordInput,
        "si-pass-err",
        passwordValid
    )) {
        ok = false;
        first = first || passwordInput;
    }


    if (first) {
        first.focus();
    }

    if (!ok) {
        return;
    }


    try {

        const data = await login(
            usernameInput.value.trim(),
            passwordInput.value
        );

        saveToken(data.access_token);

        window.location.href = "/dashboard.html";

    } catch (error) {

        console.error(error);

        document
            .getElementById("si-notice")
            .setAttribute("data-shown", "true");
    }
}