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

  function renderServiceSummary(services) {
    if (!services) {
      return '';
    }
    var keys = ['pss', 'health', 'support'];
    var html = '<div class="row">';
    keys.forEach(function (key) {
      if (!services[key]) {
        return;
      }
      var summary = services[key];
      html += '<div class="col-md-4 col-sm-6 mb-2">';
      html += '<div class="border rounded p-2 h-100">';
      html += '<div class="small text-uppercase text-muted">' + key.toUpperCase() + '</div>';
      html += '<div class="d-flex justify-content-between align-items-baseline">';
      var completed = summary.completed || 0;
      var total = summary.total || 0;
      var pending = summary.required_pending || 0;
      html += '<span class="font-weight-bold">' + escapeHtml(completed) + '/' + escapeHtml(total) + '</span>';
      html += '<span class="badge badge-' + (pending ? 'danger' : 'success') + '">';
      html += pending ? escapeHtml(pending) + ' pending' : 'Up to date';
      html += '</span>';
      html += '</div>';
      html += '</div>';
      html += '</div>';
    });
    html += '</div>';
    if (services.overall_pending_required) {
      html += '<p class="small text-danger mb-0">' + escapeHtml(services.overall_pending_required) + ' required services still pending.</p>';
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

  function renderChildren(children) {
    if (!children || !children.length) {
      return '<p class="text-muted mb-0">No children met the selected criteria.</p>';
    }

    var rows = children
      .map(function (child) {
        var attendance = child.attendance || {};
        var services = child.services || {};
        var name = child.child_name || 'Unknown child';
        var gender = child.gender ? ' (' + escapeHtml(child.gender) + ')' : '';
        var programme = child.education_programme ? '<div class="small text-muted">' + escapeHtml(child.education_programme) + '</div>' : '';
        var absenceDate = attendance.most_recent_absence ? formatDate(attendance.most_recent_absence) : '—';
        var ageInfo = child.age !== undefined && child.age !== null ? '<div class="small">Age: ' + escapeHtml(child.age) + '</div>' : '';

        return (
          '<tr>' +
          '<td class="align-middle"><strong>' + escapeHtml(child.risk_score) + '</strong></td>' +
          '<td class="align-middle">' +
          '<div class="font-weight-bold">' + escapeHtml(name) + gender + '</div>' +
          '<div class="small text-muted">Registration #' + escapeHtml(child.registration_id) + '</div>' +
          ageInfo +
          programme +
          '</td>' +
          '<td class="align-middle">' +
          '<div><strong>' + formatPercent(attendance.attendance_rate) + '</strong></div>' +
          '<div class="small text-muted">' + escapeHtml(attendance.attended_sessions || 0) + ' / ' + escapeHtml(attendance.total_sessions || 0) + ' sessions</div>' +
          '<div class="small">Last absence: ' + absenceDate + '</div>' +
          '</td>' +
          '<td class="align-middle">' + renderServiceSummary(services) + '</td>' +
          '<td class="align-middle" style="min-width: 180px;">' + renderAlerts(child.alerts) + '</td>' +
          '</tr>'
        );
      })
      .join('');

    return (
      '<div class="table-responsive">' +
      '<table class="table table-striped table-sm mb-0">' +
      '<thead>' +
      '<tr>' +
      '<th style="width: 70px;">Risk</th>' +
      '<th>Child</th>' +
      '<th>Attendance</th>' +
      '<th>Services</th>' +
      '<th>Alerts</th>' +
      '</tr>' +
      '</thead>' +
      '<tbody>' +
      rows +
      '</tbody>' +
      '</table>' +
      '</div>'
    );
  }

  function buildMetadata(payload) {
    var parts = [];
    if (payload.count !== undefined) {
      parts.push(escapeHtml(payload.count) + ' children');
    }
    if (payload.limit !== undefined) {
      parts.push('limit ' + escapeHtml(payload.limit));
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
      if (resultsPanel) {
        resultsPanel.classList.add('d-none');
      }
      showStatus('', 'info');
    }

    function handleSubmit(event) {
      event.preventDefault();
      var registrationInput = idsField ? idsField.value : '';
      var limitInput = limitField ? limitField.value : defaultLimit;
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
