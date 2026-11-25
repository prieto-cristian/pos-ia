document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.querySelector("form");
    if (!formulario) {
        return;
    }

    const aviso = document.getElementById("aviso-procesando");
    const boton = formulario.querySelector('button[type="submit"]');
    let enviando = false;

    formulario.addEventListener("submit", (evento) => {
        if (enviando) {
            evento.preventDefault();
            return;
        }

        enviando = true;
        aviso.hidden = false;
        boton.disabled = true;
    });
});
