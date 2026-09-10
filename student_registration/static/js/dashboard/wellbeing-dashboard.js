/* ==========================================================================
   BMA Compiler — Child wellbeing dashboard
   --------------------------------------------------------------------------
   Rewritten onto the shared D3 layer, replacing Highcharts 10.3.3 + lodash.
   The aggregation lodash was doing (countBy / meanBy / groupBy) is a few
   lines of d3, so the page now ships one charting dependency instead of two
   libraries.

   The old "Impact & Correlation Analysis" panel put two x-axes and two
   y-axes on one plot, showing attendance-by-labour-status and
   improvement-by-attendance-band together. Those measure different things
   over different categories, and a reader cannot tell which axis a bar
   belongs to, so they are now two charts.
   ========================================================================== */

(function (window, document) {
    'use strict';

    var config = window.wellbeingDashboardConfig;
    if (!config || typeof window.BMACharts === 'undefined') {
        return;
    }

    var charts = window.BMACharts;
    var labels = config.labels;

    function status(message) {
        var node = document.getElementById('wellbeing-status');
        if (node) {
            node.textContent = message ? ' · ' + message : '';
        }
    }

    /* Count rows by a field, dropping blanks. */
    function countBy(rows, field) {
        var counts = d3.rollup(
            rows.filter(function (d) { return d[field] !== null && d[field] !== undefined && d[field] !== ''; }),
            function (v) { return v.length; },
            function (d) { return d[field]; }
        );
        return Array.from(counts, function (entry) {
            return { name: String(entry[0]), y: entry[1] };
        });
    }

    /* Mean of a numeric field, ignoring nulls. Returns 0 for an empty set
       rather than NaN, which would render as a missing bar. */
    function meanOf(rows, field) {
        var values = rows
            .map(function (d) { return d[field]; })
            .filter(function (v) { return v !== null && v !== undefined && !isNaN(v); })
            .map(Number);
        return values.length ? d3.mean(values) : 0;
    }

    function round1(value) {
        return Math.round(value * 10) / 10;
    }

    function render(rows) {
        if (!Array.isArray(rows)) {
            rows = [];
        }

        // Two real series (caregivers vs children) — categorical, with a legend.
        var caregivers = countBy(rows, 'caregivers_distress');
        var children = countBy(rows, 'child_distress');

        function pick(list, key) {
            var hit = list.find(function (d) { return d.name === key; });
            return hit ? hit.y : 0;
        }

        charts.grouped('#distress-chart', {
            categories: [labels.yes, labels.no],
            series: [
                { name: labels.caregivers, values: [pick(caregivers, 'Yes'), pick(caregivers, 'No')] },
                { name: labels.children, values: [pick(children, 'Yes'), pick(children, 'No')] }
            ]
        }, { label: 'Distress indicators', emptyText: labels.empty });

        charts.bars('#edu-status-chart', countBy(rows, 'education_status'),
            { label: 'Educational status at entry', emptyText: labels.empty, limit: 10 });

        charts.bars('#barriers-chart', countBy(rows, 'barriers'),
            { label: 'Barriers to participation', emptyText: labels.empty, limit: 10 });

        charts.bars('#labor-chart', countBy(rows, 'have_labour'),
            { label: 'Child labour', emptyText: labels.empty });

        charts.bars('#family-chart', countBy(rows, 'living_arrangement'),
            { label: 'Living arrangement', emptyText: labels.empty, limit: 10 });

        // Subjects are a fixed set in a fixed order, so columns rather than a
        // magnitude-sorted bar.
        var improved = function (field) {
            return round1(meanOf(rows.filter(function (d) { return Number(d[field]) !== 0; }), field));
        };

        charts.columns('#subject-improvement-chart', [
            { name: labels.arabic, y: improved('arabic_improvement') },
            { name: labels.math, y: improved('math_improvement') },
            { name: labels.foreignLanguage, y: improved('language_improvement') }
        ], { label: 'Average improvement by subject', emptyText: labels.empty });

        // Correlation 1 — attendance by labour status.
        var byLabour = d3.group(
            rows.filter(function (d) { return d.have_labour !== null && d.have_labour !== ''; }),
            function (d) { return d.have_labour; }
        );
        charts.columns('#labor-attendance-chart',
            Array.from(byLabour, function (entry) {
                return { name: String(entry[0]), y: round1(meanOf(entry[1], 'attendance_rate')) };
            }),
            { label: 'Average attendance by labour status', emptyText: labels.empty });

        // Correlation 2 — improvement by attendance band. Bands are ordered,
        // so they keep their order.
        var bands = [
            { name: '0–20%', min: 0, max: 20 },
            { name: '20–40%', min: 20, max: 40 },
            { name: '40–60%', min: 40, max: 60 },
            { name: '60–80%', min: 60, max: 80 },
            // The top band is inclusive so a 100% attendance rate is counted.
            { name: '80–100%', min: 80, max: 100.01 }
        ];

        charts.columns('#attendance-improvement-chart',
            bands.map(function (band) {
                var inBand = rows.filter(function (d) {
                    var rate = Number(d.attendance_rate);
                    return !isNaN(rate) && rate >= band.min && rate < band.max &&
                           d.edu_improvement !== null && d.edu_improvement !== undefined;
                });
                return { name: band.name, y: round1(meanOf(inBand, 'edu_improvement')) };
            }),
            { label: 'Average improvement by attendance band', emptyText: labels.empty });
    }

    function init() {
        status(labels.loading);
        charts.fetchJson(config.dataUrl, {})
            .then(function (rows) {
                status('');
                render(rows);
            })
            .catch(function (error) {
                status(labels.failed);
                window.console && console.error('[wellbeing-dashboard]', error);
            });

        // Repaint on theme change so the charts pick up the dark steps.
        new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                if (mutation.attributeName === 'data-theme') {
                    charts.fetchJson(config.dataUrl, {}).then(render).catch(function () {});
                }
            });
        }).observe(document.documentElement, { attributes: true });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})(window, document);
