document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("form-pago");
    if (!formulario) {
        return;
    }

    const total = (formulario.dataset.total || "").replace(",", ".");
    const casillas = Array.from(
        formulario.querySelectorAll('input[name="medio_pago"]')
    );

    const actualizarImportes = () => {
        const marcados = casillas.filter((casilla) => casilla.checked);

        casillas.forEach((casilla) => {
            const importe = formulario.querySelector(
                `#importe-${casilla.value}`
            );
            importe.hidden = !casilla.checked;
        });

        if (marcados.length === 1) {
            const importe = formulario.querySelector(
                `#importe-${marcados[0].value}`
            );
            importe.value = total;
        }
    };

    casillas.forEach((casilla) => {
        casilla.addEventListener("change", actualizarImportes);
    });
    actualizarImportes();
});
