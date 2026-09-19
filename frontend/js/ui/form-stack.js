export function setupFormStack() {
    const stack = document.getElementById("panel-stack");

    const panels = [
        document.getElementById("form-signin"),
        document.getElementById("form-register")
    ];

    /*
    * Measure a panel as if all errors were visible.
    * This does NOT affect the actual form.
    */
    function measurePanel(panel) {
        const clone = panel.cloneNode(true);

        clone.hidden = false;
        clone.style.position = "absolute";
        clone.style.visibility = "hidden";
        clone.style.display = "block";
        clone.style.width =
            panel.getBoundingClientRect().width + "px";
        clone.style.height = "auto";
        clone.style.left = "-10000px";
        clone.style.top = "0";

        clone.querySelectorAll(".error").forEach(function (error) {
            error.style.display = "block";
        });

        document.body.appendChild(clone);

        const height = clone.scrollHeight;

        clone.remove();

        return height;
    }

    /*
    * Set the stack to the height of the tallest form.
    */
    function setStackHeight() {
        let maxHeight = 0;

        panels.forEach(function (panel) {
            const height = measurePanel(panel);

            if (height > maxHeight) {
                maxHeight = height;
            }
        });

        stack.style.height = maxHeight + "px";
    }

    /*
    * Wait until everything is rendered before measuring.
    */
    window.addEventListener("load", setStackHeight);

    /*
    * Recalculate if the screen width changes.
    */
    window.addEventListener("resize", setStackHeight);

    setStackHeight();
}