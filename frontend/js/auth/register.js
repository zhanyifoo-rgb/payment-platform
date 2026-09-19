import {
    show,
    isValidEmail,
    isValidPhone
} from "../ui/validation.js";

import { register } from "../api/auth.js";


export async function handleRegistration() {

    const usernameInput =
        document.getElementById("re-username");

    const emailInput =
        document.getElementById("re-email");

    const phoneInput =
        document.getElementById("re-phone");

    const passwordInput =
        document.getElementById("re-pass");


    const username =
        usernameInput.value.trim();

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
        username.length > 1;

    if (!show(
        usernameInput,
        "re-username-err",
        usernameValid
    )) {
        valid = false;
        firstInvalidInput =
            firstInvalidInput || usernameInput;
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

        await register(
            username,
            email,
            phone,
            password
        );

        document
            .getElementById("re-notice")
            .setAttribute("data-shown", "true");

    } catch (error) {

        console.error(error);

        document
            .getElementById("re-notice")
            .setAttribute("data-shown", "true");
    }
}