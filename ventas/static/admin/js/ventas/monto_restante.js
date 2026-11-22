document.addEventListener("DOMContentLoaded", () => {
    if (!window.location.pathname.endsWith("/add/")) {
        return;
    }

    const selector = document.getElementById("id_venta");
    if (!selector) {
        return;
    }

    const monto = document.createElement("p");
    monto.id = "monto-restante";
    monto.className = "help";
    monto.hidden = true;
    const wrapper = selector.closest(".related-widget-wrapper") || selector;
    wrapper.insertAdjacentElement("afterend", monto);

    const actualizarMonto = () => {
        const opcion = selector.selectedOptions[0];
        const restante = opcion?.dataset.montoRestante;
        monto.hidden = !restante;
        monto.textContent = restante ? `Monto restante: $${restante}` : "";
    };

    selector.addEventListener("change", actualizarMonto);
    actualizarMonto();
});
