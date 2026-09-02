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
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
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
       7. Filter chips
       --------------------------------------------------------------------- */

    function initFilterChips() {
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
       8. Multi-step form wizard
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

        if (this.steps.length > 1) {
            var bar = document.createElement('div');
            bar.className = 'wizard-progress';
            bar.innerHTML = '<div class="wizard-progress-bar"></div>';
            if (this.nav && this.nav.parentNode) {
                this.nav.parentNode.insertBefore(bar, this.nav.nextSibling);
            }
            this.progress = bar.firstChild;
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
        if (this.nextBtn) {
            this.nextBtn.classList.toggle('d-none', index >= this.steps.length - 1);
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
                    } else if (wizard.nextBtn && i === wizard.index + 1) {
                        wizard.nextBtn.click();
                    }
                });
            });
        });

        if (!wizards.length) {
            return;
        }

        // Registered on `load` so this runs after the module scripts' jQuery
        // handlers, letting us honour a preventDefault() from their validation.
        window.addEventListener('load', function () {
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
       9. Public toast helper
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
       Boot
       --------------------------------------------------------------------- */

    function boot() {
        upgradeAttributes(document);
        initComponents(document);
        initSidebar();
        initTheme();
        initForms();
        initTables();
        initFilterChips();
        initWizards();

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
    }

    window.BMA = window.BMA || {};
    window.BMA.toast = toast;
    window.BMA.upgradeAttributes = upgradeAttributes;
    window.BMA.initComponents = initComponents;
})();
