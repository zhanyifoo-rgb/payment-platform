import {
    show,
    isValidEmail,
    isValidPhone
} from "../ui/validation.js";

import { register } from "../api/auth.js";


export async function handleRegistration() {

    const usernameInput =
        document.getElementById("re-username");
    const firstNameInput =
        document.getElementById("re-firstname");
    const lastNameInput =
        document.getElementById("re-lastname");
    const emailInput =
        document.getElementById("re-email");
    const phoneInput =
        document.getElementById("re-phone");
    const passwordInput =
        document.getElementById("re-pass");

    const username =
        usernameInput.value.trim();
    const first_name =
        firstNameInput.value.trim();
    const last_name =
        lastNameInput.value.trim();
    const email =
        emailInput.value.trim();
    const phone =
        phoneInput.value.trim();
    const password =
        passwordInput.value;

    let valid = true;
    let firstInvalidInput = null;

    // Username
    const usernameValid =
        username.length > 0;

    if (!show(
        usernameInput,
        "re-username-err",
        usernameValid
    )) {
        valid = false;
        firstInvalidInput =
            firstInvalidInput || usernameInput;
    }

    // First name
    const firstNameValid =
        first_name.length > 0;

    if (!show(
        firstNameInput,
        "re-firstname-err",
        firstNameValid
    )) {
        valid = false;
        firstInvalidInput =
            firstInvalidInput || firstNameInput;
    }

    // First name
    const lastNameValid =
        last_name.length > 0;

    if (!show(
        lastNameInput,
        "re-lastname-err",
        lastNameValid
    )) {
        valid = false;
        firstInvalidInput =
            firstInvalidInput || lastNameInput;
    }

    // Email
    const emailValid =
        isValidEmail(email);

    if (!show(
        emailInput,
        "re-email-err",
        emailValid
    )) {
        valid = false;
        firstInvalidInput =
            firstInvalidInput || emailInput;
    }

    // Phone
    const phoneValid =
        isValidPhone(phone);

    if (!show(
        phoneInput,
        "re-phone-err",
        phoneValid
    )) {
        valid = false;
        firstInvalidInput =
            firstInvalidInput || phoneInput;
    }

    // Password
    const passwordValid =
        password.length >= 10;

    if (!show(
        passwordInput,
        "re-pass-err",
        passwordValid
    )) {
        valid = false;
        firstInvalidInput =
            firstInvalidInput || passwordInput;
    }

    // Focus the first invalid field
    if (firstInvalidInput) {
        firstInvalidInput.focus();
    }

    // Don't call the API if validation failed
    if (!valid) {
        return;
    }

    try {
        await register({
            username,
            email,
            phone,
            password,
            first_name,
            last_name
        });

        sessionStorage.setItem("registrationSuccess", "true");
        window.location.reload();

    } catch (error) {

        console.error(error);

        document
            .getElementById("re-notice")
            .setAttribute("data-shown", "true");
    }
}