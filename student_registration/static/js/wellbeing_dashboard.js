$(function() {
    Highcharts.setOptions({
        colors: ['#003366', '#00ADEF', '#28a745', '#ffc107', '#dc3545', '#6c757d']
    });

    $.getJSON(DATA_URL, function(data) {
        renderDistressChart(data);
        renderEducationStatusChart(data);
        renderBarriersChart(data);
        renderLaborChart(data);
        renderSubjectImprovementChart(data);
        renderFamilyChart(data);
        renderImpactCorrelation(data);
    });

    function renderDistressChart(data) {
        const cgDistress = _.countBy(data, 'caregivers_distress');
        const childDistress = _.countBy(data, 'child_distress');

        Highcharts.chart('distress-chart', {
            chart: { type: 'column' },
            title: { text: null },
            xAxis: { categories: ['Yes', 'No'] },
            yAxis: { title: { text: 'Count' } },
            series: [
                { name: 'Caregivers', data: [cgDistress['Yes'] || 0, cgDistress['No'] || 0] },
                { name: 'Children', data: [childDistress['Yes'] || 0, childDistress['No'] || 0] }
            ]
        });
    }

    function renderEducationStatusChart(data) {
        const counts = _.countBy(data, 'education_status');
        const chartData = Object.keys(counts).filter(k => k && k !== "").map(key => ({ name: key, y: counts[key] }));
        Highcharts.chart('edu-status-chart', {
            chart: { type: 'pie' },
            title: { text: null },
            series: [{ name: 'Children', colorByPoint: true, data: chartData }]
        });
    }

    function renderBarriersChart(data) {
        const counts = _.countBy(data, 'barriers');
        const categories = Object.keys(counts).filter(k => k && k !== "");
        const seriesData = categories.map(cat => counts[cat]);
        Highcharts.chart('barriers-chart', {
            chart: { type: 'bar' },
            title: { text: null },
            xAxis: { categories: categories },
            series: [{ name: 'Count', data: seriesData }]
        });
    }

    function renderLaborChart(data) {
        const laborCounts = _.countBy(data, 'have_labour');
        const chartData = Object.keys(laborCounts).map(key => ({ name: key, y: laborCounts[key] }));
        Highcharts.chart('labor-chart', {
            chart: { type: 'pie' },
            title: { text: null },
            series: [{ name: 'Children', colorByPoint: true, data: chartData }]
        });
    }

    function renderSubjectImprovementChart(data) {
        const arabic = _.meanBy(data.filter(d => d.arabic_improvement !== 0), 'arabic_improvement') || 0;
        const math = _.meanBy(data.filter(d => d.math_improvement !== 0), 'math_improvement') || 0;
        const lang = _.meanBy(data.filter(d => d.language_improvement !== 0), 'language_improvement') || 0;

        Highcharts.chart('subject-improvement-chart', {
            chart: { type: 'column' },
            title: { text: null },
            xAxis: { categories: ['Arabic', 'Math', 'Foreign Lang'] },
            yAxis: { title: { text: 'Avg Improvement (%)' } },
            series: [{ name: 'Subjects', data: [arabic, math, lang] }]
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
        // Attendance impact of Labor
        const groupedLabor = _.groupBy(data, 'have_labour');
        const laborCategories = Object.keys(groupedLabor);
        const avgAttendanceLabor = laborCategories.map(cat => {
            const rates = groupedLabor[cat].map(d => d.attendance_rate).filter(r => r !== null);
            return rates.length > 0 ? _.mean(rates) : 0;
        });

        // Impact of attendance on improvement
        const attendanceBins = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%'];
        const avgImprovementByAtt = attendanceBins.map((bin, i) => {
            const min = i * 20;
            const max = (i + 1) * 20;
            const filtered = data.filter(d => d.attendance_rate >= min && d.attendance_rate < max && d.edu_improvement !== null);
            return filtered.length > 0 ? _.meanBy(filtered, 'edu_improvement') : 0;
        });

        Highcharts.chart('impact-correlation-chart', {
            chart: { type: 'column' },
            title: { text: 'Correlation: Labor vs Attendance & Attendance vs Improvement' },
            xAxis: [
                { categories: laborCategories, title: { text: 'Labor Status' } },
                { categories: attendanceBins, title: { text: 'Attendance Range' }, opposite: true }
            ],
            yAxis: [
                { title: { text: 'Avg Attendance (%)' } },
                { title: { text: 'Avg Improvement (%)' }, opposite: true }
            ],
            series: [
                { name: 'Avg Attendance (by Labor)', data: avgAttendanceLabor, xAxis: 0, yAxis: 0 },
                { name: 'Avg Improvement (by Attendance)', data: avgImprovementByAtt, xAxis: 1, yAxis: 1 }
            ]
        });
    }
});
