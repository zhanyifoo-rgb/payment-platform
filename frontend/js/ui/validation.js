export function show(input, errId, ok) {

    const error = document.getElementById(errId);

    error.setAttribute(
        "data-shown",
        ok ? "false" : "true"
    );

    input.setAttribute(
        "aria-invalid",
        ok ? "false" : "true"
    );

    input.setAttribute(
        "aria-describedby",
        errId
    );

    return ok;
}


export function isValidEmail(value) {

    const emailRe =
        /^[^@\s]+@[^@\s.]+\.[^@\s]+$/;

    return emailRe.test(value);
}


export function isValidPhone(value) {

    return value.replace(/\D/g, "").length >= 8;
}