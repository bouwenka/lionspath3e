(function () {
  'use strict';

  const STORAGE_KEY = 'lionspath.theme';
  const DARK = 'dark';
  const LIGHT = 'light';

  function readTheme() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved === LIGHT ? LIGHT : DARK;
    } catch (error) {
      return DARK;
    }
  }

  function saveTheme(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (error) {
      // The selected theme still applies for this visit when storage is unavailable.
    }
  }

  function updateToggle(theme) {
    const toggle = document.getElementById('themeToggle');
    if (!toggle) return;
    const nextTheme = theme === DARK ? LIGHT : DARK;
    const nextLabel = nextTheme === LIGHT ? 'Switch to light mode' : 'Switch to dark mode';
    const icon = toggle.querySelector('[data-theme-icon]');
    toggle.setAttribute('aria-label', nextLabel);
    toggle.setAttribute('title', nextLabel);
    toggle.setAttribute('aria-pressed', String(theme === LIGHT));
    if (icon) icon.textContent = nextTheme === LIGHT ? '\u2600' : '\u263E';
  }

  function applyTheme(theme, persist) {
    const selected = theme === LIGHT ? LIGHT : DARK;
    document.documentElement.dataset.theme = selected;
    document.documentElement.style.colorScheme = selected;
    const themeColor = document.querySelector('meta[name="theme-color"]');
    if (themeColor) themeColor.setAttribute('content', selected === LIGHT ? '#f1f5f2' : '#003320');
    updateToggle(selected);
    if (persist) saveTheme(selected);
  }

  applyTheme(readTheme(), false);

  document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('themeToggle');
    updateToggle(document.documentElement.dataset.theme || DARK);
    if (!toggle) return;
    toggle.addEventListener('click', function () {
      const current = document.documentElement.dataset.theme === LIGHT ? LIGHT : DARK;
      applyTheme(current === DARK ? LIGHT : DARK, true);
    });
  });
})();
