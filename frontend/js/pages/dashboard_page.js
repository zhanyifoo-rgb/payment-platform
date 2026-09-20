import { getCurrentUser } from "../api/auth.js";

async function loadProfile() {
    try {
            const user = await getCurrentUser();

            document.querySelectorAll(".user-username")
                .forEach(t => t.textContent = user.username);

            document.querySelectorAll(".user-fullname")
                .forEach(t => t.textContent = `${user.firstname} ${user.lastname}`);

            document.querySelectorAll(".user-hello")
                .forEach(t => t.textContent = `Hello, ${user.firstname}`);

            document.querySelectorAll(".user-balance")
                .forEach(t => t.textContent = `RM ${user.available_balance}`);

            document.querySelectorAll(".user-initial")
                .forEach(t =>
                    t.textContent =
                        `@${user.firstname[0].toUpperCase()}.${user.lastname[0].toUpperCase()}`
                );

            document.querySelectorAll(".user-handle")
                .forEach(t =>
                    t.textContent =
                        `@${user.firstname}.${user.lastname}`
                );

            document.querySelectorAll(".user-email")
                .forEach(t => t.textContent = user.email);

            document.querySelectorAll(".user-phone")
                .forEach(t => t.textContent = user.phone);

    } catch (error) {
        console.error(error);

        sessionStorage.removeItem("access_token");
        window.location.href = "./login.html";
    }
}   

loadProfile();