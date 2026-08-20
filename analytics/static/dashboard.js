(function () {
  "use strict";

  const API_ROOT = "/admin/analytics/api";
  const numberFormat = new Intl.NumberFormat("en-US");
  const decimalFormat = new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 });
  const shortDateFormat = new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" });
  const longDateFormat = new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" });
  const dateTimeFormat = new Intl.DateTimeFormat("en-US", {
    month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit"
  });
  const svgNamespace = "http://www.w3.org/2000/svg";

  const state = {
    report: null,
    activeBreakdown: "devices",
    activePreset: "7-days",
    requestController: null
  };

  const byId = (id) => document.getElementById(id);

  function localDate(value) {
    return new Date(`${value}T12:00:00`);
  }

  function inputDate(value) {
    const year = value.getFullYear();
    const month = String(value.getMonth() + 1).padStart(2, "0");
    const day = String(value.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  function addDays(value, amount) {
    const copy = new Date(value);
    copy.setDate(copy.getDate() + amount);
    return copy;
  }

  function formatInteger(value) {
    return numberFormat.format(Number(value || 0));
  }

  function formatDuration(seconds) {
    const total = Number(seconds || 0);
    if (total < 60) return `${Math.round(total)} sec`;
    const minutes = Math.floor(total / 60);
    const remainder = Math.round(total % 60);
    return remainder ? `${minutes}m ${remainder}s` : `${minutes} min`;
  }

  function formatBytes(value) {
    const bytes = Number(value || 0);
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${decimalFormat.format(bytes / 1024)} KB`;
    return `${decimalFormat.format(bytes / (1024 * 1024))} MB`;
  }

  function formatTimestamp(value) {
    if (!value) return "Not available";
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? String(value) : dateTimeFormat.format(parsed);
  }

  function clearNode(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function textElement(tagName, text, className) {
    const element = document.createElement(tagName);
    element.textContent = text;
    if (className) element.className = className;
    return element;
  }

  function svgElement(tagName, attributes) {
    const element = document.createElementNS(svgNamespace, tagName);
    Object.entries(attributes || {}).forEach(([name, value]) => element.setAttribute(name, String(value)));
    return element;
  }

  function setLoading(isLoading) {
    const status = byId("report-status");
    status.classList.toggle("is-loading", isLoading);
    status.classList.remove("is-error");
    status.textContent = isLoading ? "Updating" : "Current";
    byId("refresh-report").disabled = isLoading;
  }

  function showError(message) {
    const status = byId("report-status");
    status.classList.remove("is-loading");
    status.classList.add("is-error");
    status.textContent = "Unavailable";
    byId("fatal-error-message").textContent = message;
    byId("fatal-error").hidden = false;
    byId("refresh-report").disabled = false;
  }

  async function loadReport(parameters) {
    if (state.requestController) state.requestController.abort();
    state.requestController = new AbortController();
    setLoading(true);
    byId("fatal-error").hidden = true;

    const query = new URLSearchParams(parameters || {});
    if (!query.has("granularity")) query.set("granularity", "auto");
    try {
      const response = await fetch(`${API_ROOT}/report?${query.toString()}`, {
        credentials: "same-origin",
        headers: { "Accept": "application/json" },
        signal: state.requestController.signal
      });
      let payload = null;
      try {
        payload = await response.json();
      } catch (_error) {
        payload = null;
      }
      if (!response.ok) {
        throw new Error(payload && payload.error ? payload.error : `Request failed with status ${response.status}`);
      }
      state.report = payload;
      renderReport(payload);
      setLoading(false);
      byId("last-refreshed").textContent = `Refreshed ${dateTimeFormat.format(new Date())}`;
      const period = payload.summary.period;
      const address = new URL(window.location.href);
      address.searchParams.set("start", period.start);
      address.searchParams.set("end", period.end);
      window.history.replaceState({}, "", address);
    } catch (error) {
      if (error.name === "AbortError") return;
      showError(error.message || "Please try again.");
    }
  }

  function renderReport(report) {
    const period = report.summary.period;
    byId("range-start").value = period.start;
    byId("range-end").value = period.end;
    const start = localDate(period.start);
    const end = localDate(period.end);
    const sameYear = start.getFullYear() === end.getFullYear();
    const startLabel = sameYear ? shortDateFormat.format(start) : longDateFormat.format(start);
    byId("range-summary").textContent = `${startLabel} to ${longDateFormat.format(end)} (${period.days} ${period.days === 1 ? "day" : "days"})`;

    renderSummary(report.summary);
    renderTrend(report.trend);
    renderPages(report.pages);
    renderPathways(report.three_e);
    renderFeatures(report.features);
    renderBreakdown(report[state.activeBreakdown]);
    renderHours(report.time_patterns.hourly);
    renderWeekdays(report.time_patterns.weekday);
    renderHeatmap(report.time_patterns.heatmap);
    renderTechnical(report.technical_health, report.diagnostics);
  }

  function renderSummary(summary) {
    const current = summary.current;
    const changes = summary.change_percent;
    const metrics = [
      ["visitors", "metric-visitors", "change-visitors", "estimated_visitors", formatInteger],
      ["views", "metric-page-views", "change-page-views", "page_views", formatInteger],
      ["sessions", "metric-sessions", "change-sessions", "sessions", formatInteger],
      ["depth", "metric-pages-session", "change-pages-session", "pages_per_session", decimalFormat.format.bind(decimalFormat)],
      ["duration", "metric-duration", "change-duration", "average_session_duration_seconds", formatDuration],
      ["requests", "metric-requests", "change-requests", "total_requests", formatInteger]
    ];

    metrics.forEach(([_name, valueId, changeId, key, formatter]) => {
      byId(valueId).textContent = formatter(current[key]);
      const changeNode = byId(changeId);
      changeNode.classList.remove("is-positive", "is-negative");
      const change = changes[key];
      if (change === null || typeof change === "undefined") {
        changeNode.textContent = "No prior baseline";
      } else {
        const sign = change > 0 ? "+" : "";
        changeNode.textContent = `${sign}${decimalFormat.format(change)}% vs previous`;
        if (change > 0) changeNode.classList.add("is-positive");
        if (change < 0) changeNode.classList.add("is-negative");
      }
    });
  }

  function addSvgText(svg, x, y, value, anchor) {
    const text = svgElement("text", {
      x, y, fill: "#adc1b5", "font-size": 12, "text-anchor": anchor || "start"
    });
    text.textContent = value;
    svg.appendChild(text);
  }

  function renderTrend(trend) {
    const svg = byId("trend-chart");
    const empty = byId("trend-empty");
    clearNode(svg);
    const points = trend.points || [];
    empty.hidden = points.length > 0;
    svg.hidden = points.length === 0;
    if (!points.length) return;

    const width = 900;
    const height = 300;
    const margin = { left: 52, right: 24, top: 18, bottom: 46 };
    const plotWidth = width - margin.left - margin.right;
    const plotHeight = height - margin.top - margin.bottom;
    const maxValue = Math.max(1, ...points.flatMap((point) => [point.page_views, point.estimated_visitors]));
    const x = (index) => margin.left + (points.length === 1 ? plotWidth / 2 : (index / (points.length - 1)) * plotWidth);
    const y = (value) => margin.top + plotHeight - (Number(value) / maxValue) * plotHeight;

    for (let index = 0; index <= 4; index += 1) {
      const value = Math.round((maxValue / 4) * index);
      const lineY = y(value);
      svg.appendChild(svgElement("line", {
        x1: margin.left, y1: lineY, x2: width - margin.right, y2: lineY,
        stroke: "rgba(255,255,255,.10)", "stroke-width": 1
      }));
      addSvgText(svg, margin.left - 10, lineY + 4, formatInteger(value), "end");
    }

    const series = [
      { key: "page_views", color: "#f0c742" },
      { key: "estimated_visitors", color: "#4fd1b2" }
    ];
    series.forEach((item) => {
      const pathData = points.map((point, index) => `${index ? "L" : "M"}${x(index)},${y(point[item.key])}`).join(" ");
      if (item.key === "page_views") {
        const areaData = `${pathData} L${x(points.length - 1)},${margin.top + plotHeight} L${x(0)},${margin.top + plotHeight} Z`;
        svg.appendChild(svgElement("path", {
          d: areaData, fill: "rgba(240,199,66,.09)", stroke: "none"
        }));
      }
      svg.appendChild(svgElement("path", {
        d: pathData, fill: "none", stroke: item.color, "stroke-width": 3,
        "stroke-linecap": "round", "stroke-linejoin": "round"
      }));
      points.forEach((point, index) => {
        svg.appendChild(svgElement("circle", {
          cx: x(index), cy: y(point[item.key]), r: 3.5, fill: item.color, stroke: "#061c13", "stroke-width": 2
        }));
      });
    });

    const labelEvery = Math.max(1, Math.ceil(points.length / 6));
    points.forEach((point, index) => {
      if (index % labelEvery !== 0 && index !== points.length - 1) return;
      addSvgText(svg, x(index), height - 17, formatTrendPeriod(point.period, trend.granularity), "middle");
    });
  }

  function formatTrendPeriod(value, granularity) {
    if (granularity === "hour") {
      const [day, hour] = value.split("T");
      const hourNumber = Number(hour.slice(0, 2));
      const suffix = hourNumber >= 12 ? "PM" : "AM";
      const displayHour = hourNumber % 12 || 12;
      return `${shortDateFormat.format(localDate(day))} ${displayHour}${suffix}`;
    }
    if (granularity === "day") return shortDateFormat.format(localDate(value));
    return value;
  }

  function appendTableCell(row, primary, secondary) {
    const cell = document.createElement("td");
    if (secondary) {
      cell.appendChild(textElement("strong", primary));
      cell.appendChild(textElement("small", secondary));
    } else {
      cell.textContent = primary;
    }
    row.appendChild(cell);
  }

  function renderPages(pages) {
    const body = byId("pages-table");
    clearNode(body);
    byId("pages-empty").hidden = pages.length > 0;
    pages.slice(0, 10).forEach((page) => {
      const row = document.createElement("tr");
      const pageCell = document.createElement("td");
      const pageDetails = document.createElement("div");
      pageDetails.className = "page-cell";
      pageDetails.appendChild(textElement("strong", page.title));
      pageDetails.appendChild(textElement("small", page.path));
      const meter = document.createElement("progress");
      meter.className = "page-meter";
      meter.max = 100;
      meter.value = page.traffic_percent;
      meter.setAttribute("aria-label", `${page.title}: ${page.traffic_percent}% of page activity`);
      pageDetails.appendChild(meter);
      pageCell.appendChild(pageDetails);
      row.appendChild(pageCell);
      appendTableCell(row, formatInteger(page.views));
      appendTableCell(row, `${decimalFormat.format(page.traffic_percent)}%`);
      body.appendChild(row);
    });
  }

  function renderPathways(pathways) {
    const container = byId("pathway-grid");
    clearNode(container);
    pathways.forEach((pathway) => {
      const card = document.createElement("article");
      card.className = "pathway-card";
      card.dataset.section = pathway.section;
      const details = document.createElement("div");
      details.appendChild(textElement("h3", pathway.title));
      const progress = document.createElement("progress");
      progress.max = 100;
      progress.value = pathway.percent;
      progress.setAttribute("aria-label", `${pathway.title}: ${pathway.percent}% of 3E page views`);
      details.appendChild(progress);
      const value = textElement("div", `${decimalFormat.format(pathway.percent)}%`, "pathway-value");
      value.appendChild(textElement("span", `${formatInteger(pathway.views)} views`));
      card.append(details, value);
      container.appendChild(card);
    });
  }

  function renderFeatures(features) {
    const body = byId("features-table");
    clearNode(body);
    byId("features-empty").hidden = features.length > 0;
    features.forEach((feature) => {
      const row = document.createElement("tr");
      appendTableCell(row, feature.title);
      appendTableCell(row, feature.section ? titleCase(feature.section) : "Sitewide");
      appendTableCell(row, formatInteger(feature.uses));
      appendTableCell(row, formatInteger(feature.estimated_visitors));
      body.appendChild(row);
    });
  }

  function titleCase(value) {
    return String(value).replace(/[_-]+/g, " ").replace(/\b\w/g, (character) => character.toUpperCase());
  }

  function renderBreakdown(items) {
    const container = byId("breakdown-list");
    clearNode(container);
    const values = items || [];
    byId("breakdown-empty").hidden = values.length > 0;
    values.slice(0, 9).forEach((item) => {
      const row = document.createElement("div");
      row.className = "breakdown-row";
      row.appendChild(textElement("strong", item.label || "Unknown"));
      const progress = document.createElement("progress");
      progress.max = 100;
      progress.value = item.percent;
      progress.setAttribute("aria-label", `${item.label}: ${item.percent}%`);
      row.appendChild(progress);
      row.appendChild(textElement("span", `${decimalFormat.format(item.percent)}% / ${formatInteger(item.views)}`));
      container.appendChild(row);
    });
  }

  function renderHours(hourly) {
    const svg = byId("hour-chart");
    const empty = byId("hours-empty");
    clearNode(svg);
    empty.hidden = hourly.length > 0;
    svg.hidden = hourly.length === 0;
    if (!hourly.length) return;

    const values = Array.from({ length: 24 }, (_, hour) => {
      const match = hourly.find((item) => item.hour === hour);
      return match ? match.views : 0;
    });
    const width = 900;
    const height = 250;
    const margin = { left: 40, right: 18, top: 15, bottom: 35 };
    const plotWidth = width - margin.left - margin.right;
    const plotHeight = height - margin.top - margin.bottom;
    const gap = 5;
    const barWidth = (plotWidth - gap * 23) / 24;
    const maxValue = Math.max(1, ...values);

    values.forEach((value, hour) => {
      const barHeight = (value / maxValue) * plotHeight;
      const x = margin.left + hour * (barWidth + gap);
      const y = margin.top + plotHeight - barHeight;
      const bar = svgElement("rect", {
        x, y, width: barWidth, height: Math.max(barHeight, value ? 2 : 0),
        rx: 2, fill: hour >= 8 && hour <= 16 ? "#f0c742" : "#4fd1b2"
      });
      const title = svgElement("title");
      title.textContent = `${hourLabel(hour)}: ${formatInteger(value)} views`;
      bar.appendChild(title);
      svg.appendChild(bar);
      if (hour % 3 === 0) addSvgText(svg, x + barWidth / 2, height - 12, hourLabel(hour), "middle");
    });
  }

  function hourLabel(hour) {
    const suffix = hour >= 12 ? "p" : "a";
    return `${hour % 12 || 12}${suffix}`;
  }

  function renderWeekdays(weekdays) {
    const container = byId("weekday-list");
    clearNode(container);
    byId("weekday-empty").hidden = weekdays.length > 0;
    const maxViews = Math.max(1, ...weekdays.map((item) => item.views));
    weekdays.forEach((item) => {
      const row = document.createElement("div");
      row.className = "breakdown-row";
      row.appendChild(textElement("strong", item.label));
      const progress = document.createElement("progress");
      progress.max = maxViews;
      progress.value = item.views;
      progress.setAttribute("aria-label", `${item.label}: ${item.views} views`);
      row.appendChild(progress);
      row.appendChild(textElement("span", `${formatInteger(item.views)} / avg ${decimalFormat.format(item.average_views)}`));
      container.appendChild(row);
    });
  }

  function renderHeatmap(items) {
    const container = byId("activity-heatmap");
    clearNode(container);
    const lookup = new Map(items.map((item) => [`${item.weekday}-${item.hour}`, item.views]));
    const maxValue = Math.max(1, ...items.map((item) => item.views));
    const dayNames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    container.appendChild(textElement("span", "", "heatmap-hour"));
    for (let hour = 0; hour < 24; hour += 1) {
      container.appendChild(textElement("span", hour % 3 === 0 ? hourLabel(hour) : "", "heatmap-hour"));
    }
    dayNames.forEach((day, weekday) => {
      container.appendChild(textElement("span", day, "heatmap-label"));
      for (let hour = 0; hour < 24; hour += 1) {
        const views = lookup.get(`${weekday}-${hour}`) || 0;
        const level = views ? Math.max(1, Math.ceil((views / maxValue) * 5)) : 0;
        const cell = document.createElement("span");
        cell.className = `heatmap-cell${level ? ` heat-${level}` : ""}`;
        cell.title = `${day}, ${hourLabel(hour)}: ${formatInteger(views)} views`;
        cell.setAttribute("aria-label", cell.title);
        container.appendChild(cell);
      }
    });
  }

  function renderTechnical(health, diagnostics) {
    const chips = byId("status-chips");
    clearNode(chips);
    health.statuses.forEach((status) => {
      const chip = textElement("span", `${status.label}  ${formatInteger(status.requests)}`, "status-chip");
      if (String(status.label).startsWith("4") || String(status.label).startsWith("5")) chip.classList.add("is-error");
      chips.appendChild(chip);
    });
    byId("human-requests").textContent = formatInteger(health.traffic.human_requests);
    byId("bot-requests").textContent = formatInteger(health.traffic.bot_requests);

    const errors = byId("errors-table");
    clearNode(errors);
    byId("errors-empty").hidden = health.top_errors.length > 0;
    health.top_errors.forEach((error) => {
      const row = document.createElement("tr");
      appendTableCell(row, String(error.status));
      appendTableCell(row, error.path);
      appendTableCell(row, formatInteger(error.requests));
      errors.appendChild(row);
    });

    const serverErrors = health.top_errors.filter((error) => error.status >= 500).reduce((sum, error) => sum + error.requests, 0);
    const badge = byId("health-badge");
    badge.classList.toggle("has-errors", serverErrors > 0);
    badge.textContent = serverErrors > 0 ? `${formatInteger(serverErrors)} server errors` : "No server errors";

    byId("newest-record").textContent = formatTimestamp(diagnostics.newest_timestamp);
    byId("oldest-record").textContent = formatTimestamp(diagnostics.oldest_timestamp);
    byId("stored-requests").textContent = formatInteger(diagnostics.request_rows);
    byId("database-size").textContent = formatBytes(diagnostics.database_bytes);
    byId("last-import").textContent = diagnostics.last_import
      ? `${titleCase(diagnostics.last_import.status)} / ${formatTimestamp(diagnostics.last_import.finished_at || diagnostics.last_import.started_at)}`
      : "Not available";
  }

  function rangeForPreset(preset) {
    const today = new Date();
    let start = new Date(today);
    let end = new Date(today);
    if (preset === "yesterday") {
      start = addDays(today, -1);
      end = addDays(today, -1);
    } else if (preset === "7-days") {
      start = addDays(today, -6);
    } else if (preset === "30-days") {
      start = addDays(today, -29);
    } else if (preset === "month") {
      start = new Date(today.getFullYear(), today.getMonth(), 1);
    } else if (preset === "year") {
      start = new Date(today.getFullYear(), 0, 1);
    } else if (preset === "all" && state.report) {
      const oldest = state.report.diagnostics.oldest_timestamp;
      const newest = state.report.diagnostics.newest_timestamp;
      if (oldest) start = localDate(String(oldest).slice(0, 10));
      if (newest) end = localDate(String(newest).slice(0, 10));
    }
    return { start: inputDate(start), end: inputDate(end) };
  }

  function selectPreset(preset) {
    state.activePreset = preset;
    document.querySelectorAll("[data-range]").forEach((button) => {
      button.classList.toggle("is-active", button.dataset.range === preset);
    });
    loadReport(rangeForPreset(preset));
  }

  function bindEvents() {
    document.querySelectorAll("[data-range]").forEach((button) => {
      button.addEventListener("click", () => selectPreset(button.dataset.range));
    });

    byId("custom-range-form").addEventListener("submit", (event) => {
      event.preventDefault();
      state.activePreset = "custom";
      document.querySelectorAll("[data-range]").forEach((button) => button.classList.remove("is-active"));
      loadReport({ start: byId("range-start").value, end: byId("range-end").value });
    });

    document.querySelectorAll("[data-breakdown]").forEach((button) => {
      button.addEventListener("click", () => {
        state.activeBreakdown = button.dataset.breakdown;
        document.querySelectorAll("[data-breakdown]").forEach((tab) => {
          tab.setAttribute("aria-selected", String(tab === button));
        });
        if (state.report) renderBreakdown(state.report[state.activeBreakdown]);
      });
    });

    byId("refresh-report").addEventListener("click", () => {
      loadReport({ start: byId("range-start").value, end: byId("range-end").value });
    });
    byId("retry-report").addEventListener("click", () => {
      loadReport({ start: byId("range-start").value, end: byId("range-end").value });
    });
    byId("download-export").addEventListener("click", () => {
      const address = new URL(`${API_ROOT}/export`, window.location.origin);
      address.searchParams.set("dataset", byId("export-dataset").value);
      address.searchParams.set("start", byId("range-start").value);
      address.searchParams.set("end", byId("range-end").value);
      const link = document.createElement("a");
      link.href = address.toString();
      document.body.appendChild(link);
      link.click();
      link.remove();
    });
  }

  function initialize() {
    bindEvents();
    const parameters = new URLSearchParams(window.location.search);
    const start = parameters.get("start");
    const end = parameters.get("end");
    if (start && end) {
      state.activePreset = "custom";
      loadReport({ start, end });
    } else {
      document.querySelector('[data-range="7-days"]').classList.add("is-active");
      loadReport({});
    }
  }

  initialize();
}());
