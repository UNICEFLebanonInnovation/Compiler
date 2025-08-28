(function() {
  function prepareData(raw) {
    return (raw || []).map(d => {
      const date = new Date(d.attendance_day__attendance_date);
      const total = d.total || 0;
      const absent = d.absent || 0;
      const present = total - absent;
      const rate = total ? present / total : 0;
      return { date, present, total, rate };
    });
  }

  function renderHeatmap(selector, rawData) {
    const data = prepareData(rawData);
    if (!data.length) {
      return;
    }

    const cellSize = 25;
    const margin = { top: 20, left: 40 };
    const width = cellSize * 31 + margin.left;
    const height = cellSize * 12 + margin.top;

    const svg = d3.select(selector).append('svg')
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const color = d3.scaleSequential()
      .domain([0, 1])
      .interpolator(d3.interpolateGreens);

    const tooltip = d3.select('body').append('div')
      .attr('class', 'heatmap-tooltip')
      .style('position', 'absolute')
      .style('opacity', 0)
      .style('padding', '4px 8px')
      .style('background', '#fff')
      .style('border', '1px solid #ccc')
      .style('pointer-events', 'none')
      .style('z-index', 10);

    g.selectAll('rect')
      .data(data)
      .enter()
      .append('rect')
      .attr('x', d => (d.date.getDate() - 1) * cellSize)
      .attr('y', d => d.date.getMonth() * cellSize)
      .attr('width', cellSize - 1)
      .attr('height', cellSize - 1)
      .attr('fill', d => color(d.rate))
      .on('mouseover', function(event, d) {
        const text = `${d3.timeFormat('%Y-%m-%d')(d.date)}: ${d.present}/${d.total} present`;
        tooltip.transition().style('opacity', 1);
        tooltip.html(text)
          .style('left', (event.pageX + 5) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        tooltip.transition().style('opacity', 0);
      });

    const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    svg.append('g')
      .selectAll('text.month')
      .data(monthNames)
      .enter()
      .append('text')
      .attr('class', 'month')
      .attr('x', 0)
      .attr('y', (d, i) => margin.top + i * cellSize + cellSize / 1.5)
      .attr('font-size', '10px')
      .text(d => d);

    const days = Array.from({ length: 31 }, (_, i) => i + 1);
    svg.append('g')
      .selectAll('text.day')
      .data(days)
      .enter()
      .append('text')
      .attr('class', 'day')
      .attr('x', (d, i) => margin.left + i * cellSize + cellSize / 2)
      .attr('y', 15)
      .attr('font-size', '10px')
      .attr('text-anchor', 'middle')
      .text(d => d);
  }

  renderHeatmap('#attendance-heatmap', window.attendanceData);

  const programmeData = window.programAttendanceData || {};
  Object.keys(programmeData).forEach(programme => {
    const slug = programme.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    const container = d3.select('#programme-heatmaps')
      .append('div')
      .attr('class', 'mb-4');
    container.append('h3').text(programme);
    const divId = `heatmap-${slug}`;
    container.append('div').attr('id', divId);
    renderHeatmap(`#${divId}`, programmeData[programme]);
  });
})();
