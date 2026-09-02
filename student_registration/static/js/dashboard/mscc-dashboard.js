/* ==========================================================================
   BMA Compiler — Makani dashboard controller
   --------------------------------------------------------------------------
   Reads window.msccDashboardConfig, fetches the aggregate endpoint and hands
   each series to BMACharts. Same shape as the BMA-NFE dashboard module.

   Replaces a Highcharts implementation that had a few real problems:
     * the KPI tiles were rendered server-side once and never refreshed, so a
       filtered chart sat under an unfiltered total;
     * the package-type tiles toggled a CSS class and reloaded, but the value
       was never sent, so they filtered nothing;
     * every filter <select> was commented out of the template while the JS
       still read them;
     * clicking a pie slice called reload(container), which only skipped one
       chart on refresh — it looked like a drill-down and did nothing.
   ========================================================================== */

(function (window, document) {
    'use strict';

    var config = window.msccDashboardConfig;
    if (!config || typeof window.BMACharts === 'undefined') {
        return;
    }

    var charts = window.BMACharts;
    var FILTERS = [
        { id: 'center_filter', param: 'centers' },
        { id: 'round_filter', param: 'rounds' },
        { id: 'governorate_filter', param: 'governorates' },
        { id: 'partner_filter', param: 'partners' }
    ];

    var packageTypes = [];
    var inFlight = 0;

    function el(id) {
        return document.getElementById(id);
    }

    function status(message) {
        var node = el('dashboard-status');
        if (node) {
            node.textContent = message || '';
        }
    }

    function collectFilters() {
        var params = {};

        FILTERS.forEach(function (filter) {
            var node = el(filter.id);
            if (!node) {
                return;
            }
            var values = Array.prototype.slice.call(node.selectedOptions || [])
                .map(function (opt) { return opt.value; })
                .filter(Boolean);
            if (values.length) {
                params[filter.param] = values;
            }
        });

        if (packageTypes.length) {
            params.types = packageTypes.slice();
        }
        return params;
    }

    function renderKpis(totals) {
        Object.keys(totals || {}).forEach(function (key) {
            var node = document.querySelector('[data-kpi="' + key + '"]');
            if (node) {
                node.textContent = charts.formatNumber(totals[key] || 0);
            }
        });
    }

    function renderCharts(payload) {
        renderKpis(payload.totals);

        config.charts.forEach(function (chart) {
            charts.bars('#' + chart.id, payload[chart.id] || [], {
                label: chart.title,
                emptyText: config.labels.empty,
                // Long tails get folded rather than given more hues.
                limit: 10
            });
        });

        charts.columns('#children_per_round', payload.children_per_round || [], {
            label: 'Children per cycle',
            emptyText: config.labels.empty
        });

        var moved = payload.children_moved_rounds || {};
        charts.grouped('#children_moved_rounds', {
            categories: moved.categories || [],
            series: [
                { name: config.labels.returning, values: moved.moved || [] },
                { name: config.labels.newChildren, values: moved['new'] || [] }
            ]
        }, {
            label: 'Returning versus new children per cycle',
            emptyText: config.labels.empty
        });
    }

    function load() {
        var request = ++inFlight;
        status(config.labels.loading);

        charts.fetchJson(config.dataUrl, collectFilters())
            .then(function (payload) {
                // A slower earlier request must not overwrite a newer one.
                if (request !== inFlight) {
                    return;
                }
                status('');
                renderCharts(payload);
            })
            .catch(function (error) {
                if (request !== inFlight) {
                    return;
                }
                status(config.labels.failed);
                window.console && console.error('[mscc-dashboard]', error);
            });
    }

    function syncPackageButtons() {
        document.querySelectorAll('.filter-package-type').forEach(function (btn) {
            var active = packageTypes.indexOf(btn.getAttribute('data-package-type')) !== -1;
            btn.setAttribute('aria-pressed', active ? 'true' : 'false');
            btn.classList.toggle('is-selected', active);
        });
    }

    function init() {
        FILTERS.forEach(function (filter) {
            var node = el(filter.id);
            if (node) {
                node.addEventListener('change', load);
            }
        });

        document.querySelectorAll('.filter-package-type').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var value = btn.getAttribute('data-package-type');
                var index = packageTypes.indexOf(value);
                if (index === -1) {
                    packageTypes.push(value);
                } else {
                    packageTypes.splice(index, 1);
                }
                syncPackageButtons();
                load();
            });
        });

        var reset = el('dashboard-reset');
        if (reset) {
            reset.addEventListener('click', function () {
                FILTERS.forEach(function (filter) {
                    var node = el(filter.id);
                    if (node) {
                        Array.prototype.forEach.call(node.options, function (opt) {
                            opt.selected = false;
                        });
                    }
                });
                packageTypes = [];
                syncPackageButtons();
                load();
            });
        }

        // The charts read their colours from CSS custom properties, so a theme
        // change needs a redraw to pick up the dark steps.
        var observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                if (mutation.attributeName === 'data-theme') {
                    load();
                }
            });
        });
        observer.observe(document.documentElement, { attributes: true });

        load();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})(window, document);
