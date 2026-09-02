# BMA Compiler — UI/UX Redesign

The Compiler now runs the same design language as the BMA – NFE sector app:
a Bootstrap 5.3 shell with a UNICEF-derived palette, Inter typography and
high-density operational tables. This document covers what changed, and —
more importantly — the compatibility layer that lets ~300 legacy templates
inherit the redesign without being rewritten.

---

## 1. Architecture

**Shell.** `templates/base.html` is the golden source: a flex `app-wrapper`
with a sticky sidebar, a sticky topbar, the page body and a footer. It renders
no chrome for anonymous visitors, so the auth screens get the viewport to
themselves. Navigation lives in `templates/_sidebar_links.html`, flat (no
nested accordions) and gated by the same groups the old header mega-menu used.

**RTL.** Direction comes from `LANGUAGE_BIDI`; the RTL Bootstrap build is
swapped in automatically. Component CSS uses logical properties
(`margin-inline-start`, `inset-inline-end`, `border-start-start-radius`) rather
than hardcoded left/right, so the layout mirrors without a second stylesheet.

## 2. Design tokens

`static/css/redesign.css` opens with the token layer. Change colour, spacing,
radius, elevation or motion there and it propagates everywhere.

| Token group | Notes |
|---|---|
| Brand | `--unicef-blue #0097D7`, `--unicef-dark-blue #004F71`, `--unicef-light-blue #E1F5FE` |
| Surfaces | `--surface-body / -raised / -sunken / -hover` |
| Text | `--text-primary / -secondary / -muted` |
| Radius | `--radius-xs` → `--radius-xl`, `--radius-pill` |
| Elevation | `--shadow-xs` → `--shadow-xl` |
| Motion | `--duration-fast/base/slow`, `--ease-out`, `--ease-in-out` |
| Layout | `--sidebar-width`, `--header-height`, `--content-gutter` |

**Dark theme.** Opt-in via the topbar toggle, which sets `data-theme="dark"` on
`<html>` and persists the choice in `localStorage`. Only the tokens are
redefined, so components need no dark-specific rules. Bootstrap's few
hardcoded greys (breadcrumbs) are re-bound to tokens.

**Reduced motion.** `prefers-reduced-motion` collapses every duration to ~0.

## 3. Components

Provided by `redesign.css`: `.page-header`, `.card` / `.card-interactive`,
`.metric-card` + `.metric-icon/value/label/trend`, `.quick-action-tile`,
`.stepper` and `.wizard-progress`, `.table-container` + `.table-toolbar`,
`.filter-chip`, `.status-pill`, `.empty-state`, `.skeleton`, `.timeline`,
`.profile-header`, `.auth-shell` / `.auth-card`, `.form-section`,
`.form-actions-sticky`.

Tables are the workhorse: sticky headers, sort affordances on every orderable
column, hover row tracking, a scroll container sized for wide grids, and
`.table-compact` for the densest screens.

## 4. The compatibility layer — read before deleting anything

`static/css/bs4-compat.css` is deliberate, not leftover. The shell moved to
Bootstrap 5 but most page templates were written against Bootstrap 4 and the
ArchitectUI theme, and rewriting all of them would have meant touching every
operational form. Instead the old vocabulary is re-homed onto the new system:

- **Bootstrap 4 utilities BS5 renamed or dropped** — `ml-*`/`mr-*`/`pl-*`/`pr-*`,
  `float-left/right`, `text-left/right`, `form-group`, `control-label`,
  `btn-block`, `badge-<colour>`, `.close`, `custom-select`,
  `input-group-append/prepend`, `media`, `no-gutters`, `form-row`, `sr-only`,
  `font-weight-*`, and `form-inline` (which the django-filter panels still set).
- **ArchitectUI components** — `app-page-title` (~90 templates), `main-card`
  (~69), `forms-wizard` (~52), `vertical-timeline`, `widget-*`, `icon-wrapper`,
  `grid-menu`, `divider`, `card-header-tab`, `badge-dot`, the gradient `bg-*`
  helpers and the SweetAlert-style modal bodies.
- **Legacy icon fonts** — Pe-icon-7-stroke, Linearicons, Ionicons and the
  Bootstrap 2 / Glyphicon classes shipped inside the ArchitectUI bundle, which
  is no longer loaded. All of them are re-pointed at Bootstrap Icons glyphs
  (`pe-7s-info` alone appears ~660 times). Codepoints were extracted from the
  bootstrap-icons 1.11.3 stylesheet, not typed by hand — regenerate the same
  way if you add more.

`static/js/redesign.js` does the behavioural half: it mirrors any remaining
`data-toggle`/`data-dismiss`/`data-target`/`data-parent` onto their `data-bs-*`
names (including on content injected later, via a MutationObserver), so legacy
modals, tabs and dropdowns keep working.

## 5. Things worth knowing

**The wizard.** Multi-step registration and service forms used to be driven by
SmartWizard inside the 2.3 MB ArchitectUI bundle. That bundle is gone;
`redesign.js` carries a dependency-free replacement that honours the existing
contract — the per-module scripts (`mscc.js`, `tls.js`, `youth.js`) validate on
`#next-btn22` and call `preventDefault()` to block, and the driver only advances
on a click that survived that.

**Attendance toggles.** `data-toggle="buttons"` has no Bootstrap 5 equivalent.
The nested radio still works natively; the selected-state styling is restored
with CSS `:has()` plus a small class-sync handler for older browsers.

**Forms.** crispy-forms renders through the `bootstrap5` pack. `bootstrap3`
stays installed for anything that asks for it explicitly.

**Tables.** `django_tables2/bootstrap5.html` is the single table shell.
`bootstrap.html`, `bootstrap4.html` and `table.html` all extend it, so tables
that name an old path — or name none at all — get the same treatment.

## 6. File map

| Path | Role |
|---|---|
| `static/css/redesign.css` | Tokens + component library |
| `static/css/bs4-compat.css` | Legacy class + icon compatibility |
| `static/css/base.css` | Older page-specific rules (kept, de-conflicted) |
| `static/js/redesign.js` | Attribute shim, shell, wizard, tables, theme |
| `templates/base.html` | Application shell |
| `templates/_sidebar_links.html` | Primary navigation |
| `templates/django_tables2/bootstrap5.html` | Shared table shell |
| `templates/account/base.html` | Auth card shell |
