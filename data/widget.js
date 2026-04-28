/* ============================================================
 * GA! Think Tank — International Affairs Tracker (widget JS)
 * Hosted via jsDelivr from github.com/GAthinktank/ga-events-feed
 *
 * The companion HTML lives in a Custom HTML block on the
 * WordPress site and contains only the markup + a <script src>
 * tag pointing to this file.
 * ============================================================ */
(function () {
  'use strict';

  // Fetch JSON directly from GitHub raw (no aggressive caching) so the
  // page always reflects the latest scrape. The widget.js itself stays
  // on jsDelivr for CDN speed.
  var DATA_BASE = 'https://raw.githubusercontent.com/GAthinktank/ga-events-feed/main/data';
  var CAL_URL  = DATA_BASE + '/calendar.json';
  var PUBS_URL = DATA_BASE + '/publications.json';

  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }

  var root = document.getElementById('ga-feed');
  if (!root) {
    console.warn('[ga-feed] No #ga-feed element found on page');
    return;
  }

  var MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  var MONTHS_LONG = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  var DOW = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' })[c];
    });
  }
  function parseDate(s) {
    if (!s) return null;
    var d = new Date(String(s).slice(0, 10) + 'T00:00:00');
    return isNaN(d) ? null : d;
  }
  function fmtRange(ev) {
    var a = parseDate(ev.date); if (!a) return '';
    var b = parseDate(ev.end_date) || a;
    if (+a === +b) return a.getDate() + ' ' + MONTHS_LONG[a.getMonth()] + ' ' + a.getFullYear();
    if (a.getMonth() === b.getMonth() && a.getFullYear() === b.getFullYear())
      return a.getDate() + '\u2013' + b.getDate() + ' ' + MONTHS_LONG[a.getMonth()] + ' ' + a.getFullYear();
    return a.getDate() + ' ' + MONTHS[a.getMonth()] + ' \u2013 ' + b.getDate() + ' ' + MONTHS[b.getMonth()] + ' ' + a.getFullYear();
  }

  var now = new Date();
  var state = {
    tab: 'calendar',
    cal: { view: 'list', region: '', theme: '', month: now.getMonth(), year: now.getFullYear(), data: [] },
    pub: { region: '', theme: '', type: '', data: [] }
  };

  // ----- Tabs -----
  $$('.ga-tabs button').forEach(function (btn) {
    btn.addEventListener('click', function () {
      $$('.ga-tabs button').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      var tab = btn.getAttribute('data-tab');
      state.tab = tab;
      $$('.ga-pane').forEach(function (p) {
        p.classList.toggle('active', p.getAttribute('data-pane') === tab);
      });
    });
  });

  // ===== CALENDAR =====
  function getCalFiltered() {
    var today = new Date(); today.setHours(0, 0, 0, 0);
    return state.cal.data
      .filter(function (e) { return parseDate(e.date); })
      .filter(function (e) {
        var end = parseDate(e.end_date) || parseDate(e.date);
        return end >= today;
      })
      .filter(function (e) { return !state.cal.region || e.region === state.cal.region; })
      .filter(function (e) { return !state.cal.theme  || e.theme  === state.cal.theme; })
      .sort(function (a, b) { return parseDate(a.date) - parseDate(b.date); });
  }

  function renderCalFeatured() {
    var featured = getCalFiltered().filter(function (e) { return e.featured; }).slice(0, 3);
    var wrap = $('#ga-cal-featured');
    var grid = $('#ga-cal-featured-grid');
    if (!featured.length) { wrap.hidden = true; return; }
    wrap.hidden = false;
    grid.innerHTML = featured.map(function (ev) {
      var titleHtml = ev.link
        ? '<a href="' + esc(ev.link) + '" target="_blank" rel="noopener">' + esc(ev.title) + '</a>'
        : esc(ev.title);
      var approx = ev.confirmed ? '' : '<span class="ga-approx">approx. dates</span>';
      return '<article class="ga-fcard">' +
        '<p class="ga-fc-date">' + fmtRange(ev) + approx + '</p>' +
        '<h3>' + titleHtml + '</h3>' +
        '<p class="ga-fc-meta">' + (ev.location ? esc(ev.location) : '') + (ev.organizer ? ' &middot; ' + esc(ev.organizer) : '') + '</p>' +
        (ev.summary ? '<p class="ga-fc-summary">' + esc(ev.summary) + '</p>' : '') +
        '</article>';
    }).join('');
  }

  function renderCalList() {
    var list = getCalFiltered();
    var el = $('#ga-cal-list');
    if (!list.length) { el.innerHTML = '<div class="ga-empty">No upcoming events match your filters.</div>'; return; }
    el.innerHTML = list.map(function (ev) {
      var d = parseDate(ev.date);
      var titleHtml = ev.link
        ? '<a href="' + esc(ev.link) + '" target="_blank" rel="noopener">' + esc(ev.title) + '</a>'
        : esc(ev.title);
      var metaParts = [];
      if (ev.location) metaParts.push('<strong>' + esc(ev.location) + '</strong>');
      if (ev.organizer) metaParts.push(esc(ev.organizer));
      if (ev.end_date && ev.end_date !== ev.date) metaParts.push('through ' + fmtRange(ev));
      var meta = metaParts.join(' &middot; ');
      var approx = ev.confirmed ? '' : '<span class="ga-approx">approx.</span>';
      return '<div class="ga-row">' +
        '<div class="ga-date">' +
          '<span class="ga-day">' + d.getDate() + '</span>' +
          '<span class="ga-mon">' + MONTHS[d.getMonth()] + '</span>' +
          '<span class="ga-yr">' + d.getFullYear() + (approx ? ' ' + approx : '') + '</span>' +
        '</div>' +
        '<div class="ga-body">' +
          '<h3>' + titleHtml + '</h3>' +
          (meta ? '<p class="ga-meta">' + meta + '</p>' : '') +
          (ev.summary ? '<p class="ga-summary">' + esc(ev.summary) + '</p>' : '') +
        '</div>' +
        '<div class="ga-tags">' +
          (ev.region ? '<span class="ga-tag region">' + esc(ev.region) + '</span>' : '') +
          (ev.theme  ? '<span class="ga-tag theme">'  + esc(ev.theme)  + '</span>' : '') +
        '</div>' +
      '</div>';
    }).join('');
  }

  function renderCalMonth() {
    var year = state.cal.year, month = state.cal.month;
    $('#ga-cal-month-name').textContent = MONTHS_LONG[month] + ' ' + year;
    var grid = $('#ga-cal-grid');
    var html = DOW.map(function (d) { return '<div class="ga-cal-dow">' + d + '</div>'; }).join('');
    var first = new Date(year, month, 1);
    var lead = (first.getDay() + 6) % 7;
    var dim = new Date(year, month + 1, 0).getDate();
    var prevDim = new Date(year, month, 0).getDate();
    var cells = Math.ceil((lead + dim) / 7) * 7;
    var today = new Date(); today.setHours(0, 0, 0, 0);
    var events = getCalFiltered();
    for (var i = 0; i < cells; i++) {
      var inMonth = i >= lead && i < lead + dim;
      var dayNum = inMonth ? (i - lead + 1)
                 : (i < lead ? prevDim - lead + i + 1 : i - lead - dim + 1);
      var cellDate = inMonth ? new Date(year, month, dayNum) : null;
      var isToday = cellDate && +cellDate === +today;
      var dayEvents = cellDate ? events.filter(function (ev) {
        var a = parseDate(ev.date), b = parseDate(ev.end_date) || a;
        return cellDate >= a && cellDate <= b;
      }) : [];
      var cls = ['ga-cal-day'];
      if (!inMonth) cls.push('other');
      if (isToday) cls.push('today');
      if (dayEvents.length) cls.push('has');
      var dots = dayEvents.slice(0, 3).map(function (e) {
        return '<span class="ga-cal-dot' + (e.featured ? ' featured' : '') + (e.confirmed ? '' : ' unconfirmed') + '"></span>';
      }).join('');
      var pad2 = function (n) { return String(n).padStart(2, '0'); };
      var localISO = cellDate.getFullYear() + '-' + pad2(cellDate.getMonth() + 1) + '-' + pad2(cellDate.getDate());
      var dataAttr = dayEvents.length ? ' data-date="' + localISO + '"' : '';
      html += '<div class="' + cls.join(' ') + '"' + dataAttr + '><span class="ga-day-num">' + dayNum + '</span>' + (dots ? '<div>' + dots + '</div>' : '') + '</div>';
    }
    grid.innerHTML = html;
    $$('#ga-cal-grid .has').forEach(function (cell) {
      cell.addEventListener('click', function () {
        var dateStr = cell.getAttribute('data-date');
        var d = parseDate(dateStr);
        var matching = events.filter(function (ev) {
          var a = parseDate(ev.date), b = parseDate(ev.end_date) || a;
          return d >= a && d <= b;
        });
        var wrap = $('#ga-cal-day-events');
        wrap.classList.remove('empty');
        wrap.innerHTML = '<h3>' + d.getDate() + ' ' + MONTHS_LONG[d.getMonth()] + ' ' + d.getFullYear() + '</h3>' +
          matching.map(function (ev) {
            var titleHtml = ev.link
              ? '<a href="' + esc(ev.link) + '" target="_blank" rel="noopener" class="ga-day-link">' + esc(ev.title) + '</a>'
              : esc(ev.title);
            return '<div class="ga-day-item">' +
              '<div class="ga-day-title">' + titleHtml + '</div>' +
              '<div class="ga-day-meta">' + (ev.location ? esc(ev.location) : '') + (ev.organizer ? ' &middot; ' + esc(ev.organizer) : '') + '</div>' +
              (ev.summary ? '<p class="ga-day-summary">' + esc(ev.summary) + '</p>' : '') +
            '</div>';
          }).join('');
        wrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });
    });
  }

  function renderCalCount() {
    var n = getCalFiltered().length;
    $('#ga-cal-count').textContent = n + ' upcoming event' + (n === 1 ? '' : 's');
  }

  function renderCal() {
    renderCalCount();
    if (state.cal.view === 'list') {
      renderCalFeatured();
      $('#ga-cal-list').style.display = '';
      $('#ga-cal-month').classList.remove('active');
      renderCalList();
    } else {
      $('#ga-cal-featured').hidden = true;
      $('#ga-cal-list').style.display = 'none';
      $('#ga-cal-month').classList.add('active');
      $('#ga-cal-day-events').classList.add('empty');
      renderCalMonth();
    }
  }

  // ===== PUBLICATIONS =====
  function getPubFiltered() {
    return state.pub.data
      .filter(function (p) { return !state.pub.region || p.region === state.pub.region; })
      .filter(function (p) { return !state.pub.theme  || p.theme  === state.pub.theme; })
      .filter(function (p) { return !state.pub.type   || p.source_type === state.pub.type; });
  }

  function renderPubs() {
    var list = getPubFiltered();
    $('#ga-pub-count').textContent = list.length + ' publication' + (list.length === 1 ? '' : 's');
    var el = $('#ga-pub-list');
    if (!list.length) { el.innerHTML = '<div class="ga-empty">No publications match your filters.</div>'; return; }
    el.innerHTML = list.slice(0, 150).map(function (p) {
      var d = parseDate(p.date);
      var titleHtml = p.link
        ? '<a href="' + esc(p.link) + '" target="_blank" rel="noopener">' + esc(p.title) + '</a>'
        : esc(p.title);
      var dayBlock = d
        ? '<span class="ga-day">' + d.getDate() + '</span><span class="ga-mon">' + MONTHS[d.getMonth()] + '</span><span class="ga-yr">' + d.getFullYear() + '</span>'
        : '<span class="ga-mon ga-no-date">no date</span>';
      return '<div class="ga-row">' +
        '<div class="ga-date">' + dayBlock + '</div>' +
        '<div class="ga-body">' +
          '<h3>' + titleHtml + '</h3>' +
          '<p class="ga-meta"><span class="ga-source">' + esc(p.source) + '</span></p>' +
          (p.summary ? '<p class="ga-summary">' + esc(p.summary) + '</p>' : '') +
        '</div>' +
        '<div class="ga-tags">' +
          (p.region ? '<span class="ga-tag region">' + esc(p.region) + '</span>' : '') +
          (p.theme  ? '<span class="ga-tag theme">'  + esc(p.theme)  + '</span>' : '') +
          (p.lang && p.lang !== 'en' ? '<span class="ga-tag lang">' + esc(p.lang.toUpperCase()) + '</span>' : '') +
        '</div>' +
      '</div>';
    }).join('');
  }

  // ===== Wire up filters =====
  $$('.ga-views button').forEach(function (btn) {
    btn.addEventListener('click', function () {
      $$('.ga-views button').forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      state.cal.view = btn.getAttribute('data-view');
      renderCal();
    });
  });
  $('#ga-cal-region').addEventListener('change', function (e) { state.cal.region = e.target.value; renderCal(); });
  $('#ga-cal-theme' ).addEventListener('change', function (e) { state.cal.theme  = e.target.value; renderCal(); });
  $('#ga-cal-prev').addEventListener('click', function () {
    state.cal.month--;
    if (state.cal.month < 0) { state.cal.month = 11; state.cal.year--; }
    renderCal();
  });
  $('#ga-cal-next').addEventListener('click', function () {
    state.cal.month++;
    if (state.cal.month > 11) { state.cal.month = 0; state.cal.year++; }
    renderCal();
  });
  $('#ga-pub-region').addEventListener('change', function (e) { state.pub.region = e.target.value; renderPubs(); });
  $('#ga-pub-theme' ).addEventListener('change', function (e) { state.pub.theme  = e.target.value; renderPubs(); });
  $('#ga-pub-type'  ).addEventListener('change', function (e) { state.pub.type   = e.target.value; renderPubs(); });

  // ===== Fetch =====
  function setUpdated(meta) {
    if (!meta || !meta.generated_at) { $('#ga-updated').textContent = ''; return; }
    var d = new Date(meta.generated_at);
    function pad(n) { return String(n).padStart(2, '0'); }
    var fmt = d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate()) + ' ' + pad(d.getUTCHours()) + ':' + pad(d.getUTCMinutes()) + ' UTC';
    $('#ga-updated').textContent = 'Updated ' + fmt + (meta.stats ? ' \u00b7 ' + meta.stats.ok + '/' + meta.source_count + ' sources' : '');
  }

  function loadCalendar() {
    fetch(CAL_URL + '?t=' + Date.now())
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (data) {
        state.cal.data = data.items || [];
        setUpdated(data.meta);
        renderCal();
      })
      .catch(function (e) {
        console.error('[ga-feed] Calendar load failed:', e);
        $('#ga-cal-list').innerHTML = '<div class="ga-empty">Could not load calendar. The feed may be initialising \u2014 try again in a few minutes.</div>';
      });
  }
  function loadPubs() {
    fetch(PUBS_URL + '?t=' + Date.now())
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (data) {
        state.pub.data = data.items || [];
        renderPubs();
      })
      .catch(function (e) {
        console.error('[ga-feed] Publications load failed:', e);
        $('#ga-pub-list').innerHTML = '<div class="ga-empty">Could not load publications. The feed may be initialising \u2014 try again in a few minutes.</div>';
      });
  }

  loadCalendar();
  loadPubs();
})();
