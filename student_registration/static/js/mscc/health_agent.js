(function () {
  'use strict';

  function qs(scope, selector) {
    return scope.querySelector(selector);
  }

  function escapeHtml(value) {
    if (value === undefined || value === null) {
      return '';
    }
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i += 1) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + '=') {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function renderMarkdown(markdown) {
    if (!markdown) {
      return '<p class="text-muted mb-0">No AI analysis was generated for this request.</p>';
    }

    var escaped = escapeHtml(markdown);
    var lines = escaped.split(/\r?\n/);
    var html = '';
    var inList = false;

    lines.forEach(function (line) {
      var trimmed = line.trim();
      if (!trimmed) {
        if (inList) {
          html += '</ul>';
          inList = false;
        }
        html += '<p></p>';
        return;
      }

      var headingMatch = trimmed.match(/^(#{1,3})\s+(.*)$/);
      if (headingMatch) {
        if (inList) {
          html += '</ul>';
          inList = false;
        }
        var level = headingMatch[1].length;
        var tag = level === 1 ? 'h3' : level === 2 ? 'h4' : 'h5';
        html += '<' + tag + '>' + headingMatch[2] + '</' + tag + '>';
        return;
      }

      var listMatch = trimmed.match(/^[-*+]\s+(.*)$/);
      if (listMatch) {
        if (!inList) {
          html += '<ul>';
          inList = true;
        }
        html += '<li>' + listMatch[1] + '</li>';
        return;
      }

      if (inList) {
        html += '</ul>';
        inList = false;
      }
      html += '<p>' + trimmed + '</p>';
    });

    if (inList) {
      html += '</ul>';
    }

    html = html
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>');

    return html;
  }

  function formatPercent(value) {
    if (value === undefined || value === null || value === '') {
      return '—';
    }
    var percent = Number(value) * 100;
    if (isNaN(percent)) {
      return '—';
    }
    return percent.toFixed(0) + '%';
  }

  function formatDate(value) {
    if (!value) {
      return '—';
    }
    try {
      var date = new Date(value);
      if (!isNaN(date.getTime())) {
        return date.toLocaleDateString();
      }
    } catch (err) {
      return escapeHtml(value);
    }
    return date.toLocaleDateString();
  }

  function formatScore(value) {
    if (value === undefined || value === null || value === '') {
      return '—';
    }

    var number = Number(value);
    if (!isNaN(number)) {
      if (Math.abs(number % 1) < 0.01) {
        return String(Math.round(number));
      }
      return number.toFixed(1);
    }

    return String(value);
  }

  function lifeQualityBadgeClass(value) {
    switch (value) {
      case 'Critical concern':
        return 'danger';
      case 'Needs attention':
        return 'warning';
      case 'Stable':
        return 'success';
      case 'Thriving':
        return 'primary';
      default:
        return 'info';
    }
  }

  function programmeImpactBadgeClass(direction) {
    switch (direction) {
      case 'positive':
        return 'success';
      case 'negative':
        return 'danger';
      case 'mixed':
      case 'neutral':
        return 'warning';
      default:
        return 'info';
    }
  }

  function renderFocusTopics(topics) {
    if (!Array.isArray(topics) || !topics.length) {
      return '';
    }

    var badges = topics
      .map(function (topic) {
        return '<span class="badge badge-light text-primary mr-1 mb-1">' + escapeHtml(topic) + '</span>';
      })
      .join('');

    return (
      '<div class="priority-focus-topics small text-muted">' +
      '<span class="mr-1">Focus:</span>' +
      badges +
      '</div>'
    );
  }

  function renderAttendanceSummary(attendance) {
    if (!attendance) {
      return '<p class="text-muted small mb-0">No attendance data recorded.</p>';
    }

    var attended = attendance.attended_sessions || 0;
    var total = attendance.total_sessions || 0;
    var missed = attendance.missed_sessions || 0;
    var rate = formatPercent(attendance.attendance_rate);
    var absence = attendance.most_recent_absence ? formatDate(attendance.most_recent_absence) : null;

    var html = '';
    html += '<div class="priority-metric-value">' + rate + '</div>';
    html += '<div class="small text-muted">Attendance rate</div>';
    html += '<div class="small">' + escapeHtml(attended) + ' of ' + escapeHtml(total) + ' sessions attended</div>';
    html += '<div class="small text-muted">Missed sessions: ' + escapeHtml(missed) + '</div>';
    if (absence) {
      html += '<div class="small text-muted">Last absence: ' + absence + '</div>';
    }

    return html;
  }

  function renderServiceSummary(services) {
    if (!services) {
      return '<p class="text-muted small mb-0">No service data recorded.</p>';
    }
    var keyMeta = [
      { key: 'pss', label: 'PSS' },
      { key: 'health', label: 'Health & Nutrition' },
      { key: 'support', label: 'Support' },
    ];

    var html = '<div class="priority-service-grid">';
    keyMeta.forEach(function (meta) {
      var summary = services[meta.key];
      if (!summary) {
        return;
      }

      var completed = summary.completed || 0;
      var total = summary.total || 0;
      var pending = summary.required_pending || 0;
      var pendingItems = (summary.items || []).filter(function (item) {
        return item.required && !item.completed;
      });

      html += '<div class="priority-service-item border rounded p-3">';
      html += '<div class="d-flex justify-content-between align-items-center mb-2">';
      html += '<span class="small text-uppercase text-muted">' + escapeHtml(meta.label) + '</span>';
      html += '<span class="badge badge-' + (pending ? 'danger' : 'success') + '">';
      html += pending ? escapeHtml(pending) + ' pending' : 'Up to date';
      html += '</span>';
      html += '</div>';
      html += '<div class="h5 mb-1">' + escapeHtml(completed) + ' / ' + escapeHtml(total) + '</div>';
      if (summary.required_total) {
        html += '<div class="small text-muted">' + escapeHtml(summary.required_total) + ' required services</div>';
      }
      if (pendingItems.length) {
        var itemsHtml = pendingItems
          .map(function (item) {
            return '<li>' + escapeHtml(item.name || 'Service') + '</li>';
          })
          .join('');
        html += '<div class="small mt-2">Pending:</div>';
        html += '<ul class="small pl-3 mb-0">' + itemsHtml + '</ul>';
      }
      html += '</div>';
    });
    html += '</div>';

    if (services.overall_pending_required) {
      html +=
        '<p class="small text-danger mb-0 mt-2">' +
        escapeHtml(services.overall_pending_required) +
        ' required services still pending.</p>';
    }

    return html;
  }

  function renderAlerts(alerts) {
    if (!alerts || !alerts.length) {
      return '<span class="badge badge-secondary">No alerts</span>';
    }
    return alerts
      .map(function (alert) {
        return '<span class="badge badge-warning mr-1 mb-1">' + escapeHtml(alert) + '</span>';
      })
      .join('');
  }

  function renderAssessmentDetails(title, entries) {
    if (!entries || !entries.length) {
      return '';
    }
    var items = entries
      .map(function (entry) {
        return '<li><strong>' + escapeHtml(entry.label) + ':</strong> ' + escapeHtml(entry.value) + '</li>';
      })
      .join('');
    return (
      '<div class="mb-2">' +
      '<div class="small text-uppercase text-muted">' + escapeHtml(title) + '</div>' +
      '<ul class="small pl-3 mb-0">' + items + '</ul>' +
      '</div>'
    );
  }

  function renderEducationProgress(progress) {
    if (!progress) {
      return '';
    }

    var summaryParts = [];
    if (progress.programme_type) {
      summaryParts.push('<strong>Programme:</strong> ' + escapeHtml(progress.programme_type));
    }

    if (typeof progress.average_change === 'number') {
      var avgChange = (progress.average_change > 0 ? '+' : '') + formatScore(progress.average_change);
      summaryParts.push('<strong>Average change:</strong> ' + escapeHtml(avgChange));
    }

    if (typeof progress.pre_average === 'number' && typeof progress.post_average === 'number') {
      var preAvg = formatScore(progress.pre_average);
      var postAvg = formatScore(progress.post_average);
      summaryParts.push('<strong>Mean score:</strong> ' + escapeHtml(preAvg) + ' → ' + escapeHtml(postAvg));
    }

    if (progress.trend) {
      summaryParts.push('<strong>Trend:</strong> ' + escapeHtml(progress.trend));
    }

    var summaryHtml = summaryParts.length
      ? '<p class="small mb-1">' + summaryParts.join(' · ') + '</p>'
      : '';

    var subjectsHtml = '';
    if (Array.isArray(progress.subjects) && progress.subjects.length) {
      var subjectItems = progress.subjects
        .map(function (subject) {
          var label = subject.label || subject.field || 'Subject';
          var pre = formatScore(subject.pre);
          var post = formatScore(subject.post);
          var changeValue = subject.change;
          var changeText = changeValue === null || changeValue === undefined
            ? '—'
            : (changeValue > 0 ? '+' : '') + formatScore(changeValue);
          return (
            '<li><strong>' +
            escapeHtml(label) +
            ':</strong> ' +
            escapeHtml(pre) +
            ' → ' +
            escapeHtml(post) +
            ' <span class="text-muted">(Δ ' + escapeHtml(changeText) + ')</span></li>'
          );
        })
        .join('');
      subjectsHtml = '<ul class="small pl-3 mb-1">' + subjectItems + '</ul>';
    }

    var metaItems = [];
    if (progress.participation) {
      metaItems.push('<li><strong>Participation:</strong> ' + escapeHtml(progress.participation) + '</li>');
    }
    if (progress.barriers) {
      var barrierText = progress.barriers;
      if (progress.barriers_detail && barrierText.toLowerCase() === 'other') {
        barrierText = progress.barriers_detail;
      }
      if (barrierText && barrierText.toLowerCase() !== 'no barriers') {
        metaItems.push('<li><strong>Barrier:</strong> ' + escapeHtml(barrierText) + '</li>');
      }
    }
    if (progress.post_test_done) {
      metaItems.push('<li><strong>Post-tests:</strong> ' + escapeHtml(progress.post_test_done) + '</li>');
    }
    if (progress.school_year_completed) {
      metaItems.push('<li><strong>School year completed:</strong> ' + escapeHtml(progress.school_year_completed) + '</li>');
    }
    if (progress.last_updated) {
      metaItems.push('<li><strong>Last updated:</strong> ' + escapeHtml(formatDate(progress.last_updated)) + '</li>');
    }

    var metaHtml = metaItems.length
      ? '<ul class="small pl-3 mb-0">' + metaItems.join('') + '</ul>'
      : '';

    if (!summaryHtml && !subjectsHtml && !metaHtml) {
      return '';
    }

    return (
      '<div class="mb-2">' +
      '<div class="small text-uppercase text-muted">Education progress</div>' +
      summaryHtml +
      subjectsHtml +
      metaHtml +
      '</div>'
    );
  }

  function renderRegistrationHistory(history) {
    if (!history) {
      return '';
    }

    var summaryItems = [];
    if (history.total_registrations !== undefined && history.total_registrations !== null) {
      summaryItems.push('<li><strong>Total registrations:</strong> ' + escapeHtml(history.total_registrations) + '</li>');
    }
    if (history.distinct_rounds !== undefined && history.distinct_rounds !== null) {
      summaryItems.push('<li><strong>Distinct rounds:</strong> ' + escapeHtml(history.distinct_rounds) + '</li>');
    }
    if (Array.isArray(history.years_active) && history.years_active.length) {
      summaryItems.push('<li><strong>Years active:</strong> ' + escapeHtml(history.years_active.join(', ')) + '</li>');
    }
    if (history.longest_consecutive_years) {
      summaryItems.push('<li><strong>Longest consecutive years:</strong> ' + escapeHtml(history.longest_consecutive_years) + '</li>');
    }
    if (history.largest_gap_years) {
      summaryItems.push('<li><strong>Largest gap:</strong> ' + escapeHtml(history.largest_gap_years) + ' year(s)</li>');
    }
    if (history.engagement_span_years) {
      summaryItems.push('<li><strong>Engagement span:</strong> ' + escapeHtml(history.engagement_span_years) + ' year(s)</li>');
    }

    var summaryHtml = summaryItems.length
      ? '<ul class="small pl-3 mb-1">' + summaryItems.join('') + '</ul>'
      : '';

    var entryHtml = '';
    if (Array.isArray(history.entries) && history.entries.length) {
      var entryItems = history.entries
        .map(function (entry) {
          var parts = [];
          parts.push('Registration #' + escapeHtml(entry.registration_id));
          if (entry.round) {
            parts.push(escapeHtml(entry.round));
          } else if (entry.round_year) {
            parts.push('Year ' + escapeHtml(entry.round_year));
          }
          if (entry.registration_date) {
            parts.push('Registered ' + escapeHtml(formatDate(entry.registration_date)));
          }
          if (entry.package_type) {
            parts.push(escapeHtml(entry.package_type));
          }
          if (entry.center) {
            parts.push(escapeHtml(entry.center));
          }
          var text = parts.filter(Boolean).join(' · ');
          if (entry.is_current) {
            text = '<strong>' + text + ' (current)</strong>';
          }
          return '<li>' + text + '</li>';
        })
        .join('');
      entryHtml = '<ul class="small pl-3 mb-0">' + entryItems + '</ul>';
    }

    if (!summaryHtml && !entryHtml) {
      return '';
    }

    return (
      '<div class="mb-2">' +
      '<div class="small text-uppercase text-muted">Registration history</div>' +
      summaryHtml +
      entryHtml +
      '</div>'
    );
  }

  function renderInsights(child) {
    var sections = '';
    sections += renderProgrammeImpactInsights(child.programme_impact);
    sections += renderAssessmentDetails('PSS responses', child.pss_details);
    sections += renderAssessmentDetails('Health & nutrition responses', child.health_details);
    sections += renderAssessmentDetails('Health referrals', child.health_referral_details);
    sections += renderAssessmentDetails('Registration profile', child.registration_details);
    sections += renderEducationProgress(child.education_progress);
    sections += renderRegistrationHistory(child.registration_history);

    if (child.wellbeing_flags && child.wellbeing_flags.length) {
      var flags = child.wellbeing_flags
        .map(function (flag) {
          return '<li>' + escapeHtml(flag) + '</li>';
        })
        .join('');
      sections +=
        '<div class="mb-2">' +
        '<div class="small text-uppercase text-muted">Wellbeing flags</div>' +
        '<ul class="small pl-3 mb-0">' +
        flags +
        '</ul>' +
        '</div>';
    }

    if (!sections) {
      return '<span class="text-muted small">No assessment data</span>';
    }

    return sections;
  }

  function renderLifeQuality(lifeQuality) {
    if (!lifeQuality) {
      return '<span class="text-muted small">No information</span>';
    }

    var label = lifeQuality.label || 'Monitor';
    var score = lifeQuality.score;
    var signals = Array.isArray(lifeQuality.signals) ? lifeQuality.signals : [];

    var html = '';
    html += '<div class="d-flex align-items-baseline mb-1">';
    html +=
      '<span class="badge badge-' + lifeQualityBadgeClass(label) + ' mr-2">' + escapeHtml(label) + '</span>';
    if (score !== undefined && score !== null) {
      html += '<span class="small text-muted">Score: ' + escapeHtml(score) + '</span>';
    }
    html += '</div>';

    if (signals.length) {
      var items = signals
        .map(function (signal) {
          var weight = signal.weight !== undefined && signal.weight !== null ? ' (' + escapeHtml(signal.weight) + ')' : '';
          return '<li>' + escapeHtml(signal.message || '') + weight + '</li>';
        })
        .join('');
      html += '<ul class="small pl-3 mb-0">' + items + '</ul>';
    } else {
      html += '<p class="text-muted small mb-0">No sentiment signals recorded.</p>';
    }

    return html;
  }

  function renderProgrammeImpact(impact) {
    if (!impact) {
      return '<span class="text-muted small">No information</span>';
    }

    var direction = impact.direction || 'mixed';
    var label = impact.label || 'Programme impact';
    var score = impact.score;
    var summary = impact.summary || '';
    var yearsEngaged = Array.isArray(impact.years_engaged) ? impact.years_engaged.length : null;
    var totalRegistrations = impact.total_registrations;
    var spanYears = impact.engagement_span_years;
    var factors = Array.isArray(impact.factors) ? impact.factors : [];

    var html = '';
    html += '<div class="d-flex align-items-baseline mb-1">';
    html +=
      '<span class="badge badge-' + programmeImpactBadgeClass(direction) + ' mr-2">' +
      escapeHtml(label) +
      '</span>';
    if (score !== undefined && score !== null) {
      html += '<span class="small text-muted">Score: ' + escapeHtml(score) + '</span>';
    }
    html += '</div>';

    if (summary) {
      html += '<p class="small mb-1">' + escapeHtml(summary) + '</p>';
    }

    if (yearsEngaged) {
      html += '<div class="small text-muted">Years engaged: ' + escapeHtml(yearsEngaged) + '</div>';
    }

    if (totalRegistrations) {
      html += '<div class="small text-muted">Registrations: ' + escapeHtml(totalRegistrations) + '</div>';
    }

    if (spanYears) {
      html += '<div class="small text-muted">Span: ' + escapeHtml(spanYears) + ' years</div>';
    }

    if (factors.length) {
      var items = factors
        .slice(0, 3)
        .map(function (factor) {
          return '<li>' + escapeHtml(factor.message || '') + '</li>';
        })
        .join('');
      html += '<ul class="small pl-3 mb-0">' + items + '</ul>';
    } else if (!summary) {
      html += '<p class="text-muted small mb-0">No impact factors recorded.</p>';
    }

    return html;
  }

  function renderProgrammeImpactInsights(impact) {
    if (!impact) {
      return '';
    }

    var factors = Array.isArray(impact.factors) ? impact.factors : [];
    var summary = impact.summary || '';
    var yearsEngaged = Array.isArray(impact.years_engaged) ? impact.years_engaged : [];
    var spanYears = impact.engagement_span_years;
    var totalRegistrations = impact.total_registrations;

    var meta = '';
    if (summary) {
      meta += '<p class="small mb-1">' + escapeHtml(summary) + '</p>';
    }
    if (yearsEngaged.length) {
      var yearList = yearsEngaged
        .map(function (year) {
          return escapeHtml(year);
        })
        .join(', ');
      meta += '<div class="small text-muted mb-1">Years active: ' + yearList + '</div>';
    }
    if (totalRegistrations) {
      meta += '<div class="small text-muted mb-1">Registrations: ' + escapeHtml(totalRegistrations) + '</div>';
    }
    if (spanYears) {
      meta += '<div class="small text-muted mb-1">Span across ' + escapeHtml(spanYears) + ' years</div>';
    }

    var items = factors
      .map(function (factor) {
        var weight =
          factor.weight !== undefined && factor.weight !== null
            ? ' (' + escapeHtml(factor.weight) + ')'
            : '';
        return '<li>' + escapeHtml(factor.message || '') + weight + '</li>';
      })
      .join('');

    if (!items) {
      items = '<li class="text-muted">No impact drivers recorded.</li>';
    }

    return (
      '<div class="mb-2">' +
      '<div class="small text-uppercase text-muted">Programme impact</div>' +
      meta +
      '<ul class="small pl-3 mb-0">' +
      items +
      '</ul>' +
      '</div>'
    );
  }

  function renderChildren(children) {
    if (!children || !children.length) {
      return '<p class="text-muted mb-0">No children met the selected criteria.</p>';
    }

    var cards = children
      .map(function (child, index) {
        var attendance = child.attendance || {};
        var services = child.services || {};
        var lifeQuality = child.life_quality || null;
        var programmeImpact = child.programme_impact || null;
        var name = child.child_name || 'Unknown child';
        var gender = child.gender ? ' (' + escapeHtml(child.gender) + ')' : '';
        var programme = child.education_programme
          ? '<div class="small text-muted">Education programme: ' + escapeHtml(child.education_programme) + '</div>'
          : '';
        var ageInfo =
          child.age !== undefined && child.age !== null ? '<div class="small">Age: ' + escapeHtml(child.age) + '</div>' : '';
        var registrationId = child.registration_id ? escapeHtml(child.registration_id) : '—';
        var riskScore = child.risk_score !== undefined && child.risk_score !== null ? escapeHtml(child.risk_score) : '—';
        var rankBadge = '<span class="badge badge-primary badge-pill mr-2">#' + (index + 1) + '</span>';
        var riskBadge = '<span class="badge badge-danger badge-pill">Risk score ' + riskScore + '</span>';
        var lifeQualityBadge = lifeQuality && lifeQuality.label
          ? '<span class="badge badge-' + lifeQualityBadgeClass(lifeQuality.label) + ' badge-pill">' +
            escapeHtml(lifeQuality.label) +
            '</span>'
          : '';

        return (
          '<div class="priority-child-card card mb-3 shadow-sm">' +
          '<div class="card-body">' +
          '<div class="priority-card-header d-flex justify-content-between align-items-start flex-wrap">' +
          '<div class="mb-2 mr-3">' +
          '<div class="d-flex align-items-center flex-wrap">' +
          rankBadge +
          '<h5 class="mb-0">' + escapeHtml(name) + gender + '</h5>' +
          '</div>' +
          '<div class="small text-muted mt-1">Registration #' + registrationId + '</div>' +
          ageInfo +
          programme +
          renderFocusTopics(child.focus_topics) +
          '</div>' +
          '<div class="text-right mb-2 ml-auto">' +
          riskBadge +
          (lifeQualityBadge ? '<div class="mt-2">' + lifeQualityBadge + '</div>' : '') +
          '</div>' +
          '</div>' +
          '<div class="row priority-metric-row">' +
          '<div class="col-xl-3 col-lg-6 col-md-6 mb-3">' +
          '<div class="priority-metric h-100">' +
          '<div class="priority-metric-title small text-uppercase text-muted">Attendance</div>' +
          renderAttendanceSummary(attendance) +
          '</div>' +
          '</div>' +
          '<div class="col-xl-3 col-lg-6 col-md-6 mb-3">' +
          '<div class="priority-metric h-100">' +
          '<div class="priority-metric-title small text-uppercase text-muted">Services</div>' +
          renderServiceSummary(services) +
          '</div>' +
          '</div>' +
          '<div class="col-xl-3 col-lg-6 col-md-6 mb-3">' +
          '<div class="priority-metric h-100">' +
          '<div class="priority-metric-title small text-uppercase text-muted">Life quality</div>' +
          renderLifeQuality(lifeQuality) +
          '</div>' +
          '</div>' +
          '<div class="col-xl-3 col-lg-6 col-md-6 mb-3">' +
          '<div class="priority-metric h-100">' +
          '<div class="priority-metric-title small text-uppercase text-muted">Programme impact</div>' +
          renderProgrammeImpact(programmeImpact) +
          '</div>' +
          '</div>' +
          '</div>' +
          '<div class="priority-section mt-3">' +
          '<div class="priority-section-title small text-uppercase text-muted">Insights &amp; history</div>' +
          '<div class="priority-section-body small">' + renderInsights(child) + '</div>' +
          '</div>' +
          '<div class="priority-section mt-3">' +
          '<div class="priority-section-title small text-uppercase text-muted">Alerts</div>' +
          '<div class="priority-alerts">' + renderAlerts(child.alerts) + '</div>' +
          '</div>' +
          '</div>' +
          '</div>'
        );
      })
      .join('');

    return '<div class="priority-children-list">' + cards + '</div>';
  }

  function buildMetadata(payload) {
    var parts = [];
    if (payload.count !== undefined) {
      parts.push(escapeHtml(payload.count) + ' children');
    }
    if (payload.limit !== undefined) {
      parts.push('limit ' + escapeHtml(payload.limit));
    }
    if (payload.question) {
      parts.push('focus: ' + escapeHtml(payload.question));
    }
    if (payload.generated_at) {
      var generatedDate = new Date(payload.generated_at);
      if (!isNaN(generatedDate.getTime())) {
        parts.push(generatedDate.toLocaleString());
      }
    }
    if (payload.model) {
      parts.push('model: ' + escapeHtml(payload.model));
    }
    return parts.join(' • ');
  }

  function parseRegistrationInput(raw) {
    if (!raw) {
      return [];
    }
    return raw
      .split(/[\n,]/)
      .map(function (value) {
        return value.trim();
      })
      .filter(function (value) {
        return value.length > 0;
      });
  }

  function clamp(value, min, max) {
    var numeric = parseInt(value, 10);
    if (isNaN(numeric)) {
      return min;
    }
    return Math.max(min, Math.min(max, numeric));
  }

  function init() {
    var container = document.getElementById('health-agent-app');
    if (!container) {
      return;
    }

    var endpoint = container.dataset.endpoint;
    if (!endpoint) {
      return;
    }

    var defaultLimit = parseInt(container.dataset.defaultLimit || '5', 10);
    var maxLimit = parseInt(container.dataset.maxLimit || '20', 10);

    var form = qs(container, '#health-agent-form');
    var idsField = qs(container, '#health-agent-registration-ids');
    var limitField = qs(container, '#health-agent-limit');
    var questionField = qs(container, '#health-agent-question');
    var resetButton = qs(container, '#health-agent-reset');
    var statusBox = document.getElementById('health-agent-status');
    var resultsPanel = document.getElementById('health-agent-results');
    var analysisContainer = document.getElementById('health-agent-analysis');
    var childrenContainer = document.getElementById('health-agent-children');
    var metadataContainer = document.getElementById('health-agent-metadata');

    if (!limitField.value) {
      limitField.value = defaultLimit;
    }

    function showStatus(message, level) {
      if (!statusBox) {
        return;
      }
      if (!message) {
        statusBox.classList.add('d-none');
        statusBox.textContent = '';
        statusBox.className = 'alert d-none';
        return;
      }
      var levelClass = level === 'error' ? 'alert-danger' : level === 'warning' ? 'alert-warning' : 'alert-info';
      statusBox.className = 'alert ' + levelClass;
      statusBox.textContent = message;
      statusBox.classList.remove('d-none');
    }

    function showResults(payload) {
      if (!resultsPanel) {
        return;
      }
      resultsPanel.classList.remove('d-none');
      analysisContainer.innerHTML = renderMarkdown(payload.analysis || '');
      childrenContainer.innerHTML = renderChildren(payload.children || []);
      metadataContainer.textContent = buildMetadata(payload);
      if (questionField && payload.question !== undefined) {
        questionField.value = payload.question;
      }
      if (payload.error) {
        showStatus(payload.error, 'warning');
      } else {
        showStatus('Assessment updated successfully.', 'info');
      }
    }

    function resetForm() {
      if (idsField) {
        idsField.value = '';
      }
      if (limitField) {
        limitField.value = defaultLimit;
      }
      if (childrenContainer) {
        childrenContainer.innerHTML = '';
      }
      if (analysisContainer) {
        analysisContainer.innerHTML = '';
      }
      if (metadataContainer) {
        metadataContainer.textContent = '';
      }
      if (questionField) {
        questionField.value = '';
      }
      if (resultsPanel) {
        resultsPanel.classList.add('d-none');
      }
      showStatus('', 'info');
    }

    function handleSubmit(event) {
      event.preventDefault();
      var registrationInput = idsField ? idsField.value : '';
      var limitInput = limitField ? limitField.value : defaultLimit;
      var questionInput = questionField ? questionField.value : '';
      var trimmedQuestion = questionInput ? questionInput.trim() : '';
      var limitValue = clamp(limitInput, 1, maxLimit);

      if (limitField) {
        limitField.value = limitValue;
      }

      var payload = {
        limit: limitValue,
      };

      var registrationIds = parseRegistrationInput(registrationInput);
      if (registrationIds.length) {
        payload.registration_ids = registrationIds;
      }
      if (trimmedQuestion) {
        payload.question = trimmedQuestion;
      }

      showStatus('Fetching recommendations…', 'info');

      fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken') || '',
        },
        body: JSON.stringify(payload),
        credentials: 'same-origin',
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error('Failed to fetch health support insights.');
          }
          return response.json();
        })
        .then(function (data) {
          showResults(data);
        })
        .catch(function (error) {
          showStatus(error.message || 'Unable to fetch data.', 'error');
        });
    }

    if (form) {
      form.addEventListener('submit', handleSubmit);
    }

    if (resetButton) {
      resetButton.addEventListener('click', function () {
        resetForm();
      });
    }

    resetForm();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
