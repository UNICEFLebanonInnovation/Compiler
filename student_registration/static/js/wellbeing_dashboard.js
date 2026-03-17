$(function() {
    Highcharts.setOptions({
        colors: ['#003366', '#00ADEF', '#28a745', '#ffc107', '#dc3545', '#6c757d']
    });

    $.getJSON(DATA_URL, function(data) {
        renderLaborChart(data);
        renderAttendanceEduChart(data);
        renderFamilyChart(data);
        renderImpactCorrelation(data);
    });

    function renderLaborChart(data) {
        const laborCounts = _.countBy(data, 'have_labour');
        const chartData = Object.keys(laborCounts).map(key => ({ name: key, y: laborCounts[key] }));
        Highcharts.chart('labor-chart', {
            chart: { type: 'pie' },
            title: { text: null },
            series: [{ name: 'Children', colorByPoint: true, data: chartData }]
        });
    }

    function renderAttendanceEduChart(data) {
        const scatterData = data
            .filter(d => d.attendance_rate !== null && d.edu_improvement !== null)
            .map(d => [d.attendance_rate, d.edu_improvement]);
        Highcharts.chart('attendance-edu-chart', {
            chart: { type: 'scatter' },
            title: { text: null },
            xAxis: { title: { text: 'Attendance Rate (%)' } },
            yAxis: { title: { text: 'Improvement (%)' } },
            series: [{ name: 'Students', data: scatterData }]
        });
    }

    function renderFamilyChart(data) {
        const counts = _.countBy(data, 'living_arrangement');
        const categories = Object.keys(counts).filter(k => k !== "");
        const seriesData = categories.map(cat => counts[cat]);
        Highcharts.chart('family-chart', {
            chart: { type: 'bar' },
            title: { text: null },
            xAxis: { categories: categories },
            series: [{ name: 'Children', data: seriesData }]
        });
    }

    function renderImpactCorrelation(data) {
        const groupedLabor = _.groupBy(data, 'have_labour');
        const categories = Object.keys(groupedLabor);
        const avgAttendance = categories.map(cat => {
            const rates = groupedLabor[cat].map(d => d.attendance_rate).filter(r => r !== null);
            return rates.length > 0 ? _.mean(rates) : 0;
        });
        const avgImprovement = categories.map(cat => {
            const improvements = groupedLabor[cat].map(d => d.edu_improvement).filter(i => i !== null);
            return improvements.length > 0 ? _.mean(improvements) : 0;
        });
        Highcharts.chart('impact-correlation-chart', {
            chart: { type: 'column' },
            title: { text: 'Impact of Child Labor' },
            xAxis: { categories: categories },
            yAxis: [{ title: { text: 'Avg Attendance (%)' } }, { title: { text: 'Avg Improvement (%)' }, opposite: true }],
            series: [{ name: 'Avg Attendance', data: avgAttendance }, { name: 'Avg Improvement', data: avgImprovement, yAxis: 1 }]
        });
    }
});
