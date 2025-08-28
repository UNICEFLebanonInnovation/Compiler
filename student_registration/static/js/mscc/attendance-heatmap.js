(function() {
  const data = (window.attendanceData || []).map(d => {
    const date = new Date(d.attendance_day__attendance_date);
    const total = d.total || 0;
    const absent = d.absent || 0;
    const rate = total ? absent / total : 0;
    return { date, rate, absent, total };
  });

  if (!data.length) {
    return;
  }

  const cellSize = 25;
  const width = cellSize * 12;
  const height = cellSize * 31;

  const svg = d3.select('#attendance-heatmap').append('svg')
    .attr('width', width)
    .attr('height', height);

  const color = d3.scaleSequential()
    .domain([0, 1])
    .interpolator(d3.interpolateYlGnBu);

  data.forEach(d => {
    const x = d.date.getMonth() * cellSize;
    const y = (d.date.getDate() - 1) * cellSize;
    const tooltip = d3.timeFormat('%Y-%m-%d')(d.date) + ': ' + Math.round(d.rate * 100) + '% absent';

    svg.append('rect')
      .attr('x', x)
      .attr('y', y)
      .attr('width', cellSize - 1)
      .attr('height', cellSize - 1)
      .attr('fill', color(d.rate))
      .append('title')
      .text(tooltip);

    svg.append('text')
      .attr('x', x + cellSize / 2)
      .attr('y', y + cellSize / 2)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('font-size', '10px')
      .attr('fill', d.rate > 0.5 ? '#fff' : '#000')
      .text(d.absent);
  });

  const monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  svg.selectAll('text.month')
    .data(monthNames)
    .enter()
    .append('text')
    .attr('class', 'month')
    .attr('x', (d, i) => i * cellSize + 2)
    .attr('y', 10)
    .attr('font-size', '10px')
    .text(d => d);
})();
