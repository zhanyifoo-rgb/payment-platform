export function saveToken(token) {
    sessionStorage.setItem("access_token", token);
}

export function getToken() {
    return sessionStorage.getItem("access_token");
}

export function removeToken() {
    sessionStorage.removeItem("access_token");
}

export function isLoggedIn() {
    return Boolean(getToken());
}