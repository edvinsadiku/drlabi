function toggleSidebar(force) {
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("overlay");
  const toggle = document.getElementById("menu-toggle");
  if (!sidebar) return;
  const open =
    typeof force === "boolean" ? force : !sidebar.classList.contains("is-open");
  sidebar.classList.toggle("is-open", open);
  sidebar.inert = !open && !window.matchMedia("(min-width: 901px)").matches;
  overlay.hidden = !open;
  toggle.setAttribute("aria-expanded", String(open));
  document.body.style.overflow = open ? "hidden" : "";
  if (open) sidebar.querySelector("a").focus();
  else if (window.matchMedia("(min-width: 901px)").matches) document.getElementById("sidebar-collapse")?.focus();
  else toggle.focus();
}
document
  .getElementById("menu-toggle")
  ?.addEventListener("click", () => toggleSidebar());
document
  .getElementById("overlay")
  ?.addEventListener("click", () => toggleSidebar(false));
document.addEventListener("keydown", (event) => {
  if (
    event.key === "Escape" &&
    document.getElementById("sidebar")?.classList.contains("is-open")
  )
    toggleSidebar(false);
});
window.matchMedia("(min-width: 901px)").addEventListener("change", (event) => {
  const sidebar = document.getElementById("sidebar");
  if (sidebar) sidebar.inert = !event.matches && !sidebar.classList.contains("is-open");
  if (
    event.matches &&
    document.getElementById("sidebar")?.classList.contains("is-open")
  )
    toggleSidebar(false);
});

if (document.getElementById("sidebar")) document.getElementById("sidebar").inert = !window.matchMedia("(min-width: 901px)").matches;

// Desktop rail preference is restored in the head to avoid flashing the full menu.
(() => {
  const root = document.documentElement;
  const toggle = document.getElementById('sidebar-collapse');
  const sidebar = document.getElementById('sidebar');
  if (!toggle || !sidebar) return;
  const desktop = window.matchMedia('(min-width: 901px)');
  const tip = document.createElement('div');
  tip.id = 'sidebar-tooltip';
  tip.className = 'sidebar-tooltip';
  tip.setAttribute('role', 'tooltip');
  tip.hidden = true;
  document.body.append(tip);
  let tipTarget;
  const hideTip = () => {
    tip.hidden = true;
    tipTarget?.removeAttribute('aria-describedby');
    tipTarget = null;
  };
  const sync = () => {
    const collapsed = root.classList.contains('sidebar-collapsed');
    toggle.setAttribute('aria-expanded', String(!collapsed));
    toggle.setAttribute('aria-label', collapsed ? 'Zgjero menunë' : 'Minimizo menunë');
    toggle.title = toggle.getAttribute('aria-label');
    hideTip();
  };
  toggle.addEventListener('click', () => {
    root.classList.toggle('sidebar-collapsed');
    try { localStorage.setItem('clinic.sidebar.collapsed', root.classList.contains('sidebar-collapsed') ? '1' : '0'); } catch (error) { /* Storage may be unavailable in private browsers. */ }
    sync();
  });
  sidebar.querySelectorAll('.nav-link').forEach(link => {
    const label = link.querySelector('span').textContent.trim();
    link.setAttribute('aria-label', label);
    const showTip = () => {
      if (!desktop.matches || !root.classList.contains('sidebar-collapsed')) return;
      hideTip();
      tipTarget = link;
      tip.textContent = label;
      link.setAttribute('aria-describedby', tip.id);
      const rect = link.getBoundingClientRect();
      tip.style.left = `${sidebar.getBoundingClientRect().right + 10}px`;
      tip.style.top = `${rect.top + rect.height / 2}px`;
      tip.hidden = false;
    };
    link.addEventListener('mouseenter', showTip);
    link.addEventListener('focus', showTip);
    link.addEventListener('mouseleave', hideTip);
    link.addEventListener('blur', hideTip);
    link.addEventListener('click', hideTip);
  });
  sidebar.querySelector('nav').addEventListener('scroll', hideTip);
  document.addEventListener('keydown', event => { if (event.key === 'Escape') hideTip(); });
  window.addEventListener('resize', hideTip);
  sync();
})();
