document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("chat-form");
    if (!formulario) {
        return;
    }

    const aviso = document.getElementById("aviso-procesando");
    const boton = formulario.querySelector('button[type="submit"]');
    const campo = document.getElementById("consulta");
    const hilo = document.getElementById("chat-thread");
    let enviando = false;

    const ajustarAltura = () => {
        if (!campo) {
            return;
        }
        campo.style.height = "auto";
        campo.style.height = `${Math.min(campo.scrollHeight, 120)}px`;
    };

    const irAlFinal = () => {
        if (hilo) {
            hilo.scrollTop = hilo.scrollHeight;
        }
    };

    if (campo) {
        campo.addEventListener("input", ajustarAltura);
        ajustarAltura();
        if (campo.value) {
            campo.focus();
            campo.setSelectionRange(campo.value.length, campo.value.length);
        }
    }

    document.querySelectorAll("[data-sugerencia]").forEach((chip) => {
        chip.addEventListener("click", () => {
            if (!campo) {
                return;
            }
            campo.value = chip.dataset.sugerencia || "";
            ajustarAltura();
            campo.focus();
            campo.setSelectionRange(campo.value.length, campo.value.length);
        });
    });

    if (campo) {
        campo.addEventListener("keydown", (evento) => {
            if (
                evento.key === "Enter" &&
                !evento.shiftKey &&
                !evento.isComposing
            ) {
                evento.preventDefault();
                formulario.requestSubmit();
            }
        });
    }

    const agregarEspera = (texto) => {
        if (!hilo) {
            return;
        }
        const vacio = hilo.querySelector(".chat-empty");
        if (vacio) {
            vacio.remove();
        }

        const turno = document.createElement("article");
        turno.className = "chat-turn";

        const pregunta = document.createElement("p");
        pregunta.className = "msg-user";
        const etiqueta = document.createElement("span");
        etiqueta.className = "sr-only";
        etiqueta.textContent = "Vos: ";
        pregunta.append(etiqueta, document.createTextNode(texto));

        const respuesta = document.createElement("div");
        respuesta.className = "msg-ai";

        const avatar = document.createElement("span");
        avatar.className = "msg-avatar";
        avatar.setAttribute("aria-hidden", "true");
        avatar.innerHTML =
            '<svg class="icon"><use href="#i-sparkles"></use></svg>';

        const cuerpo = document.createElement("div");
        cuerpo.className = "msg-body";

        const escribiendo = document.createElement("div");
        escribiendo.className = "typing";
        escribiendo.setAttribute("aria-label", "La IA está escribiendo");
        for (let i = 0; i < 3; i += 1) {
            escribiendo.append(document.createElement("span"));
        }

        cuerpo.append(escribiendo);
        respuesta.append(avatar, cuerpo);
        turno.append(pregunta, respuesta);
        hilo.append(turno);
        irAlFinal();
    };

    if (hilo && hilo.querySelector(".chat-turn")) {
        irAlFinal();
    }

    formulario.addEventListener("submit", (evento) => {
        if (enviando) {
            evento.preventDefault();
            return;
        }

        const texto = campo ? campo.value.trim() : "";
        if (!texto) {
            evento.preventDefault();
            if (campo) {
                campo.focus();
            }
            return;
        }

        enviando = true;
        aviso.hidden = false;
        boton.disabled = true;
        boton.textContent = "Enviando…";
        agregarEspera(texto);
    });
});
