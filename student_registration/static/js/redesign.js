/* ==========================================================================
   BMA Compiler — Redesign interaction layer
   --------------------------------------------------------------------------
   Responsibilities:
     1. Bridge legacy Bootstrap 4 markup (data-toggle/dismiss/target) onto the
        Bootstrap 5 JS API, so page templates keep working untouched.
     2. Shell behaviour: sidebar collapse, theme toggle, nav auto-highlight.
     3. Component bootstrapping: tooltips, popovers, toasts.
     4. Table & form ergonomics: sticky-header sizing, submit overlay,
        client validation feedback, filter chips.

   Depends on: bootstrap.bundle (global `bootstrap`). jQuery is optional.
   ========================================================================== */

(function () {
    'use strict';

    var STORAGE_SIDEBAR = 'bma.sidebar.collapsed';
    var STORAGE_THEME = 'bma.theme';

    /* ---------------------------------------------------------------------
       Small helpers
       --------------------------------------------------------------------- */

    function $all(selector, root) {
        return Array.prototype.slice.call((root || document).querySelectorAll(selector));
    }

    function store(key, value) {
        try {
            window.localStorage.setItem(key, value);
        } catch (e) {
            /* private mode / disabled storage — non-fatal */
        }
    }

    function read(key) {
        try {
            return window.localStorage.getItem(key);
        } catch (e) {
            return null;
        }
    }

    /* ---------------------------------------------------------------------
       1. Bootstrap 4 -> Bootstrap 5 data attribute shim
       ---------------------------------------------------------------------
       Bootstrap 5 namespaced every behaviour attribute (`data-toggle` became
       `data-bs-toggle`). Roughly 50 legacy templates still use the old names;
       rather than editing each one, mirror the attributes at load time.
       --------------------------------------------------------------------- */

    var ATTRIBUTE_MAP = [
        ['data-toggle', 'data-bs-toggle'],
        ['data-dismiss', 'data-bs-dismiss'],
        ['data-target', 'data-bs-target'],
        ['data-parent', 'data-bs-parent'],
        ['data-placement', 'data-bs-placement'],
        ['data-content', 'data-bs-content'],
        ['data-trigger', 'data-bs-trigger'],
        ['data-offset', 'data-bs-offset'],
        ['data-backdrop', 'data-bs-backdrop'],
        ['data-keyboard', 'data-bs-keyboard'],
        ['data-slide', 'data-bs-slide'],
        ['data-slide-to', 'data-bs-slide-to'],
        ['data-ride', 'data-bs-ride'],
        ['data-interval', 'data-bs-interval'],
        ['data-spy', 'data-bs-spy'],
        ['data-delay', 'data-bs-delay'],
        ['data-html', 'data-bs-html'],
        ['data-animation', 'data-bs-animation'],
        ['data-boundary', 'data-bs-boundary'],
        ['data-display', 'data-bs-display'],
        ['data-autohide', 'data-bs-autohide']
    ];

    // `data-toggle` values BS5 still understands. Anything else (e.g. the
    // legacy theme's "popover-custom") is left alone for its own handler.
    var KNOWN_TOGGLES = [
        'modal', 'dropdown', 'tab', 'pill', 'collapse', 'tooltip',
        'popover', 'offcanvas', 'button', 'list'
    ];

    function upgradeAttributes(root) {
        ATTRIBUTE_MAP.forEach(function (pair) {
            var legacy = pair[0];
            var modern = pair[1];

            $all('[' + legacy + ']', root).forEach(function (el) {
                if (el.hasAttribute(modern)) {
                    return; // already migrated or authored for BS5
                }

                var value = el.getAttribute(legacy);

                if (legacy === 'data-toggle' && KNOWN_TOGGLES.indexOf(value) === -1) {
                    return; // custom toggle — not ours to translate
                }

                el.setAttribute(modern, value);
            });
        });

        // BS4's `.close` button relies on the dismiss attribute we just
        // mirrored; give it the BS5 visual treatment where it is safe to do so
        // (i.e. when the button has no other content beyond the × glyph).
        $all('button.close', root).forEach(function (el) {
            if (el.dataset.rdCloseUpgraded) {
                return;
            }
            el.dataset.rdCloseUpgraded = '1';
            if (!el.getAttribute('aria-label')) {
                el.setAttribute('aria-label', 'Close');
            }
        });
    }

    /* ---------------------------------------------------------------------
       2. Component bootstrapping
       --------------------------------------------------------------------- */

    function initComponents(root) {
        if (typeof window.bootstrap === 'undefined') {
            return;
        }

        $all('[data-bs-toggle="tooltip"]', root).forEach(function (el) {
            if (!bootstrap.Tooltip.getInstance(el)) {
                new bootstrap.Tooltip(el, { container: 'body' });
            }
        });

        $all('[data-bs-toggle="popover"]', root).forEach(function (el) {
            if (!bootstrap.Popover.getInstance(el)) {
                new bootstrap.Popover(el, { container: 'body', html: true });
            }
        });
    }

    /* ---------------------------------------------------------------------
       3. Sidebar
       --------------------------------------------------------------------- */

    function initSidebar() {
        var sidebar = document.querySelector('.sidebar');
        var toggle = document.getElementById('sidebarToggle');

        if (!sidebar) {
            return;
        }

        function syncIcon() {
            if (!toggle) {
                return;
            }
            var icon = toggle.querySelector('i');
            if (!icon) {
                return;
            }
            var collapsed = sidebar.classList.contains('collapsed');
            icon.classList.toggle('bi-list', !collapsed);
            icon.classList.toggle('bi-text-indent-left', collapsed);
            toggle.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
        }

        if (read(STORAGE_SIDEBAR) === 'true') {
            sidebar.classList.add('collapsed');
        }
        syncIcon();

        if (toggle) {
            toggle.addEventListener('click', function () {
                sidebar.classList.toggle('collapsed');
                store(STORAGE_SIDEBAR, sidebar.classList.contains('collapsed') ? 'true' : 'false');
                syncIcon();
            });
        }

        // Keep the active nav item in view on load — long menus otherwise open
        // scrolled to the top with the current page out of sight.
        var active = sidebar.querySelector('.nav-link.active');
        if (active && typeof active.scrollIntoView === 'function') {
            var nav = sidebar.querySelector('.sidebar-nav');
            if (nav && active.offsetTop > nav.clientHeight) {
                active.scrollIntoView({ block: 'center' });
            }
        }
    }

    /* ---------------------------------------------------------------------
       4. Theme
       --------------------------------------------------------------------- */

    function applyTheme(theme) {
        var root = document.documentElement;

        if (theme === 'dark') {
            root.setAttribute('data-theme', 'dark');
            // Bootstrap 5.3 keys its own dark palette off `data-bs-theme`.
            // Setting it too means its components (form-select chevrons,
            // dropdowns, close buttons, modals) darken natively instead of
            // needing a per-component override here.
            root.setAttribute('data-bs-theme', 'dark');
        } else {
            root.removeAttribute('data-theme');
            root.removeAttribute('data-bs-theme');
        }

        $all('[data-theme-toggle] i').forEach(function (icon) {
            icon.classList.toggle('bi-moon-stars', theme !== 'dark');
            icon.classList.toggle('bi-sun', theme === 'dark');
        });
    }

    function initTheme() {
        applyTheme(read(STORAGE_THEME) === 'dark' ? 'dark' : 'light');

        $all('[data-theme-toggle]').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
                store(STORAGE_THEME, next);
                applyTheme(next);
            });
        });
    }

    /* ---------------------------------------------------------------------
       5. Forms
       --------------------------------------------------------------------- */

    function initForms() {
        var overlay = document.getElementById('loading-overlay');

        document.addEventListener('submit', function (e) {
            var form = e.target;

            if (!(form instanceof HTMLFormElement) || form.classList.contains('no-overlay')) {
                return;
            }

            // Never cover the screen for a form the browser has already
            // rejected — the user needs to see the invalid field.
            if (typeof form.checkValidity === 'function' && !form.noValidate && !form.checkValidity()) {
                return;
            }

            if (overlay) {
                overlay.style.display = 'flex';
            }

            // Guard against double submission of long-running exports.
            $all('button[type="submit"], input[type="submit"]', form).forEach(function (btn) {
                setTimeout(function () {
                    btn.disabled = true;
                    btn.classList.add('disabled');
                }, 0);
            });
        }, true);

        // Hide the overlay if the user navigates back to a cached page.
        window.addEventListener('pageshow', function (event) {
            if (event.persisted && overlay) {
                overlay.style.display = 'none';
                $all('button[type="submit"].disabled, input[type="submit"].disabled').forEach(function (btn) {
                    btn.disabled = false;
                    btn.classList.remove('disabled');
                });
            }
        });

        // Reveal the first invalid field on a server-rendered error page.
        var firstError = document.querySelector('.is-invalid, .has-error, .invalid-feedback');
        if (firstError && !document.querySelector('.step-content:not(.d-none)')) {
            var card = firstError.closest('.card, .form-section');
            if (card && typeof card.scrollIntoView === 'function') {
                card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }

        // Mobile keyboards: phone fields get the dial pad and numeric fields
        // the number pad. With 200+ form fields, the name is the reliable cue.
        $all('input[type="text"]:not([inputmode]), input[type="tel"]:not([inputmode])').forEach(function (input) {
            if (/phone|mobile|whatsapp|\btel\b/i.test((input.name || '') + ' ' + (input.id || ''))) {
                input.setAttribute('inputmode', 'tel');
            }
        });
        $all('input[type="number"]:not([inputmode])').forEach(function (input) {
            var step = input.getAttribute('step') || '';
            input.setAttribute('inputmode', step === 'any' || step.indexOf('.') !== -1 ? 'decimal' : 'numeric');
        });

        // Password visibility toggles on the auth screens.
        $all('[data-password-toggle]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var input = document.getElementById(btn.getAttribute('data-password-toggle'));
                if (!input) {
                    return;
                }
                var showing = input.getAttribute('type') === 'text';
                input.setAttribute('type', showing ? 'password' : 'text');
                var icon = btn.querySelector('i');
                if (icon) {
                    icon.classList.toggle('bi-eye', showing);
                    icon.classList.toggle('bi-eye-slash', !showing);
                }
                btn.setAttribute('aria-label', showing ? 'Show password' : 'Hide password');
            });
        });
    }

    /* ---------------------------------------------------------------------
       6. Tables
       --------------------------------------------------------------------- */

    function initTables() {
        // django-tables2 renders plain tables; add the interaction classes the
        // design system expects without touching every table definition.
        $all('table.table').forEach(function (table) {
            table.classList.add('table-hover', 'align-middle');

            // Wrapping happens before jQuery's ready handlers fire (this file
            // is loaded ahead of the page scripts), so plugins initialise
            // against the final DOM. Tables already managed by DataTables or
            // an existing scroll container are left alone.
            if (table.closest('.table-responsive, .dataTables_wrapper') ||
                table.classList.contains('dataTable')) {
                return;
            }

            var wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        });

        // Row action menus live inside a scrolling container (overflow: auto
        // with a max-height), which clips an absolutely positioned menu at
        // the container's edge: on the last rows only the first item or two
        // could be reached. Positioning the menu with Popper's fixed strategy
        // lets it escape the container.
        $all('.table-responsive [data-bs-toggle="dropdown"]').forEach(function (toggle) {
            if (!toggle.hasAttribute('data-bs-popper-config')) {
                toggle.setAttribute('data-bs-popper-config', '{"strategy":"fixed"}');
            }
        });

        // Wide grids: flag the scroll containers that actually overflow, so
        // the CSS can pin the first column. Skipped when that column holds a
        // dropdown, which a sticky cell's stacking context would trap.
        function markOverflow(wrapper) {
            var table = wrapper.querySelector('table');
            var trapsMenu = table && table.querySelector('tbody tr td:first-child .dropdown');
            wrapper.classList.toggle('has-scroll',
                Boolean(table) && !trapsMenu && wrapper.scrollWidth > wrapper.clientWidth + 1);
        }

        var wrappers = $all('.table-responsive');
        wrappers.forEach(markOverflow);
        if ('ResizeObserver' in window && wrappers.length) {
            var ro = new ResizeObserver(function (entries) {
                entries.forEach(function (entry) { markOverflow(entry.target); });
            });
            wrappers.forEach(function (wrapper) { ro.observe(wrapper); });
        }

        // Row-level click-through: any row exposing data-href behaves like a
        // link, except when the click landed on a control inside it.
        document.addEventListener('click', function (e) {
            var row = e.target.closest ? e.target.closest('tr[data-href]') : null;
            if (!row) {
                return;
            }
            if (e.target.closest('a, button, input, select, label, .dropdown')) {
                return;
            }
            window.location.href = row.getAttribute('data-href');
        });
    }

    /* ---------------------------------------------------------------------
       7. Legacy radio button groups
       ---------------------------------------------------------------------
       Bootstrap 4's data-toggle="buttons" is gone in 5. The attendance screens
       rely on it for their Attended/Absent and Working day/Day off controls.
       The nested radio still works natively, so only the `.active` class needs
       maintaining — CSS :has() covers current browsers, this covers the rest.
       --------------------------------------------------------------------- */

    function syncButtonGroup(group) {
        $all('label.btn', group).forEach(function (label) {
            var input = label.querySelector('input[type="radio"], input[type="checkbox"]');
            label.classList.toggle('active', !!(input && input.checked));
        });
    }

    function initButtonGroups() {
        $all('.btn-group-toggle').forEach(syncButtonGroup);

        document.addEventListener('change', function (e) {
            var group = e.target.closest ? e.target.closest('.btn-group-toggle') : null;
            if (!group) {
                return;
            }

            // Radios share a name across groups, so re-sync every group that
            // could hold a member of the same radio group.
            if (e.target.type === 'radio' && e.target.name) {
                $all('input[name="' + CSS.escape(e.target.name) + '"]').forEach(function (input) {
                    var owner = input.closest('.btn-group-toggle');
                    if (owner) {
                        syncButtonGroup(owner);
                    }
                });
            } else {
                syncButtonGroup(group);
            }
        });
    }

    /* ---------------------------------------------------------------------
       8. Filter chips
       --------------------------------------------------------------------- */

    /* The FilterSets blank out every field label and rely on placeholders and
       empty select options instead (see PlaceholderFilterSet). That leaves the
       controls with no accessible name at all, so mirror the visible text into
       aria-label — a placeholder is not a label, and it disappears on input. */
    function labelFilterControls() {
        $all('.form-inline select, .form-inline input, .form-inline textarea').forEach(function (el) {
            if (el.type === 'hidden' || el.type === 'submit' || el.type === 'button') {
                return;
            }
            if (el.getAttribute('aria-label') || (el.labels && el.labels.length)) {
                return;
            }

            var text = el.getAttribute('placeholder');

            if (!text && el.tagName === 'SELECT' && el.options.length) {
                var first = el.options[0];
                if (first.value === '') {
                    text = first.textContent.trim();
                }
            }

            if (!text && el.name) {
                text = el.name.replace(/__/g, ' ').replace(/_/g, ' ').trim();
            }

            if (text) {
                el.setAttribute('aria-label', text);
            }
        });
    }

    function initFilterChips() {
        labelFilterControls();

        document.addEventListener('click', function (e) {
            var chip = e.target.closest ? e.target.closest('[data-remove-filter]') : null;
            if (!chip) {
                return;
            }
            e.preventDefault();

            var param = chip.getAttribute('data-remove-filter');
            var url = new URL(window.location.href);
            url.searchParams.delete(param);
            url.searchParams.delete('page');
            window.location.href = url.toString();
        });
    }

    /* ---------------------------------------------------------------------
       9. Multi-step form wizard
       ---------------------------------------------------------------------
       The registration and service forms are laid out as
           <div id="smartwizard(3)">
             <ul class="forms-wizard"><li><a href="#step-N">…</a></li></ul>
             <div class="form-wizard-content"> … <div id="step-N"> … </div>
           </div>
       with Next/Previous controls carrying the ids below. Step advancement
       used to come from the ArchitectUI vendor bundle; this is a direct,
       dependency-free replacement that preserves the same contract.

       Per-module scripts (mscc.js, tls.js, youth.js) validate the current step
       on "#next-btn22" and call preventDefault() when a required field is
       empty, so this driver only advances on a click that survived that check.
       --------------------------------------------------------------------- */

    var wizards = [];

    function collectSteps(content) {
        return $all('[id]', content).filter(function (el) {
            return /^step-\d+$/.test(el.id);
        }).sort(function (a, b) {
            return parseInt(a.id.slice(5), 10) - parseInt(b.id.slice(5), 10);
        });
    }

    function Wizard(content) {
        this.content = content;
        this.root = content.parentElement;
        this.steps = collectSteps(content);
        this.nav = this.root ? this.root.querySelector('ul.forms-wizard') : null;
        this.navItems = this.nav ? $all(':scope > li', this.nav) : [];
        this.index = 0;

        var scope = content.closest('.card, .main-card, form') || document;
        this.nextBtn = scope.querySelector('#next-btn22') || document.getElementById('next-btn22');
        this.prevBtn = scope.querySelector('#prev-btn22') || document.getElementById('prev-btn22');
        this.progress = null;

        // Several forms carry two "next" buttons: #next-page runs the module
        // script's per-step validation and then triggers #next-btn22, which
        // is the one this driver advances on. Showing both meant two
        // identical-looking buttons side by side, so only one is visible;
        // the hidden one is still reachable programmatically.
        this.nextPage = scope.querySelector('#next-page') || document.getElementById('next-page');
        if (this.nextPage && this.nextBtn) {
            this.nextBtn.classList.add('d-none');
            this.nextBtn.setAttribute('aria-hidden', 'true');
            this.nextBtn.tabIndex = -1;
        }
        this.visibleNext = this.nextPage || this.nextBtn;

        // SmartWizard drew its own Previous / Next toolbar, so several
        // multi-step forms (the TLS registration among them) carry no
        // buttons of their own in the template. Without them the steps were
        // unreachable. The driver supplies the pair, with the ids the module
        // scripts validate on, right under the steps.
        if (this.steps.length > 1 && !this.visibleNext) {
            var actions = document.createElement('div');
            actions.className = 'wizard-actions';
            if (!this.prevBtn) {
                this.prevBtn = document.createElement('button');
                this.prevBtn.type = 'button';
                this.prevBtn.id = 'prev-btn22';
                this.prevBtn.className = 'btn btn-outline-secondary btn-icon';
                this.prevBtn.innerHTML = '<i class="bi bi-arrow-left" aria-hidden="true"></i>Previous';
                actions.appendChild(this.prevBtn);
            }
            this.nextBtn = document.createElement('button');
            this.nextBtn.type = 'button';
            this.nextBtn.id = 'next-btn22';
            this.nextBtn.className = 'btn btn-primary btn-icon';
            this.nextBtn.innerHTML = 'Continue<i class="bi bi-arrow-right" aria-hidden="true"></i>';
            actions.appendChild(this.nextBtn);
            this.visibleNext = this.nextBtn;
            content.parentNode.insertBefore(actions, content.nextSibling);
        }

        if (this.steps.length > 1) {
            var bar = document.createElement('div');
            bar.className = 'wizard-progress';
            bar.innerHTML = '<div class="wizard-progress-bar"></div>';
            if (this.nav && this.nav.parentNode) {
                this.nav.parentNode.insertBefore(bar, this.nav.nextSibling);
            }
            this.progress = bar.firstChild;
        }

        // Required fields carry an asterisk; say so once in words, and mark
        // the rest "(optional)" (CSS) so nobody has to decode the symbol.
        if (content.parentNode && (content.querySelector('.requiredField, [required]'))) {
            var note = document.createElement('p');
            note.className = 'form-required-note';
            note.textContent = 'All fields are required unless marked (optional).';
            content.parentNode.insertBefore(note, content);
        }
    }

    Wizard.prototype.go = function (index, options) {
        if (index < 0 || index >= this.steps.length) {
            return;
        }

        this.index = index;

        this.steps.forEach(function (step, i) {
            // Inline styles are required: base.css hides #step-2..4 with a
            // stylesheet rule that a class toggle would not override.
            step.style.display = i === index ? 'block' : 'none';
        });

        this.navItems.forEach(function (item, i) {
            item.classList.toggle('form-wizard-step-done', i < index);
            item.classList.toggle('form-wizard-step-doing', i === index);
            item.classList.toggle('active', i === index);
        });

        if (this.progress) {
            var pct = this.steps.length > 1 ? (index / (this.steps.length - 1)) * 100 : 100;
            this.progress.style.width = pct + '%';
        }

        if (this.prevBtn) {
            this.prevBtn.classList.toggle('d-none', index === 0);
        }
        if (this.visibleNext) {
            this.visibleNext.classList.toggle('d-none', index >= this.steps.length - 1);
        }

        if (!options || options.scroll !== false) {
            var top = this.content.getBoundingClientRect().top + window.pageYOffset - 90;
            window.scrollTo({ top: Math.max(top, 0), behavior: 'smooth' });
        }
    };

    Wizard.prototype.next = function () { this.go(this.index + 1); };
    Wizard.prototype.prev = function () { this.go(this.index - 1); };

    function activeWizard() {
        return wizards.length ? wizards[0] : null;
    }

    function initWizards() {
        $all('.form-wizard-content').forEach(function (content) {
            var wizard = new Wizard(content);
            if (!wizard.steps.length) {
                return;
            }
            wizards.push(wizard);
            wizard.go(0, { scroll: false });

            wizard.navItems.forEach(function (item, i) {
                var anchor = item.querySelector('a[href^="#step-"]');
                if (!anchor) {
                    return;
                }
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    // Moving backwards is always safe; moving forwards goes
                    // through the Next button so per-step validation still runs.
                    if (i <= wizard.index) {
                        wizard.go(i);
                    } else if (wizard.visibleNext && i === wizard.index + 1) {
                        wizard.visibleNext.click();
                    }
                });
            });
        });

        if (!wizards.length) {
            return;
        }

        // Registered one task later than boot so it lands after the module
        // scripts' jQuery handlers (jQuery dispatches ready via setTimeout),
        // letting us honour a preventDefault() from their validation. It used
        // to wait for window `load`, which a slow third-party script could
        // hold back for many seconds, leaving Continue dead meanwhile.
        setTimeout(function () {
            document.addEventListener('click', function (e) {
                if (!e.target.closest) {
                    return;
                }

                var wizard = activeWizard();
                if (!wizard) {
                    return;
                }

                if (e.target.closest('#next-btn22')) {
                    if (!e.defaultPrevented) {
                        wizard.next();
                    }
                    return;
                }

                if (e.target.closest('#prev-btn22')) {
                    e.preventDefault();
                    wizard.prev();
                }
            });
        });
    }

    /* ---------------------------------------------------------------------
       9b. Form errors — a message at the field and a summary that links to it

       The module scripts (mscc.js, tls.js, youth.js, general.js) validate a
       step by adding .error-field to each empty required control and then
       opening #formErrorModal, which only says "check the mandatory
       fields". The modal's show event is intercepted here whenever fields
       are marked, and the errors are rendered where the user can act on
       them instead: a message under each field, a summary above the form
       that links to each one, and a count on the wizard step that holds
       them. The modal still opens for callers that mark no field.
       --------------------------------------------------------------------- */

    var ERROR_MARK = '.error-field, .is-invalid';
    var ERROR_TEXT = {
        required: 'This field is required',
        one: 'One answer is missing',
        many: '{n} answers are missing',
        hint: 'Fill in the fields listed here, then press Continue or Save again.',
        step: 'Step {n}'
    };

    function isControl(el) {
        return /^(INPUT|SELECT|TEXTAREA)$/.test(el.tagName) && el.type !== 'hidden';
    }

    function fieldName(field) {
        var text = '';
        if (field.labels && field.labels.length) {
            text = field.labels[0].textContent;
        }
        if (!text && field.id) {
            var label = document.querySelector('label[for="' + field.id + '"]');
            text = label ? label.textContent : '';
        }
        if (!text) {
            text = field.getAttribute('aria-label') || field.getAttribute('placeholder') || field.name || '';
        }
        return text.replace(/\*/g, '').replace(/\s+/g, ' ').trim();
    }

    function errorAnchor(field) {
        var anchor = field.closest('.input-group') || field;
        var next = anchor.nextElementSibling;
        // Enhanced selects render their visible widget as the next sibling.
        if (next && (next.classList.contains('select2') || next.classList.contains('combobox-container'))) {
            anchor = next;
        }
        return anchor;
    }

    function errorNoteId(field) {
        return (field.id || field.name || 'field') + '-error';
    }

    function markField(field, message) {
        field.classList.add('is-invalid');
        field.setAttribute('aria-invalid', 'true');

        var id = errorNoteId(field);
        var note = document.getElementById(id);
        if (!note) {
            note = document.createElement('div');
            note.id = id;
            note.className = 'field-error-message';
            var anchor = errorAnchor(field);
            anchor.parentNode.insertBefore(note, anchor.nextSibling);
        }
        note.innerHTML = '<i class="bi bi-exclamation-circle-fill" aria-hidden="true"></i> ';
        note.appendChild(document.createTextNode(message || ERROR_TEXT.required));

        var described = (field.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
        if (described.indexOf(id) === -1) {
            described.push(id);
            field.setAttribute('aria-describedby', described.join(' '));
        }
    }

    function clearField(field) {
        field.classList.remove('is-invalid', 'error-field');
        field.removeAttribute('aria-invalid');

        var id = errorNoteId(field);
        var note = document.getElementById(id);
        if (note) {
            note.remove();
        }
        var described = (field.getAttribute('aria-describedby') || '').split(/\s+/).filter(function (d) {
            return d && d !== id;
        });
        if (described.length) {
            field.setAttribute('aria-describedby', described.join(' '));
        } else {
            field.removeAttribute('aria-describedby');
        }
    }

    function stepOf(field) {
        var wizard = activeWizard();
        var step = field.closest('[id^="step-"]');
        return wizard && step ? wizard.steps.indexOf(step) : -1;
    }

    function decorateSteps(fields) {
        var wizard = activeWizard();
        if (!wizard) {
            return;
        }
        wizard.navItems.forEach(function (item, i) {
            var count = fields.filter(function (f) { return stepOf(f) === i; }).length;
            var badge = item.querySelector('.wizard-step-errors');
            item.classList.toggle('has-error', count > 0);
            if (!count) {
                if (badge) {
                    badge.remove();
                }
                return;
            }
            if (!badge) {
                badge = document.createElement('span');
                badge.className = 'wizard-step-errors';
                item.appendChild(badge);
            }
            badge.textContent = count;
            badge.setAttribute('title', count + ' missing');
        });
    }

    function summaryElement(form, create) {
        var summary = document.getElementById('form-error-summary') ||
            (form && form.querySelector('.form-error-summary'));
        if (summary || !create) {
            return summary;
        }

        summary = document.createElement('div');
        summary.id = 'form-error-summary';
        summary.className = 'form-error-summary';
        summary.setAttribute('role', 'alert');
        summary.setAttribute('tabindex', '-1');
        summary.innerHTML =
            '<h2 class="form-error-summary-title">' +
            '<i class="bi bi-exclamation-circle-fill" aria-hidden="true"></i> <span></span></h2>' +
            '<p class="form-error-summary-hint"></p>' +
            '<ul class="form-error-summary-list"></ul>';

        var wizard = activeWizard();
        if (wizard && wizard.content.parentNode) {
            // Above the steps, so it stays in view whichever step is open.
            wizard.content.parentNode.insertBefore(summary, wizard.content);
        } else {
            form.insertBefore(summary, form.firstChild);
        }
        return summary;
    }

    function renderSummary(form, fields, options) {
        var summary = summaryElement(form, true);
        var wizard = activeWizard();

        summary.querySelector('.form-error-summary-title span').textContent =
            fields.length === 1 ? ERROR_TEXT.one : ERROR_TEXT.many.replace('{n}', fields.length);
        summary.querySelector('.form-error-summary-hint').textContent = ERROR_TEXT.hint;

        var list = summary.querySelector('.form-error-summary-list');
        list.innerHTML = '';
        fields.forEach(function (field) {
            var item = document.createElement('li');
            var link = document.createElement('a');
            link.href = '#' + field.id;
            link.textContent = fieldName(field) || field.name;
            item.appendChild(link);

            var step = stepOf(field);
            if (wizard && wizard.steps.length > 1 && step >= 0) {
                var where = document.createElement('span');
                where.className = 'form-error-summary-step';
                where.textContent = ' · ' + ERROR_TEXT.step.replace('{n}', step + 1);
                item.appendChild(where);
            }
            list.appendChild(item);
        });

        if (!options || options.focus !== false) {
            summary.focus();
        }
    }

    function showFormErrors(scope, options) {
        var fields = $all(ERROR_MARK, scope || document).filter(isControl);
        if (!fields.length) {
            return false;
        }
        var form = fields[0].closest('form') || document.body;
        fields.forEach(function (field) {
            markField(field);
        });
        decorateSteps(fields);
        renderSummary(form, fields, options);
        return true;
    }

    function refreshFormErrors(form) {
        var fields = $all(ERROR_MARK, form).filter(isControl);
        var summary = summaryElement(form, false);
        decorateSteps(fields);
        if (!fields.length) {
            if (summary) {
                summary.remove();
            }
        } else if (summary) {
            renderSummary(form, fields, { focus: false });
        }
    }

    function initFormErrors() {
        document.addEventListener('show.bs.modal', function (e) {
            if (e.target && e.target.id === 'formErrorModal' && showFormErrors(document)) {
                e.preventDefault();
            }
        });

        // A summary link opens the step that holds the field, then focuses it.
        document.addEventListener('click', function (e) {
            var link = e.target.closest ? e.target.closest('.form-error-summary a[href^="#"]') : null;
            if (!link) {
                return;
            }
            var target = document.getElementById(link.getAttribute('href').slice(1));
            if (!target) {
                return;
            }
            e.preventDefault();

            var wizard = activeWizard();
            var step = stepOf(target);
            if (wizard && step >= 0 && step !== wizard.index) {
                wizard.go(step, { scroll: false });
            }

            var focusTarget = target;
            if (target.classList.contains('select2-hidden-accessible') && target.nextElementSibling) {
                focusTarget = target.nextElementSibling.querySelector('.select2-selection') || target;
            }
            errorAnchor(target).scrollIntoView({ behavior: 'smooth', block: 'center' });
            focusTarget.focus({ preventScroll: true });
        });

        // Filling a field clears its message; the summary and counts follow.
        ['input', 'change'].forEach(function (type) {
            document.addEventListener(type, function (e) {
                var field = e.target;
                if (!field || !isControl(field) || field.value === '' || field.value == null) {
                    return;
                }
                if (!field.classList.contains('is-invalid') && !field.classList.contains('error-field')) {
                    return;
                }
                clearField(field);
                refreshFormErrors(field.closest('form') || document.body);
            });
        });

        // Server-rendered errors: the fields are already marked and the
        // summary already listed; add the step counts, open the step that
        // holds the first problem, and move focus so it is announced.
        var summary = document.getElementById('form-error-summary');
        if (summary) {
            var invalid = $all('.is-invalid').filter(isControl);
            decorateSteps(invalid);
            var wizard = activeWizard();
            var first = invalid.length ? stepOf(invalid[0]) : -1;
            if (wizard && first > 0) {
                wizard.go(first, { scroll: false });
            }
            summary.focus();
        }
    }

    /* ---------------------------------------------------------------------
       9c. Data safety — drafts, a leave warning and a reset confirmation

       A registration takes ten minutes on a bad connection. Answers on the
       wizard forms are saved to localStorage as the user types (never
       passwords, files or the CSRF token), offered back on return, and
       dropped once the form has really been submitted. Leaving the page
       with unsaved answers asks first, and so does Reset.
       --------------------------------------------------------------------- */

    var DRAFT_PREFIX = 'bma.draft:';
    var DRAFT_MAX_AGE = 7 * 24 * 60 * 60 * 1000;
    var DRAFT_TEXT = {
        title: 'You have unsaved answers on this form',
        hint: 'They were saved {when}. Bring them back, or start again.',
        restore: 'Bring back my answers',
        discard: 'Start again',
        restored: 'Your answers are back.',
        reset: 'Clear every answer on this form? This cannot be undone.'
    };

    function storage() {
        try {
            return window.localStorage;
        } catch (e) {
            return null;
        }
    }

    function draftForms() {
        return $all('form').filter(function (form) {
            if ((form.getAttribute('method') || 'get').toLowerCase() !== 'post') {
                return false;
            }
            if (form.hasAttribute('data-no-draft')) {
                return false;
            }
            return form.hasAttribute('data-draft') ||
                form.closest('.form-wizard-content') ||
                form.querySelector('.form-wizard-content, [id^="step-"]');
        });
    }

    function draftKey(form) {
        return DRAFT_PREFIX + location.pathname + (form.id ? '#' + form.id : '');
    }

    function draftFields(form) {
        return $all('input, select, textarea', form).filter(function (el) {
            if (!el.name || el.disabled || el.name === 'csrfmiddlewaretoken') {
                return false;
            }
            return !/^(hidden|password|file|submit|button|reset|image)$/.test(el.type);
        });
    }

    function readDraftValues(form) {
        var values = {};
        draftFields(form).forEach(function (el) {
            if (el.type === 'checkbox' || el.type === 'radio') {
                if (el.checked) {
                    (values[el.name] = values[el.name] || []).push(el.value);
                }
            } else if (el.multiple) {
                var picked = Array.prototype.map.call(el.selectedOptions, function (o) { return o.value; });
                if (picked.length) {
                    values[el.name] = picked;
                }
            } else if (el.value !== '') {
                values[el.name] = el.value;
            }
        });
        return values;
    }

    function fieldHasValue(el, value) {
        if (el.type === 'checkbox' || el.type === 'radio') {
            return el.checked === (value.indexOf(el.value) !== -1);
        }
        if (el.multiple) {
            return Array.prototype.every.call(el.options, function (o) {
                return o.selected === (value.indexOf(o.value) !== -1);
            });
        }
        return el.value === value;
    }

    function applyDraftValues(form, values) {
        draftFields(form).forEach(function (el) {
            if (!(el.name in values) || fieldHasValue(el, values[el.name])) {
                return;
            }
            var value = values[el.name];
            if (el.type === 'checkbox' || el.type === 'radio') {
                el.checked = value.indexOf(el.value) !== -1;
            } else if (el.multiple) {
                Array.prototype.forEach.call(el.options, function (o) {
                    o.selected = value.indexOf(o.value) !== -1;
                });
            } else {
                el.value = value;
            }
            el.dispatchEvent(new Event('change', { bubbles: true }));
        });
    }

    function canonical(values) {
        return JSON.stringify(Object.keys(values).sort().map(function (k) { return [k, values[k]]; }));
    }

    function saveDraft(form) {
        var store = storage();
        if (!store) {
            return;
        }
        var values = readDraftValues(form);
        if (!Object.keys(values).length) {
            store.removeItem(draftKey(form));
            return;
        }
        try {
            store.setItem(draftKey(form), JSON.stringify({ at: Date.now(), values: values }));
        } catch (e) {
            // Quota exceeded or storage disabled: the form still works.
        }
    }

    function loadDraft(form) {
        var store = storage();
        var raw = store && store.getItem(draftKey(form));
        if (!raw) {
            return null;
        }
        try {
            var draft = JSON.parse(raw);
            if (draft && draft.values && Date.now() - draft.at <= DRAFT_MAX_AGE) {
                return draft;
            }
        } catch (e) {
            // fall through: a damaged draft is simply dropped
        }
        store.removeItem(draftKey(form));
        return null;
    }

    function clearDraft(form) {
        var store = storage();
        if (store) {
            store.removeItem(draftKey(form));
        }
    }

    function relativeTime(ts) {
        var mins = Math.round((Date.now() - ts) / 60000);
        if (mins < 1) {
            return 'a moment ago';
        }
        if (mins < 60) {
            return mins + (mins === 1 ? ' minute ago' : ' minutes ago');
        }
        var hours = Math.round(mins / 60);
        if (hours < 24) {
            return hours + (hours === 1 ? ' hour ago' : ' hours ago');
        }
        var days = Math.round(hours / 24);
        return days + (days === 1 ? ' day ago' : ' days ago');
    }

    function offerDraft(form, draft) {
        if (canonical(readDraftValues(form)) === canonical(draft.values)) {
            return;
        }
        var banner = document.createElement('div');
        banner.className = 'draft-banner';
        banner.setAttribute('role', 'region');
        banner.setAttribute('aria-label', DRAFT_TEXT.title);
        banner.innerHTML =
            '<i class="bi bi-clock-history draft-banner-icon" aria-hidden="true"></i>' +
            '<div class="draft-banner-text"><strong></strong><span></span></div>' +
            '<div class="draft-banner-actions">' +
            '<button type="button" class="btn btn-primary btn-sm" data-draft-restore></button>' +
            '<button type="button" class="btn btn-outline-secondary btn-sm" data-draft-discard></button>' +
            '</div>';
        banner.querySelector('strong').textContent = DRAFT_TEXT.title;
        banner.querySelector('span').textContent = DRAFT_TEXT.hint.replace('{when}', relativeTime(draft.at));
        banner.querySelector('[data-draft-restore]').textContent = DRAFT_TEXT.restore;
        banner.querySelector('[data-draft-discard]').textContent = DRAFT_TEXT.discard;

        var wizard = activeWizard();
        if (wizard && wizard.content.parentNode) {
            wizard.content.parentNode.insertBefore(banner, wizard.content);
        } else {
            form.insertBefore(banner, form.firstChild);
        }

        banner.querySelector('[data-draft-restore]').addEventListener('click', function () {
            applyDraftValues(form, draft.values);
            // Cascading selects (governorate → district) load their options
            // after the parent changes; a second pass fills those in.
            setTimeout(function () { applyDraftValues(form, draft.values); }, 1500);
            banner.remove();
            toast(DRAFT_TEXT.restored, 'success');
        });
        banner.querySelector('[data-draft-discard]').addEventListener('click', function () {
            clearDraft(form);
            banner.remove();
        });
    }

    function initDrafts() {
        var forms = draftForms();
        var dirty = false;
        var submitting = false;
        var timer = null;

        forms.forEach(function (form) {
            var draft = loadDraft(form);
            if (draft) {
                offerDraft(form, draft);
            }

            ['input', 'change'].forEach(function (type) {
                form.addEventListener(type, function () {
                    dirty = true;
                    clearTimeout(timer);
                    timer = setTimeout(function () { saveDraft(form); }, 400);
                });
            });

            // The module scripts may cancel the submit after validation;
            // only a submit nobody prevented counts as "sent".
            form.addEventListener('submit', function (e) {
                setTimeout(function () {
                    if (!e.defaultPrevented) {
                        submitting = true;
                        clearDraft(form);
                    }
                }, 0);
            });
        });

        window.addEventListener('beforeunload', function (e) {
            if (dirty && !submitting && !suppressLeaveGuard) {
                e.preventDefault();
                e.returnValue = '';
            }
        });

        window.addEventListener('pageshow', function (ev) {
            if (ev.persisted) {
                submitting = false;
            }
        });

        // Reset wipes every answer on the page, so it asks first. The wizard
        // templates' #reset-btn22 is type="button" and had no handler at
        // all; it now resets the same way, after the same question.
        document.addEventListener('click', function (e) {
            var btn = e.target.closest ?
                e.target.closest('button[type="reset"], input[type="reset"], #reset-btn22') : null;
            if (!btn) {
                return;
            }
            var form = btn.form || btn.closest('form') || forms[0];
            if (!form) {
                return;
            }
            if (Object.keys(readDraftValues(form)).length && !window.confirm(DRAFT_TEXT.reset)) {
                e.preventDefault();
                e.stopImmediatePropagation();
                return;
            }
            if (btn.type !== 'reset') {
                form.reset();
            }
            clearDraft(form);
            dirty = false;
        }, true);
    }

    /* ---------------------------------------------------------------------
       9d. Long selects — type to shorten the list

       A <select> with a hundred centers or schools is hard to scan on any
       screen and hopeless on a phone. Selects on the wizard forms (or any
       select carrying data-searchable) with twelve or more options get a
       filter box above them; the select keeps its name, id, value and
       change events, so the module scripts see nothing new.
       --------------------------------------------------------------------- */

    function initSelectFilters() {
        $all('.form-wizard-content select:not([multiple]), select[data-searchable]').forEach(function (select) {
            if (select.options.length < 12 || select.querySelector('optgroup') || select.closest('.select-search')) {
                return;
            }

            var wrap = document.createElement('div');
            wrap.className = 'select-search';
            select.parentNode.insertBefore(wrap, select);

            var input = document.createElement('input');
            input.type = 'search';
            input.className = 'form-control select-search-input';
            input.autocomplete = 'off';
            input.placeholder = 'Type to shorten the list';
            input.setAttribute('aria-label', (fieldName(select) || 'List') + ': type to shorten the list');
            if (select.id) {
                input.setAttribute('aria-controls', select.id);
            }
            wrap.appendChild(input);
            wrap.appendChild(select);

            var all = null;
            function snapshot() {
                all = Array.prototype.slice.call(select.options);
            }
            input.addEventListener('focus', function () {
                if (!input.value) {
                    snapshot();
                }
            });
            input.addEventListener('input', function () {
                if (!all) {
                    snapshot();
                }
                var query = input.value.trim().toLowerCase();
                var keep = all.filter(function (option) {
                    return !query || option.value === '' || option.selected ||
                        option.text.toLowerCase().indexOf(query) !== -1;
                });
                // Moving options in and out of a select can reset which one
                // is selected; the current value is put back afterwards.
                var current = select.value;
                while (select.firstChild) {
                    select.removeChild(select.firstChild);
                }
                keep.forEach(function (option) { select.appendChild(option); });
                select.value = current;
                if (query && keep.length > 1) {
                    select.size = Math.min(keep.length, 6);
                } else {
                    select.removeAttribute('size');
                }
            });
            select.addEventListener('change', function () {
                select.removeAttribute('size');
            });
        });
    }

    /* ---------------------------------------------------------------------
       9e. Button semantics — one colour per meaning

       Cancel, Reset and Back buttons were coloured btn-warning or btn-info
       in the older templates; amber on "Cancel" reads as a hazard and blue
       makes it compete with the primary action. They become quiet outline
       buttons. Attendance state toggles keep their colours.
       --------------------------------------------------------------------- */

    function initButtonSemantics() {
        var quiet = /^(cancel|reset|close|back|go back|return|back to .+)$/i;
        $all('.btn-warning, .btn-info').forEach(function (btn) {
            if (btn.tagName === 'LABEL' || btn.closest('.btn-group-toggle, .btn-group')) {
                return;
            }
            var text = (btn.textContent || '').replace(/\s+/g, ' ').trim();
            var title = btn.getAttribute('title') || '';
            if (quiet.test(text) || (!text && quiet.test(title))) {
                btn.classList.remove('btn-warning', 'btn-info', 'text-white');
                btn.classList.add('btn-outline-secondary');
            }
        });
    }

    /* ---------------------------------------------------------------------
       9f. Session timer — warn before the idle logout, keep a busy user in

       AutoLogout (middleware.py) ends the session after AUTO_LOGOUT_DELAY
       minutes without a request, and typing into a long form makes none.
       base.html hands the cutoff and two URLs to the body element. While
       the user is active a keep-alive ping refreshes the server's clock;
       when they go quiet, a banner counts down the last two minutes with a
       "Stay signed in" button. When the server has already signed them
       out, the page goes to the sign-in screen with a way back; their
       draft is waiting on return.
       --------------------------------------------------------------------- */

    var SESSION_TEXT = {
        title: 'You will be signed out in {time}',
        hint: 'Nothing has been sent to the server for a while. Anything you typed is kept on this device.',
        stay: 'Stay signed in'
    };
    var suppressLeaveGuard = false;

    function initSessionTimer() {
        var body = document.body;
        var minutes = parseFloat(body.getAttribute('data-idle-minutes') || '0');
        var pingUrl = body.getAttribute('data-ping-url');
        var loginUrl = body.getAttribute('data-login-url') || '/accounts/login/';
        if (!minutes || minutes <= 0 || !pingUrl || !document.querySelector('.topbar')) {
            return;
        }

        var limit = minutes * 60 * 1000;
        var warnBefore = Math.min(2 * 60 * 1000, limit / 2);
        var activePingEvery = Math.min(5 * 60 * 1000, limit / 3);
        var activeWindow = Math.min(60 * 1000, limit / 3);
        var lastRequest = Date.now();
        var lastActivity = Date.now();
        var pinging = false;
        var banner = null;

        function signedOut() {
            suppressLeaveGuard = true;
            var next = encodeURIComponent(location.pathname + location.search);
            window.location.href = loginUrl + (loginUrl.indexOf('?') === -1 ? '?' : '&') + 'next=' + next;
        }

        function ping() {
            if (pinging) {
                return;
            }
            pinging = true;
            fetch(pingUrl, { credentials: 'same-origin', cache: 'no-store', redirect: 'manual' })
                .then(function (res) {
                    if (res.ok) {
                        lastRequest = Date.now();
                        hideBanner();
                    } else {
                        // A redirect to the sign-in page (opaque here) or an
                        // error: the server no longer has this session.
                        signedOut();
                    }
                })
                .catch(function () {
                    // Offline: leave the clock alone and try again later.
                })
                .then(function () {
                    pinging = false;
                });
        }

        function format(ms) {
            var s = Math.max(0, Math.ceil(ms / 1000));
            return Math.floor(s / 60) + ':' + ('0' + (s % 60)).slice(-2);
        }

        function showBanner() {
            if (banner) {
                return;
            }
            banner = document.createElement('div');
            banner.className = 'session-banner';
            banner.setAttribute('role', 'alert');
            banner.innerHTML =
                '<i class="bi bi-hourglass-split session-banner-icon" aria-hidden="true"></i>' +
                '<div class="session-banner-text"><strong></strong><span></span></div>' +
                '<button type="button" class="btn btn-primary" data-session-stay></button>';
            banner.querySelector('span').textContent = SESSION_TEXT.hint;
            var stay = banner.querySelector('[data-session-stay]');
            stay.textContent = SESSION_TEXT.stay;
            stay.addEventListener('click', ping);
            document.body.appendChild(banner);
            stay.focus();
        }

        function hideBanner() {
            if (banner) {
                banner.remove();
                banner = null;
            }
        }

        function check() {
            var left = limit - (Date.now() - lastRequest);
            if (left <= 0) {
                signedOut();
                return;
            }
            if (left <= warnBefore) {
                showBanner();
                banner.querySelector('strong').textContent = SESSION_TEXT.title.replace('{time}', format(left));
                return;
            }
            // Active within the last minute but quiet towards the server:
            // refresh its clock so a long form never times out mid-way.
            if (Date.now() - lastActivity < activeWindow && Date.now() - lastRequest > activePingEvery) {
                ping();
            }
        }

        ['keydown', 'pointerdown', 'input', 'change'].forEach(function (type) {
            document.addEventListener(type, function () {
                lastActivity = Date.now();
            }, { passive: true });
        });
        setInterval(check, 1000);
    }

    /* ---------------------------------------------------------------------
       10. Public toast helper
       --------------------------------------------------------------------- */

    function ensureToastHost() {
        var host = document.getElementById('rd-toast-host');
        if (!host) {
            host = document.createElement('div');
            host.id = 'rd-toast-host';
            host.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            host.style.zIndex = '2000';
            document.body.appendChild(host);
        }
        return host;
    }

    function toast(message, variant) {
        var host = ensureToastHost();
        var el = document.createElement('div');
        var tone = variant || 'primary';

        el.className = 'toast align-items-center text-bg-' + tone + ' border-0';
        el.setAttribute('role', 'status');
        el.setAttribute('aria-live', 'polite');
        el.innerHTML =
            '<div class="d-flex">' +
            '<div class="toast-body"></div>' +
            '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>' +
            '</div>';
        el.querySelector('.toast-body').textContent = message;
        host.appendChild(el);

        if (typeof window.bootstrap !== 'undefined') {
            var instance = new bootstrap.Toast(el, { delay: 4500 });
            el.addEventListener('hidden.bs.toast', function () {
                el.remove();
            });
            instance.show();
        }
    }

    /* ---------------------------------------------------------------------
       Bootstrap's jQuery interface for every jQuery on the page

       Bootstrap 5 attaches $.fn.modal, .dropdown, .collapse … to the jQuery
       present when its bundle loads. 115 page templates then load
       jquery-1.12.3 again for their own scripts, which replaces $ with a copy
       that has none of those methods: the module scripts' calls to
       $('#formErrorModal').modal('show') threw, and their validation and
       step handling stopped at that line. The interface is re-attached to
       whichever jQuery is current, at DOMContentLoaded and again at load.
       Methods another library already defined (jQuery UI's button and
       tooltip) are left alone.
       --------------------------------------------------------------------- */

    var BS_PLUGINS = {
        alert: 'Alert', button: 'Button', collapse: 'Collapse', dropdown: 'Dropdown',
        modal: 'Modal', offcanvas: 'Offcanvas', popover: 'Popover', tab: 'Tab',
        toast: 'Toast', tooltip: 'Tooltip'
    };

    function bridgeJQueryPlugins() {
        var $ = window.jQuery;
        if (!$ || !$.fn || typeof window.bootstrap === 'undefined' || $.bmaBootstrapBridged) {
            return;
        }
        Object.keys(BS_PLUGINS).forEach(function (name) {
            var Component = window.bootstrap[BS_PLUGINS[name]];
            if (!Component || typeof $.fn[name] === 'function') {
                return;
            }
            $.fn[name] = function (config) {
                return this.each(function () {
                    var data = Component.getOrCreateInstance(this, typeof config === 'object' ? config : {});
                    if (typeof config !== 'string') {
                        return;
                    }
                    if (typeof data[config] === 'undefined' || config.charAt(0) === '_' || config === 'constructor') {
                        throw new TypeError('No method named "' + config + '"');
                    }
                    data[config]();
                });
            };
        });
        $.bmaBootstrapBridged = true;
    }

    /* ---------------------------------------------------------------------
       Boot
       --------------------------------------------------------------------- */

    function boot() {
        bridgeJQueryPlugins();
        window.addEventListener('load', bridgeJQueryPlugins);
        upgradeAttributes(document);
        initComponents(document);
        initSidebar();
        initTheme();
        initForms();
        initTables();
        initFilterChips();
        initButtonGroups();
        initWizards();
        initFormErrors();
        initDrafts();
        initSelectFilters();
        initButtonSemantics();
        initSessionTimer();

        // Content injected later (remote modals, AJAX partials) needs the same
        // treatment; a scoped observer is cheaper than re-scanning on a timer.
        if ('MutationObserver' in window) {
            var observer = new MutationObserver(function (mutations) {
                mutations.forEach(function (mutation) {
                    Array.prototype.forEach.call(mutation.addedNodes, function (node) {
                        if (node.nodeType === 1) {
                            upgradeAttributes(node);
                            initComponents(node);
                        }
                    });
                });
            });
            observer.observe(document.body, { childList: true, subtree: true });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', boot);
    } else {
        boot();
    }

    // Apply the stored theme before first paint where possible, so a dark-mode
    // user does not get a white flash while the rest of the script loads.
    if (read(STORAGE_THEME) === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        document.documentElement.setAttribute('data-bs-theme', 'dark');
    }

    window.BMA = window.BMA || {};
    window.BMA.toast = toast;
    window.BMA.upgradeAttributes = upgradeAttributes;
    window.BMA.initComponents = initComponents;
    window.BMA.formErrors = {
        show: showFormErrors,
        refresh: refreshFormErrors,
        mark: markField,
        clear: clearField
    };
    window.BMA.drafts = {
        save: saveDraft,
        load: loadDraft,
        clear: clearDraft
    };
})();
