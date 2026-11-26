(() => {
    "use strict";

    const catalogNode = document.getElementById("pos-catalogo");
    if (!catalogNode) {
        return;
    }

    const catalog = JSON.parse(catalogNode.textContent);
    const byId = new Map(catalog.map((product) => [String(product.id), product]));
    const initialNode = document.getElementById("pos-initial-items");
    const initial = (() => {
        try {
            const parsed = JSON.parse(initialNode ? initialNode.textContent : "[]");
            return Array.isArray(parsed) ? parsed : [];
        } catch (error) {
            return [];
        }
    })();

    const saleNode = document.getElementById("pos-sale-id");
    const saleComplete = Boolean(
        saleNode &&
            saleNode.textContent.trim() &&
            saleNode.textContent.trim() !== "null"
    );

    const storageKey = "posia.cart.v1";
    const columnsKey = "posia.columns.v1";

    const search = document.getElementById("busqueda");
    const searchClear = document.getElementById("search-clear");
    const productGrid = document.getElementById("product-grid");
    const catalogCount = document.getElementById("catalog-count");
    const catalogEmpty = document.getElementById("catalog-empty");
    const clearFilters = document.getElementById("clear-filters");
    const cards = Array.from(document.querySelectorAll(".product-card"));
    const catTabs = Array.from(document.querySelectorAll(".cat-tab"));
    const columnButtons = Array.from(
        document.querySelectorAll(".segmented-btn")
    );

    const cartItems = document.getElementById("cart-items");
    const cartEmpty = document.getElementById("cart-empty");
    const cartCount = document.getElementById("cart-count");
    const cartTotal = document.getElementById("cart-total");
    const cartTotalMeta = document.getElementById("cart-total-meta");
    const cartClear = document.getElementById("cart-clear");
    const itemsInput = document.getElementById("items-input");
    const paymentInputs = document.getElementById("payment-inputs");
    const paymentNote = document.getElementById("payment-note");
    const methodButtons = Array.from(
        document.querySelectorAll(".pay-method")
    );
    const methodLabels = new Map(
        methodButtons.map((button) => [
            button.dataset.method,
            button.querySelector(".pm-label").textContent.trim(),
        ])
    );
    const form = document.getElementById("form-pago");
    const payBtn = document.getElementById("pay-btn");
    const saleSuccess = document.getElementById("sale-success");
    const cartLive = document.getElementById("cart-live");
    const newSale = document.getElementById("new-sale");
    const lineTemplate = document.getElementById("cart-line-template");
    const cartRail = document.getElementById("carrito");
    const mobileCartBar = document.getElementById("mobile-cart-bar");
    const mobileCartCount = document.getElementById("mobile-cart-count");
    const mobileCartTotal = document.getElementById("mobile-cart-total");
    const compactMedia = window.matchMedia("(max-width: 980px)");

    const state = {
        items: new Map(),
        methods: new Set(),
        amounts: new Map(),
    };

    let activeCategory = "todos";
    let query = "";
    let canPay = false;
    let cartInView = false;
    let toastElement = null;
    let toastTimer = null;

    const normalize = (value) =>
        String(value || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .trim();

    cards.forEach((card) => {
        card.dataset.search = normalize(
            `${card.dataset.name} ${card.dataset.code}`
        );
    });

    const emptyTitle = catalogEmpty.querySelector(".empty-title");
    const emptyTitleDefault = emptyTitle.textContent;

    const ars = new Intl.NumberFormat("es-AR", {
        maximumFractionDigits: 0,
    });

    const money = (cents) => {
        const absolute = Math.abs(Math.round(cents));
        const units = Math.floor(absolute / 100);
        const remainder = absolute % 100;
        const sign = cents < 0 ? "-" : "";
        return `${sign}$ ${ars.format(units)}${
            remainder ? `,${String(remainder).padStart(2, "0")}` : ""
        }`;
    };

    const unitPrice = (product) =>
        Math.round(Number(product.precio) * 100);

    const totalCents = () => {
        let total = 0;
        state.items.forEach((quantity, id) => {
            const product = byId.get(id);
            if (product) {
                total += unitPrice(product) * quantity;
            }
        });
        return total;
    };

    const unitCount = () => {
        let total = 0;
        state.items.forEach((quantity) => {
            total += quantity;
        });
        return total;
    };

    const itemsPayload = () =>
        Array.from(state.items.entries()).map(([id, quantity]) => ({
            producto_id: Number(id),
            cantidad: quantity,
        }));

    const updateMobileBar = () => {
        if (!mobileCartBar) {
            return;
        }
        const successVisible = Boolean(
            saleSuccess && !saleSuccess.hidden
        );
        mobileCartBar.hidden = !(
            compactMedia.matches &&
            state.items.size > 0 &&
            !cartInView &&
            !successVisible
        );
    };

    const parseAmount = (raw) => {
        if (!raw) {
            return 0;
        }
        let value = String(raw).replace(/[^\d.,-]/g, "").trim();
        if (!value) {
            return 0;
        }
        if (value.includes(",") && value.includes(".")) {
            value = value.replace(/\./g, "").replace(",", ".");
        } else if (value.includes(",")) {
            value = value.replace(",", ".");
        } else if (/^-?\d{1,3}(\.\d{3})+$/.test(value)) {
            value = value.replace(/\./g, "");
        }
        const number = Number(value);
        if (!Number.isFinite(number) || number < 0) {
            return 0;
        }
        return Math.round(number * 100);
    };

    const amountFor = (method) => {
        if (state.methods.size === 1) {
            return totalCents();
        }
        return parseAmount(state.amounts.get(method) || "");
    };

    const dismissToast = () => {
        if (toastTimer) {
            window.clearTimeout(toastTimer);
            toastTimer = null;
        }
        if (toastElement) {
            toastElement.remove();
            toastElement = null;
        }
    };

    const showToast = (message, action) => {
        dismissToast();
        const toast = document.createElement("div");
        toast.className = "toast";
        toast.setAttribute("role", "status");
        const text = document.createElement("span");
        text.textContent = message;
        toast.append(text);
        if (action) {
            const button = document.createElement("button");
            button.type = "button";
            button.textContent = action.label;
            button.addEventListener("click", () => {
                action.run();
                dismissToast();
            });
            toast.append(button);
        }
        document.body.append(toast);
        toastElement = toast;
        window.requestAnimationFrame(() => {
            toast.classList.add("is-visible");
        });
        toastTimer = window.setTimeout(() => {
            toast.classList.remove("is-visible");
            window.setTimeout(() => {
                toast.remove();
                if (toastElement === toast) {
                    toastElement = null;
                }
            }, 200);
        }, action ? 6000 : 3200);
    };

    const persist = () => {
        try {
            window.sessionStorage.setItem(
                storageKey,
                JSON.stringify({
                    items: Array.from(state.items.entries()).map(
                        ([id, quantity]) => ({
                            id: Number(id),
                            qty: quantity,
                        })
                    ),
                    savedAt: Date.now(),
                })
            );
        } catch (error) {
            /* El carrito sigue funcionando sin almacenamiento. */
        }
    };

    const clearPersisted = () => {
        try {
            window.sessionStorage.removeItem(storageKey);
        } catch (error) {
            /* Sin almacenamiento no hay nada que borrar. */
        }
    };

    const readPersisted = () => {
        try {
            const raw = window.sessionStorage.getItem(storageKey);
            if (!raw) {
                return null;
            }
            const parsed = JSON.parse(raw);
            return Array.isArray(parsed.items) ? parsed.items : null;
        } catch (error) {
            return null;
        }
    };

    const hydrate = () => {
        if (saleComplete) {
            clearPersisted();
            return;
        }
        const stored = readPersisted();
        const source = initial.length ? initial : stored || [];
        source.forEach((item) => {
            const id = String(item.producto_id ?? item.id ?? "");
            const quantity = Number(item.cantidad ?? item.qty ?? 0);
            const product = byId.get(id);
            if (!product || !Number.isFinite(quantity) || quantity < 1) {
                return;
            }
            const stock = Number(product.stock);
            const limit = stock > 0 ? stock : 99;
            state.items.set(id, Math.min(quantity, limit));
        });
        persist();
    };

    const updateCards = () => {
        cards.forEach((card) => {
            const id = String(card.dataset.productId);
            const quantity = state.items.get(id) || 0;
            const add = card.querySelector("[data-add]");
            const stepper = card.querySelector("[data-stepper]");
            const quantityLabel = stepper
                ? stepper.querySelector(".step-qty")
                : null;

            if (add) {
                add.hidden = quantity > 0;
            }
            if (stepper) {
                stepper.hidden = quantity === 0;
                const plus = stepper.querySelector('[data-step="1"]');
                const minus = stepper.querySelector('[data-step="-1"]');
                const stock = Number(card.dataset.stock);
                if (plus) {
                    plus.disabled = stock > 0 && quantity >= stock;
                }
                if (minus) {
                    minus.disabled = quantity <= 0;
                }
            }
            if (quantityLabel) {
                quantityLabel.textContent = String(quantity);
            }
            card.classList.toggle("is-in-cart", quantity > 0);
        });
    };

    const buildLine = (product, quantity, isNew) => {
        const fragment = lineTemplate.content.cloneNode(true);
        const line = fragment.querySelector(".cart-line");
        const id = String(product.id);
        const category = product.categoria_slug || "otros";
        const price = unitPrice(product);

        line.dataset.productoId = id;
        line.dataset.cantidad = String(quantity);

        const thumb = line.querySelector(".cart-thumb");
        thumb.dataset.cat = category;
        thumb
            .querySelector("use")
            .setAttribute("href", `#cat-${category}`);

        line.querySelector(".cart-line-name").textContent = product.nombre;

        const remove = line.querySelector(".cart-remove");
        remove.dataset.remove = id;
        remove.setAttribute(
            "aria-label",
            `Quitar ${product.nombre} del carrito`
        );

        line.querySelector(
            ".cart-line-unit"
        ).textContent = `${money(price)} c/u`;

        const quantityLabel = line.querySelector(".step-qty");
        quantityLabel.textContent = String(quantity);
        quantityLabel.dataset.qty = id;

        const stock = Number(product.stock);
        const stepButtons = line.querySelectorAll(".step-btn");
        stepButtons.forEach((button) => {
            const delta = button.dataset.step;
            button.dataset.id = id;
            button.setAttribute(
                "aria-label",
                delta === "-1"
                    ? `Quitar una unidad de ${product.nombre}`
                    : `Agregar una unidad de ${product.nombre}`
            );
            if (delta === "1") {
                button.disabled = stock > 0 && quantity >= stock;
            }
        });

        line.querySelector(".cart-line-total").textContent = money(
            price * quantity
        );

        if (isNew) {
            line.classList.add("is-new");
        }

        return line;
    };

    const renderMethods = () => {
        methodButtons.forEach((button) => {
            button.setAttribute(
                "aria-pressed",
                state.methods.has(button.dataset.method) ? "true" : "false"
            );
        });
        methodButtons.forEach((button) => {
            button.parentElement
                ?.querySelectorAll(".split-input")
                .forEach((input) => input.remove());
        });

        if (state.methods.size < 2) {
            return;
        }

        state.methods.forEach((method) => {
            const button = methodButtons.find(
                (candidate) => candidate.dataset.method === method
            );
            if (!button) {
                return;
            }

            const input = document.createElement("input");
            input.type = "text";
            input.id = `importe-${method}`;
            input.className = "split-input";
            input.inputMode = "decimal";
            input.autocomplete = "off";
            input.placeholder = "0";
            input.setAttribute(
                "aria-label",
                `Importe para ${methodLabels.get(method) || method}`
            );
            input.value = state.amounts.get(method) || "";

            input.addEventListener("input", () => {
                state.amounts.set(method, input.value);
                refreshPaymentState();
            });

            input.addEventListener("blur", () => {
                if (!input.value.trim()) {
                    return;
                }
                const cents = parseAmount(input.value);
                input.value = money(cents).replace("$ ", "");
                state.amounts.set(method, input.value);
                refreshPaymentState();
            });

            button.parentElement.append(input);
        });
    };

    const refreshPaymentState = () => {
        const count = state.items.size;
        const total = totalCents();
        const methods = Array.from(state.methods);
        const label = methods.length
            ? methodLabels.get(methods[0]) || methods[0]
            : "";
        const single = methods.length === 1;
        const amounts = methods.map((method) =>
            single ? total : amountFor(method)
        );
        const sum = amounts.reduce((accumulator, value) => accumulator + value, 0);
        const splitReady =
            methods.length >= 2 && sum === total;

        canPay =
            count > 0 &&
            methods.length > 0 &&
            (single || splitReady);

        payBtn.disabled = !canPay;

        paymentNote.classList.remove("is-ready", "is-short", "is-over");
        if (count === 0) {
            paymentNote.textContent = "Agregá productos para cobrar.";
        } else if (methods.length === 0) {
            paymentNote.textContent = "Elegí uno o más medios de pago.";
        } else if (single) {
            paymentNote.textContent = `${label} · total completo.`;
            paymentNote.classList.add("is-ready");
        } else if (
            methods.every(
                (method) => parseAmount(state.amounts.get(method) || "") === 0
            )
        ) {
            paymentNote.textContent = "Completá los importes de cada medio.";
        } else if (sum < total) {
            paymentNote.textContent = `Faltan ${money(
                total - sum
            )} para completar el total.`;
            paymentNote.classList.add("is-short");
        } else if (sum > total) {
            paymentNote.textContent = `Los importes superan el total por ${money(
                sum - total
            )}.`;
            paymentNote.classList.add("is-over");
        } else {
            paymentNote.textContent = "Listo para cobrar.";
            paymentNote.classList.add("is-ready");
        }

        paymentInputs.replaceChildren();
        methods.forEach((method, index) => {
            const methodInput = document.createElement("input");
            methodInput.type = "hidden";
            methodInput.name = "medio_pago";
            methodInput.value = method;

            const amountInput = document.createElement("input");
            amountInput.type = "hidden";
            amountInput.name = `importe_${method}`;
            amountInput.value = (amounts[index] / 100).toFixed(2);

            paymentInputs.append(methodInput, amountInput);
        });
    };

    const focusAfterRender = (focus) => {
        if (!focus) {
            return;
        }
        if (focus.type === "search") {
            search.focus();
            return;
        }
        if (focus.type === "card") {
            const card = productGrid.querySelector(
                `[data-product-id="${focus.id}"]`
            );
            const target = state.items.has(String(focus.id))
                ? card && card.querySelector('[data-stepper] [data-step="1"]')
                : card && card.querySelector("[data-add]");
            if (target && !target.disabled) {
                target.focus();
            } else {
                search.focus();
            }
            return;
        }
        if (focus.type === "cart-step") {
            const button = cartItems.querySelector(
                `.step-btn[data-id="${focus.id}"][data-step="${focus.step}"]`
            );
            if (button && !button.disabled) {
                button.focus();
            } else {
                search.focus();
            }
        }
    };

    const renderCart = (options = {}) => {
        const justAdded = options.justAdded || null;
        cartItems.replaceChildren();

        state.items.forEach((quantity, id) => {
            const product = byId.get(id);
            if (product) {
                cartItems.append(
                    buildLine(product, quantity, justAdded === id)
                );
            }
        });

        cartEmpty.hidden = state.items.size > 0;
        cartClear.disabled = state.items.size === 0;

        const count = unitCount();
        const total = totalCents();
        cartCount.textContent = String(count);
        if (cartTotalMeta) {
            cartTotalMeta.textContent = `${count} artículo${
                count === 1 ? "" : "s"
            }`;
        }
        cartTotal.textContent = money(total);
        if (mobileCartCount) {
            mobileCartCount.textContent = String(count);
        }
        if (mobileCartTotal) {
            mobileCartTotal.textContent = money(total);
        }
        itemsInput.value = JSON.stringify(itemsPayload());

        updateCards();
        renderMethods();
        refreshPaymentState();
        persist();
        updateMobileBar();

        focusAfterRender(options.focus);
    };

    const resetPayments = () => {
        state.methods.clear();
        state.amounts.clear();
    };

    const changeQuantity = (id, delta, options = {}) => {
        const key = String(id);
        const product = byId.get(key);
        if (!product) {
            return;
        }
        const current = state.items.get(key) || 0;
        const stock = Number(product.stock);
        const next = current + delta;

        if (delta > 0 && stock > 0 && next > stock) {
            showToast(`No hay más stock de ${product.nombre}.`);
            return;
        }

        if (next <= 0) {
            state.items.delete(key);
        } else {
            const limit = stock > 0 ? stock : 99;
            state.items.set(key, Math.min(next, limit));
        }

        if (state.items.size === 0) {
            resetPayments();
        }

        renderCart({
            justAdded: delta > 0 ? key : null,
            focus: options.focus || null,
        });
    };

    const addProduct = (id, options = {}) => {
        const key = String(id);
        const product = byId.get(key);
        if (!product) {
            return false;
        }
        const current = state.items.get(key) || 0;
        const stock = Number(product.stock);
        if (stock > 0 && current >= stock) {
            showToast(`No hay más stock de ${product.nombre}.`);
            return false;
        }

        dismissSuccess();
        state.items.set(key, current + 1);

        if (options.clearSearch) {
            search.value = "";
            query = "";
            applyFilters();
        }

        renderCart({
            justAdded: key,
            focus: options.focus || null,
        });

        if (options.announce) {
            showToast(`${product.nombre} agregado al carrito.`);
        }
        return true;
    };

    const removeProduct = (id) => {
        state.items.delete(String(id));
        if (state.items.size === 0) {
            resetPayments();
        }
        renderCart({ focus: { type: "search" } });
    };

    const clearCart = (announce = true) => {
        if (state.items.size === 0) {
            return;
        }
        const snapshot = new Map(state.items);
        state.items.clear();
        resetPayments();
        renderCart({ focus: { type: "search" } });
        if (announce) {
            showToast("Carrito vaciado.", {
                label: "Deshacer",
                run: () => {
                    snapshot.forEach((quantity, id) => {
                        state.items.set(id, quantity);
                    });
                    renderCart({ focus: { type: "search" } });
                },
            });
        }
    };

    const applyFilters = () => {
        let visible = 0;
        cards.forEach((card) => {
            const matchesCategory =
                activeCategory === "todos" ||
                card.dataset.cat === activeCategory;
            const matchesQuery =
                !query || card.dataset.search.includes(query);
            const show = matchesCategory && matchesQuery;
            card.hidden = !show;
            if (show) {
                visible += 1;
            }
        });

        catalogCount.textContent = String(visible);
        catalogEmpty.hidden = visible !== 0;
        productGrid.hidden = visible === 0;
        searchClear.hidden = !search.value;

        if (query) {
            emptyTitle.textContent = `Sin resultados para “${search.value.trim()}”`;
        } else {
            emptyTitle.textContent = emptyTitleDefault;
        }
    };

    const clearSearch = (focus) => {
        search.value = "";
        query = "";
        applyFilters();
        if (focus) {
            search.focus();
        }
    };

    const setCategory = (category) => {
        activeCategory = category;
        catTabs.forEach((tab) => {
            const active = tab.dataset.cat === category;
            tab.classList.toggle("is-active", active);
            tab.setAttribute("aria-pressed", active ? "true" : "false");
        });
        applyFilters();
    };

    const setColumns = (columns) => {
        const value = String(columns);
        productGrid.style.setProperty("--cols", value);
        columnButtons.forEach((button) => {
            const active = button.dataset.cols === value;
            button.classList.toggle("is-active", active);
            button.setAttribute("aria-pressed", active ? "true" : "false");
        });
        try {
            window.localStorage.setItem(columnsKey, value);
        } catch (error) {
            /* La preferencia es opcional. */
        }
    };

    const dismissSuccess = () => {
        if (!saleSuccess || saleSuccess.hidden) {
            return false;
        }
        saleSuccess.hidden = true;
        cartLive.hidden = false;
        clearPersisted();
        return true;
    };

    /* Eventos del catálogo */

    search.addEventListener("input", () => {
        query = normalize(search.value);
        applyFilters();
    });

    search.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            if (search.value) {
                event.preventDefault();
                clearSearch(true);
            } else {
                search.blur();
            }
            return;
        }
        if (event.key !== "Enter") {
            return;
        }
        event.preventDefault();
        const raw = search.value.trim();
        if (!raw) {
            return;
        }
        const exact = catalog.find(
            (product) => product.codigo && product.codigo === raw
        );
        if (exact) {
            addProduct(exact.id, {
                clearSearch: true,
                focus: { type: "search" },
                announce: true,
            });
            return;
        }
        const visible = cards.filter((card) => !card.hidden);
        if (visible.length === 1) {
            addProduct(visible[0].dataset.productId, {
                clearSearch: true,
                focus: { type: "search" },
                announce: true,
            });
        } else if (visible.length > 1) {
            const first = visible[0].querySelector("[data-add]");
            if (first) {
                first.focus();
            }
        }
    });

    searchClear.addEventListener("click", () => clearSearch(true));

    clearFilters.addEventListener("click", () => {
        clearSearch(false);
        setCategory("todos");
        search.focus();
    });

    catTabs.forEach((tab) => {
        tab.addEventListener("click", () => setCategory(tab.dataset.cat));
    });

    columnButtons.forEach((button) => {
        button.addEventListener("click", () => {
            setColumns(button.dataset.cols);
        });
    });

    productGrid.addEventListener("click", (event) => {
        const add = event.target.closest("[data-add]");
        if (add) {
            addProduct(add.dataset.add, {
                focus: { type: "card", id: add.dataset.add },
            });
            return;
        }
        const step = event.target.closest(".step-btn");
        if (!step) {
            return;
        }
        const id = step.dataset.id;
        const delta = Number(step.dataset.step);
        changeQuantity(id, delta, {
            focus: { type: "card", id },
        });
    });

    cartItems.addEventListener("click", (event) => {
        const remove = event.target.closest("[data-remove]");
        if (remove) {
            removeProduct(remove.dataset.remove);
            return;
        }
        const step = event.target.closest(".step-btn");
        if (!step) {
            return;
        }
        const id = step.dataset.id;
        const delta = Number(step.dataset.step);
        changeQuantity(id, delta, {
            focus: { type: "cart-step", id, step: delta },
        });
    });

    cartClear.addEventListener("click", () => clearCart(true));

    methodButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const method = button.dataset.method;
            if (state.methods.has(method)) {
                state.methods.delete(method);
                state.amounts.delete(method);
            } else {
                state.methods.add(method);
                if (state.methods.size >= 2) {
                    state.methods.forEach((selected) => {
                        if (!state.amounts.has(selected)) {
                            state.amounts.set(selected, "");
                        }
                    });
                }
            }
            if (state.methods.size <= 1) {
                state.amounts.clear();
            }
            renderMethods();
            refreshPaymentState();
            if (state.methods.size >= 2) {
                const first = document.querySelector(".split-input");
                if (first && !first.value) {
                    first.focus();
                }
            }
        });
    });

    form.addEventListener("submit", (event) => {
        if (!canPay) {
            event.preventDefault();
            return;
        }
        if (form.dataset.submitting === "1") {
            event.preventDefault();
            return;
        }
        form.dataset.submitting = "1";
        payBtn.disabled = true;
        const label = payBtn.querySelector("span");
        if (label) {
            label.textContent = "Cobrando…";
        }
    });

    if (newSale) {
        newSale.addEventListener("click", () => {
            dismissSuccess();
            clearPersisted();
            renderCart({ focus: { type: "search" } });
        });
    }

    document.addEventListener("keydown", (event) => {
        const target = event.target;
        const typing =
            target instanceof HTMLElement &&
            (target.tagName === "INPUT" ||
                target.tagName === "TEXTAREA" ||
                target.isContentEditable);

        if (event.key === "F2") {
            event.preventDefault();
            search.focus();
            search.select();
            return;
        }

        if (event.key === "F4") {
            event.preventDefault();
            if (saleSuccess && !saleSuccess.hidden) {
                dismissSuccess();
                search.focus();
                return;
            }
            if (!payBtn.disabled) {
                payBtn.focus();
            } else {
                methodButtons[0]?.focus();
            }
            return;
        }

        if (event.key === "/" && !typing) {
            event.preventDefault();
            search.focus();
            return;
        }

        if (event.key === "Escape" && !typing && search.value) {
            clearSearch(true);
        }
    });

    /* Estado inicial */

    const storedColumns = (() => {
        try {
            return window.localStorage.getItem(columnsKey);
        } catch (error) {
            return null;
        }
    })();
    if (["2", "3", "4"].includes(storedColumns)) {
        setColumns(storedColumns);
    }

    if (cartRail && "IntersectionObserver" in window) {
        const observer = new IntersectionObserver(
            (entries) => {
                cartInView = entries.some((entry) => entry.isIntersecting);
                updateMobileBar();
            },
            { threshold: 0.15 }
        );
        observer.observe(cartRail);
    }

    const onCompactChange = () => updateMobileBar();
    if (compactMedia.addEventListener) {
        compactMedia.addEventListener("change", onCompactChange);
    } else if (compactMedia.addListener) {
        compactMedia.addListener(onCompactChange);
    }

    hydrate();
    applyFilters();
    renderCart();
})();
