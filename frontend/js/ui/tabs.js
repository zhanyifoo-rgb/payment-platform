export function setupTabs() {

    const tabs = [
        {
            tab: document.getElementById("tab-signin"),
            panel: document.getElementById("form-signin")
        },
        {
            tab: document.getElementById("tab-register"),
            panel: document.getElementById("form-register")
        }
    ];

    /*
    * Toggle between Sign in / Create account.
    */
    function activate(index) {

        tabs.forEach(function (item, i) {

            const active = i === index;

            item.tab.setAttribute(
                "aria-selected",
                String(active)
            );

            item.panel.hidden = !active;

            if (active) {
                item.panel.removeAttribute("inert");
            } else {
                item.panel.setAttribute("inert", "");
            }
        });
    }

    tabs.forEach(function (item, index) {

        item.tab.addEventListener("click", function () {
            activate(index);
        });

    });

    // Start with Sign In
    activate(0);
}