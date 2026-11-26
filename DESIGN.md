---
name: PosIA
description: "Punto de venta de almacén: un tablero limpio y luminoso donde el catálogo, el carrito y el cobro no compiten con el próximo escaneo."
colors:
  canvas: "#e9eef4"
  surface: "#ffffff"
  surface-2: "#f5f7fa"
  surface-3: "#eef2f6"
  ink: "#161a1f"
  ink-2: "#556173"
  ink-3: "#667386"
  ink-4: "#93a0b1"
  line: "#e3e8ee"
  line-strong: "#d3dae3"
  red: "#d92d2d"
  red-hover: "#bd2323"
  red-soft: "#fdecec"
  red-ink: "#b32626"
  green: "#0b7a56"
  green-hover: "#086346"
  green-soft: "#e8f6f0"
  green-ink: "#076a4a"
  amber: "#8a5200"
  amber-soft: "#fff4dc"
  cat-almacen-bg: "#fbf1dd"
  cat-almacen-ink: "#8a5a00"
  cat-bebidas-bg: "#eaf0fe"
  cat-bebidas-ink: "#1d4ed8"
  cat-congelados-bg: "#e5f5f9"
  cat-congelados-ink: "#0e6e8a"
  cat-fiambreria-bg: "#fbecef"
  cat-fiambreria-ink: "#9d2f4b"
  cat-golosinas-bg: "#fcecf5"
  cat-golosinas-ink: "#a3206b"
  cat-limpieza-bg: "#e6f5f1"
  cat-limpieza-ink: "#0b6b5e"
  cat-lacteos-bg: "#edeffc"
  cat-lacteos-ink: "#3b4cb8"
  cat-panaderia-bg: "#f8eee5"
  cat-panaderia-ink: "#8a4b1f"
  cat-perfumeria-bg: "#f1ecfe"
  cat-perfumeria-ink: "#6d28d9"
  cat-otros-bg: "#eef2f6"
  cat-otros-ink: "#4a5568"
typography:
  display:
    fontFamily: "Figtree, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "36px"
    fontWeight: 750
    lineHeight: 1.1
    letterSpacing: "-0.04em"
  headline:
    fontFamily: "Figtree, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "28px"
    fontWeight: 750
    lineHeight: 1.12
    letterSpacing: "-0.03em"
  title:
    fontFamily: "Figtree, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "16px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.015em"
  body:
    fontFamily: "Figtree, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.45
    letterSpacing: "0em"
  label:
    fontFamily: "Figtree, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "11px"
    fontWeight: 700
    lineHeight: 1.45
    letterSpacing: "0.1em"
  total:
    fontFamily: "Figtree, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "27px"
    fontWeight: 750
    lineHeight: 1
    letterSpacing: "-0.035em"
    fontFeature: "tnum"
rounded:
  xl: "24px"
  lg: "16px"
  card: "14px"
  field: "10px"
  sm: "9px"
  control: "8px"
  chip: "5px"
components:
  button-add:
    backgroundColor: "{colors.red}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    height: "40px"
    padding: "0 14px"
  button-add-hover:
    backgroundColor: "{colors.red-hover}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    height: "40px"
    padding: "0 14px"
  button-pay:
    backgroundColor: "{colors.green}"
    textColor: "{colors.surface}"
    rounded: "{rounded.field}"
    height: "48px"
    padding: "0 16px"
  button-primary:
    backgroundColor: "{colors.red}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
    height: "38px"
    padding: "0 14px"
  button-primary-hover:
    backgroundColor: "{colors.red-hover}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
    height: "38px"
    padding: "0 14px"
  button-ghost:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.sm}"
    height: "38px"
    padding: "0 14px"
  search-field:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    height: "42px"
  category-tab:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.control}"
    height: "40px"
    padding: "0 10px"
  category-tab-active:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    height: "40px"
    padding: "0 10px"
  nav-item-active:
    backgroundColor: "{colors.red-soft}"
    textColor: "{colors.red-ink}"
    rounded: "{rounded.sm}"
    height: "40px"
    padding: "0 10px"
  ticket-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    padding: "13px"
  product-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
  status-chip:
    backgroundColor: "{colors.green-soft}"
    textColor: "{colors.green-ink}"
    rounded: "{rounded.chip}"
    padding: "3px 7px"
  pay-method:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink-2}"
    rounded: "{rounded.control}"
    height: "40px"
    padding: "0 9px"
  pay-method-selected:
    backgroundColor: "{colors.surface-2}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    height: "40px"
    padding: "0 9px"
---

# Design System: PosIA

## Overview

**Creative North Star: "El mostrador iluminado" ("The Lit Counter")**

PosIA is a lit work board at a neighborhood counter: a cool paper field holds one white application frame, a calm white sidebar, a fluid catalog in the center, and a cart rail that tops out at 400px while owning the checkout. The composition is pinned by the client's reference image, but the content is the real almacén. Nothing decorative competes with the next scan: no food photography, no invented customer or table, no promo chrome. The only saturated color on a normal screen is the red used to add or to ask, plus the green that appears when money is taken.

The material is exact and quiet. One self-hosted variable family, Figtree, does all the talking; money is always tabular, so totals never jitter as quantities change. Cards and panels are border-only white, the single 24px frame carries the only structural shadow, and color appears as low-tint category fields behind authored line pictograms. The result reads as a clean instrument rather than a restaurant dashboard.

**Key Characteristics:**
- 20px of cool-paper air around a 24px-radius frame; 232px white sidebar, fluid center, cart rail capped at 400px.
- Action Red adds and asks; Pay Green takes money; Stock Amber warns; none of them trade jobs.
- Every price, count and total uses tabular numerals; headings track tight (-0.02 to -0.04em).
- Content is border-only: 1px hairlines, 14px cards, 16px panels; depth lives at the frame.
- Category fiches are flat tinted fields with dark category ink and 1.5px authored pictograms; UI icons are 1.75px.
- Primary controls are 40px; dense cart steppers are 32px inside a 40px stepper; the absolute floor is 24px.
- No raster assets ship. The mark, the empty-cart art and all category pictograms are authored SVG.

## Colors

A cool-paper and white room with near-black ink, two saturated working colors and one warning amber; the only other color comes from ten paired category fields.

### Primary
- **Action Red** (#d92d2d): the add buttons on product cards, the assistant's Consultar button, the chat Enviar button, the active navigation wash and ink, the text caret and the selected split control. Its state family is **Pressed Red** (#bd2323), **Red Wash** (#fdecec) and **Red Ink** (#b32626). The red was tuned darker than the reference so white text on it clears AA; it is an action color, never a page fill.

### Secondary
- **Pay Green** (#0b7a56): the Cobrar CTA, the selected-payment check, the ready payment note, the success mark and the Cobrada chip. Its family is **Pressed Green** (#086346), **Green Wash** (#e8f6f0) and **Green Ink** (#076a4a). Green is reserved for money received and states that confirm readiness.

### Tertiary
- **Stock Amber** (#8a5200): the low-stock chip on **Amber Wash** (#fff4dc) and the short-payment note in Stock Amber text. It is the only warning color; it never becomes an action or a category tint.

### Neutral
- **Cool Paper** (#e9eef4): the canvas outside the frame. The frame floats on it with 20px of air.
- **White Counter** (#ffffff): frame, sidebar, cards, panels, fields and the cart rail.
- **Haze** (#f5f7fa) and **Quiet Wash** (#eef2f6): quiet fills for chips, count pills, the segmented track, thumbnails, disabled controls and AI message bodies.
- **Ink** (#161a1f): primary text, the filled active category tab, the mobile cart bar, the user chat bubble, and the focus outline.
- **Slate** (#556173), **Muted Slate** (#667386), **Faint Slate** (#93a0b1): secondary text at three strengths, down to disabled labels and decorative icon marks.
- **Hairline** (#e3e8ee) and **Strong Hairline** (#d3dae3): the 1px structure of the whole product. Hairline divides; Strong Hairline wraps fields, steppers and the frame.

### Category Fields
Each category is one flat background plus one dark ink, used only behind its pictogram or cart thumbnail:
- **Almacén** (#fbf1dd / #8a5a00), **Bebidas** (#eaf0fe / #1d4ed8), **Congelados** (#e5f5f9 / #0e6e8a), **Fiambrería** (#fbecef / #9d2f4b), **Golosinas** (#fcecf5 / #a3206b), **Limpieza** (#e6f5f1 / #0b6b5e), **Lácteos** (#edeffc / #3b4cb8), **Panadería** (#f8eee5 / #8a4b1f), **Perfumería** (#f1ecfe / #6d28d9), and **Sin categoría / Otros** (#eef2f6 / #4a5568).

### Named Rules
**The Red Adds, Green Pays Rule.** Red is the color of adding a product or asking a question; green is the color of taking money. Red never fills the Cobrar button, green never fills Agregar, and amber never becomes either.

**The Tint Is a Field Rule.** A category color exists only as a flat field behind a category pictogram or thumbnail, paired with its dark ink. It never fills a card body, a panel, a header, or the page.

## Typography

**Display Font:** Figtree variable (with ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif)
**Body Font:** Figtree variable (same stack; one family carries the entire product)
**Label/Mono Font:** none; labels are Figtree in uppercase, money uses tabular figures rather than a mono face.

**Character:** A geometric-humanist sans with open counters and a broad weight range (300–900, used from 400 to 800). It is compact enough for a dense counter and calm enough that the money can be the loudest element. There is no display face and no second family.

### Hierarchy
- **Display** (750, 36px/1.1, -0.04em): the completed-sale total only. It is the largest type in the product and the payoff of the checkout.
- **Headline** (750, 26–28px/1.1–1.12, -0.03em): page titles — Caja, Asistente comercial, Chat. The POS title steps down to 24px at 1080 and 23px at 620; mobile page titles reach 24px.
- **Title** (700, 16px/1.2, -0.015em): section titles such as Tickets recientes and Catálogo, the 15px cart title and 13px panel titles. Product and store names use 13px/600.
- **Body** (400–600, 14px/1.45): the base. Dense operational copy drops to 12.5–13.5px (product names 13/600, cart names 12/650, chat messages 12.5/1.6); long answer prose stays at 14px/1.65 with a 72ch cap.
- **Label** (700, 11px, 0.1em, uppercase): sidebar group labels and the PUNTO DE VENTA brand sub-line. Payment eyebrow copy uses 11px/0.02em without uppercase.
- **Total** (750, 12–27px, -0.01 to -0.035em, tabular): line total 12px, product and ticket totals 17px, cart total 27px; the receipt's 36px total is the Display role. All figures are `tabular-nums`.

### Named Rules
**The Tabular Money Rule.** Every price, subtotal, total, quantity and count uses tabular numerals. Proportional figures are a bug anywhere money or stock can change.

**The Versalitas Belong to the Sidebar Rule.** Uppercase 11px with 0.1em tracking is the sidebar's group voice and micro-label voice. It never becomes a page-level kicker above a heading.

**The 11px Floor Rule.** Functional copy never sets below 11px. The only smaller type is the glyph inside a keycap (`kbd`, 9–10px), which is a symbol, not a sentence.

## Layout

The application is a framed desktop workspace: at least 20px of canvas air on every side, a white frame at up to 1680px wide and `100dvh - 40px` tall, a 232px sidebar, a fluid content column, and a cart rail clamped between 320px and 400px (`clamp(320px, 30vw, 400px)`). The frame has a 1px Strong Hairline border and a 24px radius; inside, the sidebar is separated by a 1px Hairline, and the center column scrolls independently.

The POS center uses 22px top, 24px side and 34px bottom padding. Recent tickets are a three-column grid with 12px gaps; the catalog is a 12px-gap grid with a user-switchable 2, 3 or 4 columns (3 by default, persisted in local storage). The cart rail is a fixed three-part stack: header with count and context pills, a flexible line list that scrolls on its own, and a pinned checkout block holding total, payment methods and the pay CTA.

The assistant is a 330px suggestion column plus a fluid working column inside a 1180px page; the chat is a 980px column with a single 18px-radius conversation shell that fills the available height. Both use the same frame and sidebar, with 24–30px page padding.

The working rhythm is 4, 6, 8, 10, 12, 14, 18, 20, 22, 24, 28 and 34px: 6–8px inside compact controls, 10–14px inside cards and between rows, 20–24px between sections, and 34px at the bottom of the scrolling catalog.

Responsive behavior:
- **≤1199px:** sidebar narrows to 208px, tickets become a horizontally scroll-snapping strip, the product grid drops to two columns, and the column-density control is hidden.
- **≤1080px:** center and cart paddings tighten to 16–22px; the POS title drops to 24px.
- **≤980px:** the frame becomes edge-to-edge with no radius or shadow; a 52px sticky white topbar appears with a menu button, the PosIA mark and the current context (Caja 1, Asistente or Chat). The sidebar becomes an off-canvas 286px drawer over a scrim. The cart stacks under the catalog, and a fixed dark cart bar (56px minimum, 12px inset) shows count, total and "Ver carrito". The bar hides when the cart rail is at least 15% in view or while the sale receipt is shown. The desktop rail itself is unchanged in composition.
- **≤620px:** two catalog columns at 9px gap, a 82vw ticket card, full-width search, 14–16px page padding, and the 23px POS title.

### Named Rules
**The Frame-in-Air Rule.** Above 980px the product lives inside a 24px-radius white frame with at least 20px of cool paper visible on every side. It never runs edge-to-edge on desktop.

**The Money Stays in Reach Rule.** The cart header, total and pay CTA are never scrolled away by cart lines; only the line list flexes. On compact screens the bottom cart bar stands in until the rail itself is visible.

## Elevation & Depth

The system is flat by default and border-led. Content surfaces — tickets, product cards, panels, the sidebar, the cart rail — are flat white with a 1px Hairline and no shadow at rest. Depth is conveyed by the frame first, by a faint hover lift second, and by transient overlays third. There are no gradients, no glass and no backdrop blur.

### Shadow Vocabulary
- **Frame** (`box-shadow: 0 24px 60px -28px rgba(22, 26, 31, 0.25), 0 2px 8px rgba(22, 26, 31, 0.05)`): the single structural shadow, on the application frame only.
- **Popover** (`box-shadow: 0 12px 32px -12px rgba(22, 26, 31, 0.22)`): off-canvas sidebar, toast, and the compact cart bar.
- **Card hover** (`box-shadow: 0 10px 22px -18px rgba(22, 26, 31, 0.32)` for tickets; `0 12px 24px -20px rgba(22, 26, 31, 0.30)` for products): a suggestion of lift paired with a border shift and `translateY(-1px)`.
- **Active segment** (`box-shadow: 0 1px 2px rgba(22, 26, 31, 0.10)`): the white thumb inside the density segmented control.
- **Selected payment** (`box-shadow: inset 0 0 0 1px #161a1f`): the inset second border that marks a chosen method.
- **Success glow** (`box-shadow: 0 8px 20px -10px rgba(11, 122, 86, 0.60)`): the 52px circular success mark, the one celebratory lift in the product.
- **Focus halo** (`box-shadow: 0 0 0 3px rgba(22, 26, 31, 0.06)` with a 1px Ink border): fields and search on focus; the global `:focus-visible` outline is 2px Ink with 2px offset.

### Named Rules
**The Frame Owns the Shadow Rule.** Structural depth belongs to the 24px application frame. Cards do not carry resting shadows; they earn a thin hover suggestion or a transient overlay, never both at rest.

**The Border Does the Work Rule.** When a surface needs definition, add or strengthen a 1px hairline; do not reach for a shadow or a tinted panel.

## Shapes

Corners descend with the container: 24px frame, 16px panels (18px for the chat shell), 14px content cards (tickets, products, empty states), 10px fields and primary pay surfaces (search, segmented track, Cobrar), 9px sidebar items and thumbnails, 8px compact controls (category tabs, add buttons, product steppers, payment tiles), 7px split-amount fields and dense cart steppers, and 4–7px chips, counts and keycaps. Circular geometry is reserved for the success mark, the selected-payment check, the chat empty mark, and status dots.

Borders are 1px throughout, in Hairline for structure and Strong Hairline for interactive fields and steppers. Dashed 1px borders are the signature of absence and receipt structure: empty ticket/catalog/answer states, the ticket footer divider, and the payment block on the sale receipt. Media is a 16:9 flat tinted field, not a photo. There is no clipping beyond card overflow, no inset bevel, and no decorative gradient.

### Named Rule
**The Radius Follows the Container Rule.** Bigger container, bigger corner: frame 24, panel 16, card 14, field 10, control 8, chip 5. Never round a chip like a card or a card like the frame.

## Components

### Buttons
- **Shape:** compact, full-width where it belongs to a card; 8px radius for the red Agregar (40px tall) and 10px for the green Cobrar (48px tall). Toolbar and assistant buttons use 9px at 38px tall (36px in the small variant).
- **Primary add:** Action Red fill, white 12px/650 label, 5px gap to a 14px plus icon; hover darkens to Pressed Red; active drops 1px; disabled becomes Quiet Wash with Muted Slate text.
- **Pay:** full-width green, 14px/700 label on the left, arrow on the right, 16px side padding; hover Pressed Green; disabled Quiet Wash with Faint Slate; on submit the label becomes "Cobrando…".
- **Ghost / text:** white with a Strong Hairline and Slate text (Ver ventas, Copiar); text buttons are 11px/650 with a 40px hit area, underline on hover, Red Ink for destructive Vaciar.
- **Focus:** 2px Ink outline at 2px offset on every control; fields add the soft 3px halo instead.

### Search and Filters
- **Search field:** 42px tall, 10px radius, Strong Hairline, a 17px Muted Slate magnifier inset 12px, and an F2 keycap on the right. Focus turns the border Ink and adds the 3px ink halo. The clear button is a 40px square that appears only with text.
- **Density control:** a 48px Haze track with 3px padding holding three 38×40 icon buttons at 7px radius; the active one is a white thumb with the active-segment shadow. It disappears below 1200px.
- **Category tabs:** 40px tall, 8px radius, 1px Hairline, 11.5px/600 Slate label plus an 11px tabular count in a Haze pill. Active inverts to Ink fill, white text and a translucent white count. Hover only strengthens the border.

### Cards and Containers
- **Corner style:** 14px for ticket and product cards, 16px for panels and answer cards.
- **Background:** white; no tinted card bodies.
- **Border:** 1px Hairline at rest, Strong Hairline on hover.
- **Internal padding:** 13px for tickets, 11–12px for product bodies, 16–18px for panels, 18–20px for answer cards.
- **Ticket card:** 124px minimum height; id and green Cobrada chip on top, a two-line clamped product summary, time and article count in 11px tabular meta, then a dashed-top footer with the total and a truncated compact payment label ("Tarjeta · Transf.") whose full value is visually hidden. Hover: Strong Hairline, faint shadow, 1px lift.
- **Product card:** 16:9 category field with an 11px/750 uppercase category name at top-left, a translucent white stock chip at top-right (Amber Wash for "Quedan N", Red Wash for "Sin stock"), and an authored category pictogram at 38–62px. Below: a two-line clamped 13px name, 17px tabular price, then a 40px red Agregar that swaps in place for a 40px stepper once the product is in the cart.
- **Empty states:** dashed Strong Hairline at 14px radius, centered Muted Slate copy capped at 34–38ch, and an 18–22px pictogram, with a 78px authored cart drawing in the empty rail.

### Inputs and Fields
- **Style:** white, 1px Strong Hairline, 10px radius for the main search and the 112px-min assistant textarea; 7px radius for the 32px split-amount inputs.
- **Focus:** Ink border plus the 3px 6% ink halo; no glow color.
- **Density:** the assistant textarea is 15px/1.5 with 12–13px padding; the chat composer is borderless inside an 11px-radius row that carries the focus treatment.
- **Split amounts:** right-aligned, tabular, 11.5px/650, 112px wide; blur reformats to Argentine grouping.

### Navigation
- **Desktop sidebar:** 232px white, 20px top and 14px side padding, 38px red rounded-square mark with a white ticket glyph, 18px/800 wordmark and an 11px/700 0.1em uppercase sub-line. Groups are 11px/700 uppercase Muted Slate labels; items are 40px tall, 9px radius, 13px/550 Slate with 1.75px icons. Hover is Haze; active is Red Wash with Red Ink and weight 650. External links add a 12px 40%-opacity arrow.
- **Footer:** a 34px avatar tile, 12px/650 name, 11px Muted Slate role, then a 30px icon button; separated by a 1px Hairline.
- **Compact:** 52px sticky white topbar with a 40px menu button, a 26px red mark and the 14px/800 wordmark; the context label sits right. Sidebar becomes a 286px off-canvas drawer with a scrim and a 32px close button.

### Payment Rail (signature)
The cart rail (320–400px) is the checkout instrument. Header: 17px cart icon, 15px/700 "Carrito", an 11px tabular count badge and a Red Ink Vaciar text button. Under it, 22px context pills for Mostrador and Caja 1 plus an 11px uppercase date. The line list is the only flexible region; each line pairs a 42px tinted category thumbnail with a two-line name, an 11px unit price, a 40px stepper (30×32 step buttons, 12px/700 tabular quantity) and a 12px/750 line total. The checkout block holds a 27px/750 tabular total over an 11px article count, a 2×2 grid of 40px payment tiles, and the 48px green Cobrar.

Payment tiles carry a 16px muted icon and an 11px label; selection turns the border and text Ink, adds the inset ink ring, and fades in a 15px green circular check. Dividing the payment reveals one 32px amount field per selected method and a status note that moves through Red Ink (over), Amber (short), and Green Ink (ready). The CTA only enables when the cart has items and the selected method is "total completo" or the split amounts sum exactly.

### Receipt (signature)
After a sale, the rail becomes a receipt: a 52px green circle with a check, a green Cobrada chip, "Venta N°…", the 36px tabular total, a one-line article and stock note, a sold-line list (quantity, name, line total) capped at 160px, a dashed-top-and-bottom payment block, a 44px "Nueva venta" button and a "Ver en administración" text link. It replaces the live cart in place; scanning again dismisses it.

### Assistant and Chat
The assistant uses a 330px "Consultas rápidas" panel: 28px icon tiles on Haze, 11.5px/650 titles, 11px queries separated by hairlines, and a shield note that states the read-only contract. The composer is a 16px-radius panel with an uppercase 11px label, a 112px textarea, an 11px tabular character count and the red Consultar. Answers sit in a 16px panel: a 12px/750 header with a green "Datos del POS" badge, the echoed question in a Haze box, and 14px/1.65 prose capped at 72ch.

Chat is one 18px-radius shell: a 12px header with a green-dot "Datos del POS" status, a 16px-gap thread, user messages as Ink bubbles with a 13/13/4/13 radius, AI messages as Haze bodies with a 4/13/13/13 radius beside a 26px red sparkle tile. Empty chat shows a 54px Red Wash circle, 18px question, 12px explanation and 30px suggestion chips. The composer row pairs a borderless 13px textarea with a 34px red Enviar.

### Feedback
Toasts are fixed Ink bars at the bottom center, 11.5px white text, 10px radius and the Popover shadow; destructive clears offer a 6-second Deshacer. Alerts and notices are Red Wash with Red Ink and a 1px pale red border. Status chips are 11px/750 uppercase on Green Wash. Motion is 100–220ms ease for state changes, 600ms for the green wash on a newly added cart line, and a 1.2s breathing loop for chat typing dots; `prefers-reduced-motion` collapses every duration to 0.01ms.

## Do's and Don'ts

### Do:
- **Do** keep the desktop frame in at least 20px of cool paper with a 24px radius, a 232px white sidebar and a cart rail capped at 400px.
- **Do** reserve Action Red for adding and asking, Pay Green for taking money, and Stock Amber for warnings.
- **Do** set every price, quantity, count and total in tabular numerals.
- **Do** define surfaces with 1px Hairline borders and the 14px card / 16px panel radius pair.
- **Do** place category tints only behind pictograms and thumbnails, paired with their dark category ink.
- **Do** hold primary controls at 40px, dense cart steppers at 32px inside a 40px stepper, and never below a 24px target.
- **Do** keep total, count and the pay CTA visible while cart lines flex, and use the compact cart bar until the rail is in view.
- **Do** format pesos as "$ 4.500" and pair every abbreviated payment label with a visually hidden full label.
- **Do** author pictograms as SVG: 1.75px strokes for UI, 1.5px for category art.

### Don't:
- **Don't** add product photos, fake customers, tables, shifts, discounts, taxes, promos or testimonials; the almacén data is the only content.
- **Don't** use red on the Cobrar button or green on Agregar.
- **Don't** put shadows on content cards at rest; the frame owns structural depth.
- **Don't** set functional copy below 11px, with keycap glyphs (9–10px) as the only exception.
- **Don't** introduce page-level kickers or eyebrows; uppercase 11px belongs to sidebar groups and micro-labels.
- **Don't** use gradients, glass, backdrop blur or tinted page sections.
- **Don't** replace Figtree with a display or serif face, or money with proportional figures.
- **Don't** round a chip like a card, a card like a panel, or a panel like the frame.
