(() => {
    "use strict";

    const form = document.getElementById("form-agente");
    const textarea = document.getElementById("pregunta");
    if (!form || !textarea) {
        return;
    }

    const counter = document.getElementById("char-count");
    const status = document.getElementById("agente-status");
    const submit = form.querySelector('button[type="submit"]');
    const submitLabel = submit ? submit.querySelector("span") : null;

    const updateCounter = () => {
        const length = textarea.value.length;
        counter.textContent = `${length} / 1000`;
        counter.classList.toggle("is-limit", length >= 1000);
    };

    textarea.addEventListener("input", updateCounter);
    updateCounter();

    document.querySelectorAll("[data-pregunta]").forEach((button) => {
        button.addEventListener("click", () => {
            textarea.value = button.dataset.pregunta || "";
            updateCounter();
            textarea.focus();
            textarea.setSelectionRange(
                textarea.value.length,
                textarea.value.length
            );
        });
    });

    textarea.addEventListener("keydown", (event) => {
        if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
            event.preventDefault();
            form.requestSubmit();
        }
    });

    form.addEventListener("submit", () => {
        if (!textarea.value.trim()) {
            return;
        }
        if (submit) {
            submit.disabled = true;
        }
        if (submitLabel) {
            submitLabel.textContent = "Consultando…";
        }
        if (status) {
            status.hidden = false;
        }
    });

    const copy = document.getElementById("copy-answer");
    const answer = document.getElementById("answer-body");
    if (copy && answer) {
        copy.addEventListener("click", async () => {
            const label = copy.querySelector("span");
            try {
                await navigator.clipboard.writeText(answer.innerText);
                if (label) {
                    label.textContent = "Copiado";
                }
                window.setTimeout(() => {
                    if (label) {
                        label.textContent = "Copiar";
                    }
                }, 1800);
            } catch (error) {
                copy.blur();
            }
        });
    }
})();
