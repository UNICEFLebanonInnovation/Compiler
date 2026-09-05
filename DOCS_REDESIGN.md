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
| Action | `--brand-action #0077B0` — every surface that carries white text (filled buttons, active pager, checked controls, current wizard step). UNICEF blue itself is 3.28:1 with white and stays an accent. |
| Surfaces | `--surface-body / -raised / -sunken / -hover` |
| Text | `--text-primary / -secondary / -muted` (muted is 5.45:1 on white) |
| Focus | `--focus-ring` is a two-tone ring (surface gap + `--focus-ring-color`) so it reads on white, cards and filled buttons |
| Radius | `--radius-xs` → `--radius-xl`, `--radius-pill` |
| Elevation | `--shadow-xs` → `--shadow-xl` |
| Motion | `--duration-fast/base/slow`, `--ease-out`, `--ease-in-out` |
| Layout | `--sidebar-width`, `--header-height`, `--content-gutter` |

**Dark theme.** Opt-in via the topbar toggle, which sets `data-theme="dark"` on
`<html>` and persists the choice in `localStorage`. Only the tokens are
redefined, so components need no dark-specific rules. Bootstrap's few
hardcoded greys (breadcrumbs) are re-bound to tokens.

**Reduced motion.** `prefers-reduced-motion` collapses every duration to ~0.

**Type scale.** 16px body with a 13px (`.8125rem`) floor on every secondary
size; `small`/`.small` and `.badge` carry the same floor. Tables sit at 14px
for column density. Section titles, table headers, chips and legends are
sentence case — no `text-transform: uppercase` anywhere in the system, since
all-caps at small sizes is the hardest text for low-literacy readers.

**Targets.** Topbar actions are 44px; form controls, buttons and pager links
40px, rising to 44px under `(pointer: coarse)`; small icon controls (chip ×,
chart/table toggle, Clear all) get an invisible 44px hit area via `::before`.

## 3. Components

Provided by `redesign.css`: `.page-header`, `.card` / `.card-interactive`,
`.metric-card` + `.metric-icon/value/label/trend`, `.quick-action-tile`,
`.stepper` and `.wizard-progress`, `.table-container` + `.table-toolbar`,
`.filter-chip`, `.filter-group` (dashboard checkbox filters), `.status-pill`,
`.empty-state`, `.skeleton`, `.timeline`, `.profile-header`, `.auth-shell` /
`.auth-card`, `.form-section`, `.form-actions-sticky`, `.form-error-summary` +
`.field-error-message` (validation).

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

Forms that carry both `#next-page` (the module script's validating button)
and `#next-btn22` show only the first; the driver hides the second and still
uses it as the advance target. Both are labelled "Continue". A multi-step
form with no buttons at all (SmartWizard used to draw its own toolbar; the
TLS and Makani `main_form.html` templates relied on it) gets a Previous /
Continue row from the driver, with the same ids so the module validation
still applies. The driver's click listener is registered one task after
DOMContentLoaded, not on window `load`, so a slow third-party script cannot
leave Continue dead.

**Two jQueries.** 115 page templates load `jquery-1.12.3.min.js` again in
their own script block, after the shell's jQuery 3.7 and the Bootstrap
bundle. That replaces `$` with a copy that has no Bootstrap methods, so the
module scripts' `$('#formErrorModal').modal('show')` threw and validation
died there. `redesign.js` re-attaches Bootstrap 5's jQuery interface to
whichever jQuery is current (`bridgeJQueryPlugins`, at DOMContentLoaded and
at load), leaving jQuery UI's `button` and `tooltip` alone. The page scripts'
`$(window).load(fn)` (a jQuery 1.x form) became `$(window).on('load', fn)`
so they run under either version.

**Row action menus.** Dropdown toggles inside `.table-responsive` get
Popper's `fixed` strategy (`data-bs-popper-config`, set in `initTables`) so
the menu can escape the container's overflow clip; `redesign.css` overrides
the legacy `position: absolute !important` in base.css for those menus.

**Form errors.** The module scripts validate a step by adding `.error-field`
to each empty required control and opening `#formErrorModal`. `redesign.js`
intercepts that modal's `show.bs.modal` whenever fields are marked and renders
the errors in place instead: a message under each field (`aria-describedby`
wired), a summary above the form that links to each field and opens the step
that holds it, and a count on the wizard step. The modal still opens for
callers that mark no field. Server-side errors render the same summary from
`base.html` (`form.errors`). Public API: `BMA.formErrors.show / refresh /
mark / clear`.

**Filter labels.** Every module's `PlaceholderFilterSet` used to blank the
field label and use the placeholder or empty `<option>` as the field's name.
`student_registration/filter_labels.py` restores a visible label on every
control (the empty option becomes "All"); it is the one place to change how
filter forms are labelled.

**Filter drawer.** Filters no longer sit above the results. Every list page
and both dashboards keep one slim row in the flow, the filter bar (a
Filters button with the applied count, the applied filters as removable
chips, Clear all), and the form itself lives in a Bootstrap offcanvas
drawer (`.filter-drawer`, `offcanvas-end`, 28rem, fixed over the page) that
the button opens. Inside the drawer the form is one field per row and the
action row is sticky at the bottom. `_list_filters.html` renders both for
the crispy-based list pages; the eighteen older lists (schools, CLM, ALP,
enrolments, staff) carry the same markup inline around their own
django-bootstrap5 form, now in the vertical layout so labels are visible;
the dashboards' drawer has no backdrop and leaves the page scrollable so the
charts can be watched while values are ticked.

**Dashboard filters.** `mscc/_dashboard_filter_group.html` renders one
dimension as a checkbox `<fieldset>` (search box above eight values, count in
the legend). `mscc-dashboard.js` reads checked values; parameter names are
unchanged, so `DashboardDataView` needed no change.

**Language.** `USE_I18N` is on with `en` and `ar`. The topbar and the sign-in
card post to `set_language`; `student_registration.language_middleware`
activates only the language the user chose (cookie) and otherwise the default,
deliberately ignoring `Accept-Language` while the Arabic catalogue is partial
(~67 % translated). Swap it for Django's `LocaleMiddleware` once translations
are complete. `static/locale/ar/LC_MESSAGES/django.mo` is committed because
the Docker image has no `gettext`; re-run `compilemessages` (or `polib`) after
editing the `.po`.

**Drafts and data safety.** Answers on the wizard forms (any POST form that
contains `[id^="step-"]`, or one marked `data-draft`) are saved to
`localStorage` as the user types, minus passwords, files and the CSRF token,
keyed by path. On return a banner offers to bring them back; a submit that no
script prevented clears them; leaving the page with unsaved answers asks
first, and so does any Reset button (the wizard's `#reset-btn22` had no
handler at all and now resets after the same question). Opt a form out with
`data-no-draft`. API: `BMA.drafts.save / load / clear`.

**Required and optional.** Wizard forms open with "All fields are required
unless marked (optional)", and CSS appends "(optional)" to any wizard label
that is neither `.requiredField` nor followed by a `required` control.

**Long selects.** A wizard `<select>` with twelve or more options (or any
select carrying `data-searchable`) gets a "type to shorten the list" box
above it; the select keeps its id, name, value and change events.

**Button colours.** `btn-info` now carries the primary look. Cancel, Reset,
Close and Back buttons coloured `btn-warning`/`btn-info` are switched to
`btn-outline-secondary` at load; attendance state toggles keep their colours.

**Tables on phones.** `django_tables2/bootstrap5.html` marks tables
`table-stackable` and puts each column header in `data-label`. Below 768px a
row becomes a card with a label beside each value; from 768px up, a table
that overflows its container gets `.has-scroll` from `redesign.js` and its
first column stays pinned (skipped when that column holds a dropdown).

**Wizard step height.** `base.css` pins `#step-1..4` to 400px, which only
worked inside SmartWizard's scrolling container; `redesign.css` lets steps
take their natural height.

**Page headers.** Every page now uses the one `.page-header` shape
(`.page-header-titles` with breadcrumb nav, `h1.page-header-title` and an
optional `p.page-header-subtitle`, then `.page-header-actions`). The 79
ArchitectUI `.app-page-title` blocks were rewritten mechanically; the ten
list pages whose title was the signed-in user's name got a real title
("Schools", "Teachers") with the user line moved to the subtitle. Each page
has exactly one h1. `.app-page-title` styling stays in the compatibility
layer for anything added later from an old copy.

**Idle logout.** `AutoLogout` (production: 30 minutes without a request)
used to end a session silently. `base.html` passes the cutoff and the URLs
for `session_ping` and sign-in on the body element; `redesign.js` pings
while the user is active so a long form never times out mid-way, shows a
countdown banner with "Stay signed in" for the last two minutes, and on
expiry goes to the sign-in page with `next=` set. The ping is excluded from
the user-activity log. Set `AUTO_LOGOUT_DELAY = 0` to turn the timer off.

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
| `static/js/redesign.js` | Attribute shim, shell, wizard, form errors, tables, theme |
| `static/js/dashboard/` | D3 chart plugin and the dashboard controllers |
| `static/locale/ar/` | Arabic catalogue (`.po` source, compiled `.mo`) |
| `filter_labels.py` | Visible labels for the list-page filter forms |
| `language_middleware.py` | Interface language from the user's choice only |
| `templates/base.html` | Application shell, error summary, language menu |
| `templates/_sidebar_links.html` | Primary navigation |
| `templates/_list_filters.html` | Shared filter panel + active-filter chips |
| `templates/mscc/_dashboard_filter_group.html` | Checkbox filter group |
| `templates/django_tables2/bootstrap5.html` | Shared table shell |
| `templates/account/base.html` | Auth card shell |
