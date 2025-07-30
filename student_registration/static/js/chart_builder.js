(function () {
    'use strict';

    let tooltip;

    function loadMsccData() {
        const source = document.getElementById('mscc-data-type').value;
        fetch(`/mscc/chart-data/?chart=${source}`)
            .then(r => r.json())
            .then(data => {
                document.getElementById('chart-data').value = JSON.stringify(data, null, 2);
                render();
            });
    }

    function render() {
        const type = document.getElementById('chart-type').value;
        let data;
        try {
            data = JSON.parse(document.getElementById('chart-data').value);
        } catch (e) {
            alert('Invalid data');
            return;
        }

        const svg = d3.select('#chart');
        const width = svg.node().clientWidth;
        const height = svg.node().clientHeight;
        svg.selectAll('*').remove();
        d3.select('#legend').html('');

        const color = d3
            .scaleOrdinal(d3.schemeCategory10)
            .domain(data.map((d) => d.label));

        if (!tooltip) {
            tooltip = d3
                .select('body')
                .append('div')
                .attr('class', 'tooltip')
                .style('opacity', 0);
        }

        if (type === 'bar') {
            const x = d3.scaleBand().range([0, width]).padding(0.1);
            const y = d3.scaleLinear().range([height, 0]);

            x.domain(data.map(d => d.label));
            y.domain([0, d3.max(data, d => d.value)]);

            svg.append('g')
                .attr('transform', `translate(0,${height})`)
                .call(d3.axisBottom(x));

            svg.append('g')
                .call(d3.axisLeft(y));

            svg.selectAll('.bar')
                .data(data)
                .enter().append('rect')
                .attr('class', 'bar')
                .attr('x', d => x(d.label))
                .attr('y', d => y(d.value))
                .attr('width', x.bandwidth())
                .attr('height', d => height - y(d.value))
                .attr('fill', d => color(d.label))
                .on('mousemove', (event, d) => {
                    tooltip
                        .style('opacity', 1)
                        .html(`${d.label}: ${d.value}`)
                        .style('left', event.pageX + 10 + 'px')
                        .style('top', event.pageY - 15 + 'px');
                })
                .on('mouseout', () => tooltip.style('opacity', 0));
        } else if (type === 'line') {
            const x = d3.scalePoint().range([0, width]);
            const y = d3.scaleLinear().range([height, 0]);

            x.domain(data.map(d => d.label));
            y.domain([0, d3.max(data, d => d.value)]);

            const line = d3.line()
                .x(d => x(d.label))
                .y(d => y(d.value));

            svg.append('g')
                .attr('transform', `translate(0,${height})`)
                .call(d3.axisBottom(x));

            svg.append('g')
                .call(d3.axisLeft(y));

            svg.append('path')
                .datum(data)
                .attr('fill', 'none')
                .attr('stroke', '#428bca')
                .attr('stroke-width', 2)
                .attr('d', line);

            svg.selectAll('circle')
                .data(data)
                .enter().append('circle')
                .attr('cx', d => x(d.label))
                .attr('cy', d => y(d.value))
                .attr('r', 4)
                .attr('fill', d => color(d.label))
                .on('mousemove', (event, d) => {
                    tooltip
                        .style('opacity', 1)
                        .html(`${d.label}: ${d.value}`)
                        .style('left', event.pageX + 10 + 'px')
                        .style('top', event.pageY - 15 + 'px');
                })
                .on('mouseout', () => tooltip.style('opacity', 0));
        } else if (type === 'pie') {
            const radius = Math.min(width, height) / 2;
            const g = svg.append('g')
                .attr('transform', `translate(${width / 2},${height / 2})`);

            const pie = d3.pie().value(d => d.value);
            const path = d3.arc()
                .outerRadius(radius - 10)
                .innerRadius(0);

            const arc = g.selectAll('.arc')
                .data(pie(data))
                .enter().append('g')
                .attr('class', 'arc');

            arc.append('path')
                .attr('d', path)
                .attr('fill', d => color(d.data.label))
                .on('mousemove', (event, d) => {
                    tooltip
                        .style('opacity', 1)
                        .html(`${d.data.label}: ${d.data.value}`)
                        .style('left', event.pageX + 10 + 'px')
                        .style('top', event.pageY - 15 + 'px');
                })
                .on('mouseout', () => tooltip.style('opacity', 0));

            arc.append('text')
                .attr('transform', d => `translate(${path.centroid(d)})`)
                .attr('dy', '0.35em')
                .text(d => d.data.label);
        }

        const legend = d3.select('#legend');
        const legendItem = legend
            .selectAll('.legend-item')
            .data(data)
            .enter()
            .append('div')
            .attr('class', 'legend-item');

        legendItem
            .append('span')
            .attr('class', 'legend-color')
            .style('background-color', d => color(d.label));

        legendItem
            .append('span')
            .text(d => d.label);
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.getElementById('chart-form').addEventListener('submit', function (e) {
            e.preventDefault();
            render();
        });
        const loadBtn = document.getElementById('load-mscc-data');
        if (loadBtn) {
            loadBtn.addEventListener('click', loadMsccData);
        }
        loadMsccData();
    });
})();