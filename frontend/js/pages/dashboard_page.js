import { getCurrentUser } from "../api/auth.js";
import { handleSignOut } from "../auth/logout.js";

async function initDashboard() {
    const token = sessionStorage.getItem("access_token");

    if (!token) {
        window.location.replace("./login.html");
        return;
    }

    try {
        const user = await getCurrentUser();

        // Populate dashboard
        document.querySelectorAll(".user-username")
            .forEach(t => t.textContent = user.username);

        document.querySelectorAll(".user-fullname")
            .forEach(t => t.textContent = `${user.firstname} ${user.lastname}`);

        document.querySelectorAll(".user-hello")
            .forEach(t => t.textContent = `Hello, ${user.firstname}`);

        document.querySelectorAll(".user-balance")
            .forEach(t => t.textContent = `RM ${user.available_balance.toFixed(2)}`);
        
        document.querySelectorAll(".user-accountNo")
            .forEach(t => t.textContent = `Tunai account ${user.account_number.slice(0,3)} ${user.account_number.slice(3,6)} ${user.account_number.slice(6,9)} ${user.account_number.slice(9,12)}`);

        document.querySelectorAll(".user-initial")
            .forEach(t =>
                t.textContent =
                    `${user.firstname[0].toUpperCase()}${user.lastname[0].toUpperCase()}`
            );

        document.querySelectorAll(".user-handle")
            .forEach(t =>
                t.textContent =
                    `@${user.firstname.toLowerCase()}.${user.lastname.toLowerCase()}`
            );

        document.querySelectorAll(".user-email")
            .forEach(t => t.textContent = user.email);

        document.querySelectorAll(".user-phone")
            .forEach(t => t.textContent = user.phone);

        document.body.classList.add("auth-checked");

    } catch (error) {
        sessionStorage.removeItem("access_token");
        window.location.replace("./login.html");
    }
}

document
    .querySelector('[aria-label="Log out"]')
    .addEventListener("click", handleSignOut);

initDashboard();