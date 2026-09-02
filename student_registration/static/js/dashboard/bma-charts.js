/* ==========================================================================
   BMA Compiler — D3 dashboard charts
   --------------------------------------------------------------------------
   A small chart layer over D3 v7, shared by every dashboard in the app, in
   the same shape as the BMA-NFE module: one IIFE, a namespaced global, data
   fetched as JSON and handed to a renderer per container.

   Why bars and not pies: these series are all "how many per category", whose
   job is magnitude comparison. A pie makes that comparison hard and needs a
   distinct hue per slice; a sorted bar in one hue reads instantly and keeps
   colour free to mean something. Charts that genuinely carry two series (for
   example moved vs. new per cycle) use the categorical palette and a legend.

   Colours are read from CSS custom properties on the container, so a theme
   switch repaints without JS. The categorical order is fixed — never cycle
   or reorder it; it was validated for colour-vision separation in both modes.

     BMACharts.bars(selector, data, opts)      [{name, y}] horizontal, sorted
     BMACharts.columns(selector, data, opts)   [{name, y}] vertical, in order
     BMACharts.grouped(selector, spec, opts)   {categories, series[]}
     BMACharts.empty(selector, message)
     BMACharts.fetchJson(url, params)

   Depends on: d3 v7 (global `d3`).
   ========================================================================== */

(function (window, document) {
    'use strict';

    if (typeof window.d3 === 'undefined') {
        window.console && console.warn('[BMACharts] D3 is not loaded; charts will not render.');
        return;
    }

    var SERIES_SLOTS = 8;
    var DURATION = 450;

    /* ------------------------------------------------------------------ */
    /* Utilities                                                           */
    /* ------------------------------------------------------------------ */

    function prefersReducedMotion() {
        return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }

    function duration() {
        return prefersReducedMotion() ? 0 : DURATION;
    }

    function token(node, name, fallback) {
        var value = getComputedStyle(node).getPropertyValue(name);
        return (value && value.trim()) || fallback;
    }

    function palette(node) {
        var colors = [];
        for (var i = 1; i <= SERIES_SLOTS; i++) {
            colors.push(token(node, '--viz-series-' + i, '#0097D7'));
        }
        return colors;
    }

    function formatNumber(value) {
        return d3.format(',')(value);
    }

    function root(selector) {
        var node = typeof selector === 'string' ? document.querySelector(selector) : selector;
        if (!node) {
            window.console && console.warn('[BMACharts] missing container:', selector);
            return null;
        }
        node.classList.add('viz');
        return node;
    }

    function hasData(data) {
        return Array.isArray(data) && data.some(function (d) { return Number(d.y) > 0; });
    }

    /* ------------------------------------------------------------------ */
    /* Tooltip — one shared node, positioned against the viewport          */
    /* ------------------------------------------------------------------ */

    var tooltipNode = null;

    function tooltip() {
        if (!tooltipNode) {
            tooltipNode = document.createElement('div');
            tooltipNode.className = 'viz-tooltip';
            tooltipNode.setAttribute('role', 'presentation');
            document.body.appendChild(tooltipNode);
        }
        return tooltipNode;
    }

    function showTooltip(event, name, value, total) {
        var node = tooltip();
        var share = total ? ' · ' + d3.format('.1%')(value / total) : '';
        node.innerHTML =
            '<span class="viz-tooltip-name"></span>' +
            '<span class="viz-tooltip-value"></span>';
        node.querySelector('.viz-tooltip-name').textContent = name;
        node.querySelector('.viz-tooltip-value').textContent = formatNumber(value) + share;
        node.classList.add('is-visible');
        moveTooltip(event);
    }

    function moveTooltip(event) {
        var node = tooltip();
        var pad = 14;
        var rect = node.getBoundingClientRect();
        var x = event.clientX + pad;
        var y = event.clientY + pad;

        if (x + rect.width > window.innerWidth - 8) {
            x = event.clientX - rect.width - pad;
        }
        if (y + rect.height > window.innerHeight - 8) {
            y = event.clientY - rect.height - pad;
        }

        node.style.left = Math.max(8, x) + 'px';
        node.style.top = Math.max(8, y) + 'px';
    }

    function hideTooltip() {
        if (tooltipNode) {
            tooltipNode.classList.remove('is-visible');
        }
    }

    /* ------------------------------------------------------------------ */
    /* Empty state and the accessible table                                */
    /* ------------------------------------------------------------------ */

    function empty(selector, message) {
        var node = root(selector);
        if (!node) {
            return;
        }
        node.innerHTML = '';
        var box = document.createElement('div');
        box.className = 'viz-empty';
        box.innerHTML = '<i class="bi bi-bar-chart" aria-hidden="true"></i>';
        var text = document.createElement('span');
        text.textContent = message || 'No data for the current filters.';
        box.appendChild(text);
        node.appendChild(box);
    }

    /* Mirrors the chart as a table. Screen readers get it via the sr-only
       copy; sighted users can reveal it from the card header, which is also
       what satisfies the contrast-relief rule for the lighter series steps. */
    function attachTable(node, columns, rows, label) {
        var existing = node.parentNode.querySelector('.viz-table-wrap');
        if (existing) {
            existing.remove();
        }

        var wrap = document.createElement('div');
        wrap.className = 'viz-table-wrap sr-only';
        wrap.setAttribute('data-viz-table', '');

        var table = document.createElement('table');
        table.className = 'table viz-table';
        if (label) {
            var caption = document.createElement('caption');
            caption.className = 'sr-only';
            caption.textContent = label;
            table.appendChild(caption);
        }

        var thead = document.createElement('thead');
        var headRow = document.createElement('tr');
        columns.forEach(function (col) {
            var th = document.createElement('th');
            th.scope = 'col';
            th.textContent = col;
            headRow.appendChild(th);
        });
        thead.appendChild(headRow);
        table.appendChild(thead);

        var tbody = document.createElement('tbody');
        rows.forEach(function (row) {
            var tr = document.createElement('tr');
            row.forEach(function (cell, i) {
                var td = document.createElement(i === 0 ? 'th' : 'td');
                if (i === 0) {
                    td.scope = 'row';
                }
                td.textContent = cell;
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);
        wrap.appendChild(table);
        node.parentNode.appendChild(wrap);
    }

    /* ------------------------------------------------------------------ */
    /* Re-render on resize                                                 */
    /* ------------------------------------------------------------------ */

    function observe(node, redraw) {
        if (!('ResizeObserver' in window)) {
            return;
        }
        if (node.__vizObserver) {
            node.__vizObserver.disconnect();
        }
        var last = node.getBoundingClientRect().width;
        var observer = new ResizeObserver(function () {
            var width = node.getBoundingClientRect().width;
            // Only a width change matters, and only a real one — redrawing on
            // sub-pixel noise would fight the enter transition.
            if (Math.abs(width - last) > 1) {
                last = width;
                redraw();
            }
        });
        observer.observe(node);
        node.__vizObserver = observer;
    }

    /* ------------------------------------------------------------------ */
    /* Horizontal bars — the default for "count per category"              */
    /* ------------------------------------------------------------------ */

    function bars(selector, data, opts) {
        var node = root(selector);
        if (!node) {
            return;
        }

        opts = opts || {};
        var label = opts.label || node.getAttribute('data-viz-label') || 'Chart';

        if (!hasData(data)) {
            empty(selector, opts.emptyText);
            return;
        }

        function draw() {
            node.innerHTML = '';

            var items = data
                .map(function (d) { return { name: String(d.name || 'N/A'), y: Number(d.y) || 0 }; })
                .filter(function (d) { return d.y > 0; })
                .sort(function (a, b) { return b.y - a.y; });

            if (opts.limit && items.length > opts.limit) {
                var head = items.slice(0, opts.limit);
                var tail = items.slice(opts.limit);
                var other = tail.reduce(function (sum, d) { return sum + d.y; }, 0);
                // Never invent a hue for a long tail — fold it into "Other".
                head.push({ name: 'Other (' + tail.length + ')', y: other });
                items = head;
            }

            var total = d3.sum(items, function (d) { return d.y; });
            var width = node.getBoundingClientRect().width || 320;
            var rowHeight = 26;
            var margin = { top: 6, right: 52, bottom: 6, left: Math.min(150, Math.max(90, width * 0.36)) };
            var height = items.length * rowHeight;

            var svg = d3.select(node).append('svg')
                .attr('width', width)
                .attr('height', height + margin.top + margin.bottom)
                .attr('role', 'img')
                .attr('aria-label', label + '. ' + items.length + ' categories, ' +
                      formatNumber(total) + ' total.');

            var g = svg.append('g')
                .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

            var innerWidth = Math.max(10, width - margin.left - margin.right);

            var x = d3.scaleLinear()
                .domain([0, d3.max(items, function (d) { return d.y; }) || 1])
                .nice()
                .range([0, innerWidth]);

            var y = d3.scaleBand()
                .domain(items.map(function (d) { return d.name; }))
                .range([0, height])
                .padding(0.28);

            var color = opts.color || token(node, '--viz-sequential', '#0097D7');

            g.append('g')
                .attr('class', 'viz-axis')
                .call(d3.axisLeft(y).tickSize(0))
                .call(function (sel) { sel.select('.domain').remove(); })
                .selectAll('text')
                .text(function (d) { return d.length > 26 ? d.slice(0, 25) + '…' : d; })
                .append('title')
                .text(function (d) { return d; });

            var barGroup = g.append('g');

            var bar = barGroup.selectAll('rect')
                .data(items)
                .join('rect')
                .attr('class', 'viz-bar')
                .attr('x', 0)
                .attr('y', function (d) { return y(d.name); })
                .attr('height', y.bandwidth())
                .attr('rx', 4)
                .attr('fill', color)
                .attr('width', 0);

            bar.transition().duration(duration())
                .attr('width', function (d) { return Math.max(2, x(d.y)); });

            bar.on('mousemove', function (event, d) { showTooltip(event, d.name, d.y, total); })
                .on('mouseleave', hideTooltip);

            // Direct value labels: they carry the reading when the fill is
            // low-contrast, and remove the need to trace back to an axis.
            g.append('g')
                .selectAll('text')
                .data(items)
                .join('text')
                .attr('class', 'viz-value')
                .attr('x', function (d) { return Math.max(2, x(d.y)) + 6; })
                .attr('y', function (d) { return y(d.name) + y.bandwidth() / 2; })
                .attr('dy', '0.35em')
                .text(function (d) { return formatNumber(d.y); });

            attachTable(node, [opts.categoryHeading || 'Category', 'Count'],
                items.map(function (d) { return [d.name, formatNumber(d.y)]; }), label);
        }

        draw();
        observe(node, draw);
    }

    /* ------------------------------------------------------------------ */
    /* Columns — for a category with a meaningful order (cycles, months)   */
    /* ------------------------------------------------------------------ */

    function columns(selector, data, opts) {
        var node = root(selector);
        if (!node) {
            return;
        }

        opts = opts || {};
        var label = opts.label || node.getAttribute('data-viz-label') || 'Chart';

        if (!hasData(data)) {
            empty(selector, opts.emptyText);
            return;
        }

        function draw() {
            node.innerHTML = '';

            // Order is meaningful here, so it is preserved rather than sorted.
            var items = data
                .map(function (d) { return { name: String(d.name || 'N/A'), y: Number(d.y) || 0 }; });

            var total = d3.sum(items, function (d) { return d.y; });
            var width = node.getBoundingClientRect().width || 320;
            var height = opts.height || 260;
            var margin = { top: 16, right: 12, bottom: 64, left: 46 };
            var innerWidth = Math.max(10, width - margin.left - margin.right);
            var innerHeight = Math.max(10, height - margin.top - margin.bottom);

            var svg = d3.select(node).append('svg')
                .attr('width', width)
                .attr('height', height)
                .attr('role', 'img')
                .attr('aria-label', label + '. ' + items.length + ' categories, ' +
                      formatNumber(total) + ' total.');

            var g = svg.append('g')
                .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

            var x = d3.scaleBand()
                .domain(items.map(function (d) { return d.name; }))
                .range([0, innerWidth])
                .padding(0.25);

            var y = d3.scaleLinear()
                .domain([0, d3.max(items, function (d) { return d.y; }) || 1])
                .nice()
                .range([innerHeight, 0]);

            g.append('g')
                .attr('class', 'viz-grid')
                .selectAll('line')
                .data(y.ticks(4))
                .join('line')
                .attr('x1', 0).attr('x2', innerWidth)
                .attr('y1', y).attr('y2', y);

            g.append('g')
                .attr('class', 'viz-axis')
                .attr('transform', 'translate(0,' + innerHeight + ')')
                .call(d3.axisBottom(x).tickSize(0).tickPadding(8))
                .selectAll('text')
                .attr('transform', 'rotate(-40)')
                .style('text-anchor', 'end')
                .text(function (d) { return d.length > 18 ? d.slice(0, 17) + '…' : d; })
                .append('title')
                .text(function (d) { return d; });

            g.append('g')
                .attr('class', 'viz-axis')
                .call(d3.axisLeft(y).ticks(4).tickSize(0).tickFormat(d3.format('~s')))
                .call(function (sel) { sel.select('.domain').remove(); });

            var color = opts.color || token(node, '--viz-sequential', '#0097D7');

            var bar = g.append('g').selectAll('rect')
                .data(items)
                .join('rect')
                .attr('class', 'viz-bar')
                .attr('x', function (d) { return x(d.name); })
                .attr('width', x.bandwidth())
                .attr('rx', 4)
                .attr('fill', color)
                .attr('y', innerHeight)
                .attr('height', 0);

            bar.transition().duration(duration())
                .attr('y', function (d) { return y(d.y); })
                .attr('height', function (d) { return innerHeight - y(d.y); });

            bar.on('mousemove', function (event, d) { showTooltip(event, d.name, d.y, total); })
                .on('mouseleave', hideTooltip);

            attachTable(node, [opts.categoryHeading || 'Category', 'Count'],
                items.map(function (d) { return [d.name, formatNumber(d.y)]; }), label);
        }

        draw();
        observe(node, draw);
    }

    /* ------------------------------------------------------------------ */
    /* Grouped bars — two or more real series                              */
    /* ------------------------------------------------------------------ */

    function grouped(selector, spec, opts) {
        var node = root(selector);
        if (!node) {
            return;
        }

        opts = opts || {};
        spec = spec || {};
        var label = opts.label || node.getAttribute('data-viz-label') || 'Chart';
        var categories = spec.categories || [];
        var series = (spec.series || []).filter(function (s) { return s && s.values; });

        var anyData = series.some(function (s) {
            return s.values.some(function (v) { return Number(v) > 0; });
        });

        if (!categories.length || !series.length || !anyData) {
            empty(selector, opts.emptyText);
            return;
        }

        function draw() {
            node.innerHTML = '';

            var colors = palette(node);
            var width = node.getBoundingClientRect().width || 320;
            var height = opts.height || 280;
            var margin = { top: 8, right: 12, bottom: 64, left: 46 };
            var innerWidth = Math.max(10, width - margin.left - margin.right);
            var innerHeight = Math.max(10, height - margin.top - margin.bottom);

            // A legend is always present from two series up, so identity never
            // rests on colour alone.
            var legend = document.createElement('ul');
            legend.className = 'viz-legend';
            series.forEach(function (s, i) {
                var li = document.createElement('li');
                var swatch = document.createElement('span');
                swatch.className = 'viz-swatch';
                swatch.style.background = colors[i % SERIES_SLOTS];
                var text = document.createElement('span');
                text.textContent = s.name;
                li.appendChild(swatch);
                li.appendChild(text);
                legend.appendChild(li);
            });
            node.appendChild(legend);

            var svg = d3.select(node).append('svg')
                .attr('width', width)
                .attr('height', height)
                .attr('role', 'img')
                .attr('aria-label', label + '. ' + series.length + ' series across ' +
                      categories.length + ' categories.');

            var g = svg.append('g')
                .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

            var x0 = d3.scaleBand()
                .domain(categories)
                .range([0, innerWidth])
                .paddingInner(0.25);

            var x1 = d3.scaleBand()
                .domain(series.map(function (s) { return s.name; }))
                .range([0, x0.bandwidth()])
                // A 2px surface gap between adjacent fills keeps them readable
                // as separate marks rather than one block.
                .padding(x0.bandwidth() > 24 ? 0.12 : 0.05);

            var maxValue = d3.max(series, function (s) {
                return d3.max(s.values, function (v) { return Number(v) || 0; });
            }) || 1;

            var y = d3.scaleLinear().domain([0, maxValue]).nice().range([innerHeight, 0]);

            g.append('g')
                .attr('class', 'viz-grid')
                .selectAll('line')
                .data(y.ticks(4))
                .join('line')
                .attr('x1', 0).attr('x2', innerWidth)
                .attr('y1', y).attr('y2', y);

            g.append('g')
                .attr('class', 'viz-axis')
                .attr('transform', 'translate(0,' + innerHeight + ')')
                .call(d3.axisBottom(x0).tickSize(0).tickPadding(8))
                .selectAll('text')
                .attr('transform', 'rotate(-40)')
                .style('text-anchor', 'end')
                .text(function (d) { return d.length > 18 ? d.slice(0, 17) + '…' : d; })
                .append('title')
                .text(function (d) { return d; });

            g.append('g')
                .attr('class', 'viz-axis')
                .call(d3.axisLeft(y).ticks(4).tickSize(0).tickFormat(d3.format('~s')))
                .call(function (sel) { sel.select('.domain').remove(); });

            categories.forEach(function (category, ci) {
                var group = g.append('g')
                    .attr('transform', 'translate(' + x0(category) + ',0)');

                var rows = series.map(function (s, si) {
                    return { name: s.name, value: Number(s.values[ci]) || 0, index: si };
                });

                var rect = group.selectAll('rect')
                    .data(rows)
                    .join('rect')
                    .attr('class', 'viz-bar')
                    .attr('x', function (d) { return x1(d.name); })
                    .attr('width', x1.bandwidth())
                    .attr('rx', 3)
                    .attr('fill', function (d) { return colors[d.index % SERIES_SLOTS]; })
                    .attr('y', innerHeight)
                    .attr('height', 0);

                rect.transition().duration(duration())
                    .attr('y', function (d) { return y(d.value); })
                    .attr('height', function (d) { return innerHeight - y(d.value); });

                rect.on('mousemove', function (event, d) {
                        showTooltip(event, category + ' · ' + d.name, d.value, null);
                    })
                    .on('mouseleave', hideTooltip);
            });

            attachTable(node,
                [opts.categoryHeading || 'Category'].concat(series.map(function (s) { return s.name; })),
                categories.map(function (c, ci) {
                    return [c].concat(series.map(function (s) {
                        return formatNumber(Number(s.values[ci]) || 0);
                    }));
                }), label);
        }

        draw();
        observe(node, draw);
    }

    /* ------------------------------------------------------------------ */
    /* Data helpers                                                        */
    /* ------------------------------------------------------------------ */

    function toQuery(params) {
        var q = new URLSearchParams();
        Object.keys(params || {}).forEach(function (key) {
            var value = params[key];
            if (value === null || value === undefined || value === '') {
                return;
            }
            if (Array.isArray(value)) {
                value.forEach(function (v) {
                    if (v !== '' && v !== null && v !== undefined) {
                        q.append(key, v);
                    }
                });
            } else {
                q.append(key, value);
            }
        });
        var qs = q.toString();
        return qs ? '?' + qs : '';
    }

    function fetchJson(url, params) {
        return fetch(url + toQuery(params), {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            credentials: 'same-origin'
        }).then(function (response) {
            if (!response.ok) {
                throw new Error('Dashboard data request failed: ' + response.status);
            }
            return response.json();
        });
    }

    /* Reveal/hide the table mirror of a chart. */
    function toggleTable(node) {
        var wrap = node && node.parentNode && node.parentNode.querySelector('[data-viz-table]');
        if (!wrap) {
            return false;
        }
        wrap.classList.toggle('sr-only');
        return !wrap.classList.contains('sr-only');
    }

    document.addEventListener('click', function (event) {
        var btn = event.target.closest && event.target.closest('.chart-toggle-table');
        if (!btn) {
            return;
        }
        var card = btn.closest('.card');
        var chart = card && card.querySelector('.viz');
        var shown = toggleTable(chart);
        btn.setAttribute('aria-pressed', shown ? 'true' : 'false');
        btn.querySelector('i').className = shown ? 'bi bi-bar-chart' : 'bi bi-table';
    });

    window.BMACharts = {
        bars: bars,
        columns: columns,
        grouped: grouped,
        empty: empty,
        fetchJson: fetchJson,
        formatNumber: formatNumber
    };
})(window, document);
