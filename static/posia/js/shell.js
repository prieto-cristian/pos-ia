(() => {
    "use strict";

    const sidebar = document.getElementById("sidebar");
    if (!sidebar) {
        return;
    }

    const body = document.body;
    const toggle = document.querySelector("[data-sidebar-toggle]");
    const scrim = document.querySelector(".sidebar-scrim");
    const closers = document.querySelectorAll("[data-sidebar-close]");
    const mobile = window.matchMedia("(max-width: 980px)");

    const isOpen = () => body.classList.contains("is-sidebar-open");

    const open = () => {
        body.classList.add("is-sidebar-open");
        if (toggle) {
            toggle.setAttribute("aria-expanded", "true");
        }
        if (scrim) {
            scrim.hidden = false;
        }
        const closeButton = sidebar.querySelector(".sidebar-close");
        if (closeButton) {
            closeButton.focus();
        }
    };

    const close = (restoreFocus = true) => {
        body.classList.remove("is-sidebar-open");
        if (toggle) {
            toggle.setAttribute("aria-expanded", "false");
        }
        if (scrim) {
            scrim.hidden = true;
        }
        if (restoreFocus && toggle && mobile.matches) {
            toggle.focus();
        }
    };

    if (toggle) {
        toggle.addEventListener("click", () => {
            if (isOpen()) {
                close();
            } else {
                open();
            }
        });
    }

    closers.forEach((button) => {
        button.addEventListener("click", () => close());
    });

    if (scrim) {
        scrim.addEventListener("click", () => close());
    }

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && isOpen()) {
            close();
        }
    });

    sidebar.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", () => {
            if (mobile.matches) {
                close(false);
            }
        });
    });

    mobile.addEventListener("change", (event) => {
        if (!event.matches && isOpen()) {
            close(false);
        }
    });
})();
