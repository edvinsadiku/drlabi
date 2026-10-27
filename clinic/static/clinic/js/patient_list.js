/* One request pipeline for search, filters and pagination; one validated patient form. */
document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('patientModal');
  const card = document.getElementById('patientCard');
  const form = document.getElementById('patientForm');
  const save = document.getElementById('btnSubmitPatient');
  const title = document.getElementById('patientModalTitle');
  const filters = document.getElementById('searchForm');
  const input = document.getElementById('searchInput');
  const add = document.querySelector('[data-add-patient]');
  if (!modal || !form || !filters) return;
  let debounce, listController, editController, openTimer, closeTimer;
  let opener, previousOverflow = '', saving = false;
  const headers = {'X-Requested-With': 'XMLHttpRequest'};
  const notify = (message, error = false) => {
    const toast = document.createElement('div');
    toast.className = error ? 'notice notice-error' : 'notice';
    toast.setAttribute('role', error ? 'alert' : 'status');
    toast.textContent = message;
    document.getElementById('toastStack').append(toast);
    setTimeout(() => toast.remove(), 6000);
  };
  function openModal(trigger) {
    clearTimeout(closeTimer);
    opener = trigger;
    previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    modal.classList.remove('hidden');
    modal.classList.add('flex');
    openTimer = setTimeout(() => {
      card.classList.remove('opacity-0', 'scale-95');
      card.classList.add('opacity-100', 'scale-100');
      form.elements.emri_mbiemri.focus({preventScroll: true});
    }, 20);
  }
  function closeModal() {
    if (saving) return;
    clearTimeout(openTimer);
    editController?.abort();
    card.classList.add('opacity-0', 'scale-95');
    card.classList.remove('opacity-100', 'scale-100');
    closeTimer = setTimeout(() => {
      modal.classList.add('hidden');
      modal.classList.remove('flex');
      document.body.style.overflow = previousOverflow;
      if (opener?.isConnected) opener.focus({preventScroll: true});
    }, 150);
  }
  window.closePatientModal = closeModal;
  document.addEventListener('keydown', event => {
    if (modal.classList.contains('hidden')) return;
    if (event.key === 'Escape') { event.preventDefault(); closeModal(); }
    if (event.key !== 'Tab') return;
    const items = [...modal.querySelectorAll('button,input,textarea,select,a[href]')]
      .filter(e => !e.disabled && e.getClientRects().length && e.type !== 'hidden');
    const first = items[0], last = items[items.length - 1];
    if (!modal.contains(document.activeElement)) { event.preventDefault(); first?.focus(); }
    else if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  add?.addEventListener('click', event => {
    event.preventDefault();
    editController?.abort();
    form.reset();
    form.action = add.href;
    title.textContent = 'Shto pacient';
    openModal(add);
  });
  document.querySelector('.patient-directory').addEventListener('click', async event => {
    const link = event.target.closest('a[href*="/edit/"]');
    if (!link) return;
    event.preventDefault();
    editController?.abort();
    const controller = editController = new AbortController();
    link.setAttribute('aria-busy', 'true');
    try {
      const response = await fetch(link.href, {headers, signal: controller.signal});
      if (!response.ok) throw new Error();
      const data = await response.json();
      if (!data.success || !data.patient) throw new Error();
      if (controller.signal.aborted) return;
      form.reset();
      form.action = link.href;
      for (const name of ['emri_mbiemri','data_e_lindjes','telefoni','emaili','leternjoftimi','adresa','informata_shtese']) {
        form.elements[name].value = data.patient[name] || '';
      }
      title.textContent = 'Ndrysho pacient';
      openModal(link);
    } catch (error) {
      if (error.name !== 'AbortError') notify('Të dhënat nuk u ngarkuan. Provo përsëri.', true);
    } finally { link.removeAttribute('aria-busy'); }
  });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (saving || !form.reportValidity()) return;
    saving = true;
    save.disabled = true;
    form.setAttribute('aria-busy', 'true');
    let succeeded = false;
    try {
      const response = await fetch(form.action, {method: 'POST', headers, body: new FormData(form)});
      const data = await response.json();
      if (!response.ok || !data.success) {
        notify(data.message || 'Ruajtja dështoi. Kontrollo të dhënat dhe provo përsëri.', true);
        return;
      }
      succeeded = true;
      notify(data.message || 'Pacienti u ruajt.');
      saving = false;
      closeModal();
      setTimeout(() => { if (data.redirect_url) location.assign(data.redirect_url); else location.reload(); }, 600);
    } catch (error) { notify('Lidhja me serverin dështoi. Të dhënat mbeten në formular.', true); }
    finally {
      saving = succeeded;
      save.disabled = succeeded;
      form.removeAttribute('aria-busy');
    }
  });
  async function fetchPatients(url) {
    listController?.abort();
    const controller = listController = new AbortController();
    const table = document.querySelector('.patient-directory table');
    table.setAttribute('aria-busy', 'true');
    try {
      const response = await fetch(url, {headers, signal: controller.signal});
      if (!response.ok || response.redirected) throw new Error();
      const doc = new DOMParser().parseFromString(await response.text(), 'text/html');
      if (controller.signal.aborted) return;
      if (!doc.querySelector('.patient-directory table')) throw new Error();
      for (const selector of ['.patient-directory table', '#patient-count', '#patientPagination']) {
        const target = document.querySelector(selector), source = doc.querySelector(selector);
        if (source && target) target.replaceChildren(...source.childNodes);
      }
      history.replaceState(null, '', url);
    } catch (error) {
      if (error.name !== 'AbortError') notify('Lista nuk u përditësua. Provo përsëri.', true);
    } finally { if (controller === listController) table.removeAttribute('aria-busy'); }
  }
  const refresh = () => fetchPatients(`${location.pathname}?${new URLSearchParams(new FormData(filters))}`);
  input.addEventListener('input', () => {
    clearTimeout(debounce);
    listController?.abort();
    debounce = setTimeout(refresh, 300);
  });
  filters.addEventListener('change', event => {
    if (event.target === input) return;
    clearTimeout(debounce); refresh();
  });
  filters.addEventListener('submit', event => { event.preventDefault(); clearTimeout(debounce); refresh(); });
  document.getElementById('patientPagination').addEventListener('click', event => {
    const link = event.target.closest('a');
    if (!link) return;
    event.preventDefault(); clearTimeout(debounce); fetchPatients(link.href);
  });
});
