export function setupPasswordToggles() {

    document.querySelectorAll(".peek").forEach(function (btn) {

        btn.addEventListener("click", function () {

            const input = document.getElementById(
                btn.dataset.target
            );

            const hidden = input.type === "password";

            input.type = hidden ? "text" : "password";

            btn.textContent = hidden ? "Hide" : "Show";

            btn.setAttribute(
                "aria-label",
                hidden ? "Hide password" : "Show password"
            );

            input.focus();
        });

    });
}