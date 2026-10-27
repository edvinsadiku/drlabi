(() => {
  const workspace = document.querySelector('.clinic-workspace');
  if (!workspace) return;
  const panels = [...workspace.querySelectorAll('[data-dashboard-panel]')];
  const tabs = workspace.querySelector('.dashboard-sections');
  let activePanel = panels[0]?.id;
  let compact = false;
  const states = panels.filter(panel => panel.querySelector('[data-dashboard-list]')).map(panel => ({
    panel, list: panel.querySelector('[data-dashboard-list]'),
    rows: [...panel.querySelectorAll('[data-dashboard-row]')],
    controls: panel.querySelector('.dashboard-page-controls'),
    range: panel.querySelector('.dashboard-page-range'),
    page: 0, size: 1,
  }));
  function render(state) {
    const { rows, controls, range, panel } = state;
    const pages = Math.max(1, Math.ceil(rows.length / state.size));
    state.page = Math.min(state.page, pages - 1);
    const start = state.page * state.size;
    rows.forEach((row, index) => { row.hidden = index < start || index >= start + state.size; });
    controls.hidden = pages <= 1;
    controls.querySelector('[data-page-prev]').disabled = state.page === 0;
    controls.querySelector('[data-page-next]').disabled = state.page >= pages - 1;
    const total = Number(panel.dataset.total || rows.length);
    range.textContent = rows.length ? `${start + 1}–${Math.min(start + state.size, rows.length)} nga ${rows.length}${total > rows.length ? ` · ${total} gjithsej` : ''}` : '0 regjistrime';
  }
  states.forEach(state => {
    state.controls.querySelector('[data-page-prev]').addEventListener('click', () => { state.page--; render(state); });
    state.controls.querySelector('[data-page-next]').addEventListener('click', () => { state.page++; render(state); });
  });
  panels.forEach(panel => {
    const button = document.createElement('button');
    button.type = 'button'; button.className = 'btn';
    button.id = `${panel.id}-tab`;
    button.textContent = panel.dataset.dashboardPanel;
    button.setAttribute('role', 'tab');
    button.setAttribute('aria-controls', panel.id);
    button.addEventListener('click', () => { activePanel = panel.id; updatePanels(); scheduleLayout(); });
    tabs.append(button);
  });
  tabs.setAttribute('role', 'tablist');
  tabs.addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    const buttons = [...tabs.querySelectorAll('button')];
    let index = buttons.indexOf(document.activeElement);
    if (index < 0) return;
    event.preventDefault();
    index = event.key === 'Home' ? 0 : event.key === 'End' ? buttons.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : -1) + buttons.length) % buttons.length;
    buttons[index].click(); buttons[index].focus();
  });
  function updatePanels() {
    workspace.classList.toggle('is-compact', compact);
    tabs.hidden = !compact;
    panels.forEach(panel => {
      panel.hidden = compact && panel.id !== activePanel;
      if (compact) { panel.setAttribute('role', 'tabpanel'); panel.setAttribute('aria-labelledby', `${panel.id}-tab`); }
      else { panel.removeAttribute('role'); panel.removeAttribute('aria-labelledby'); }
      const button = document.getElementById(`${panel.id}-tab`);
      button.setAttribute('aria-selected', String(panel.id === activePanel));
      button.tabIndex = panel.id === activePanel ? 0 : -1;
      button.classList.toggle('btn-primary', panel.id === activePanel);
    });
  }
  function layout() {
    // Small screens switch sections; desktop shows every panel at once.
    compact = window.innerWidth <= 900 || window.innerHeight < 650;
    updatePanels();
    states.filter(state => !state.panel.hidden).forEach(state => {
      if (!state.rows.length) return;
      const firstIndex = state.page * state.size;
      state.rows.forEach(row => { row.hidden = false; });
      const rowHeight = Math.max(...state.rows.map(row => row.getBoundingClientRect().height));
      state.size = Math.max(1, Math.floor((state.list.clientHeight + .5) / rowHeight));
      state.page = Math.floor(firstIndex / state.size);
      render(state);
    });
  }
  let scheduled = false;
  function scheduleLayout() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => { scheduled = false; layout(); });
  }
  workspace.classList.add('dashboard-ready');
  const observer = new ResizeObserver(scheduleLayout);
  observer.observe(workspace);
  states.forEach(state => observer.observe(state.list));
  window.addEventListener('resize', scheduleLayout);
  document.fonts.ready.then(scheduleLayout);
  layout();
})();
