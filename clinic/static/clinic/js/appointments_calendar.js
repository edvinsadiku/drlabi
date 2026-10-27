document.addEventListener("DOMContentLoaded", function () {
  if (!document.getElementById("calendar") || typeof FullCalendar === "undefined") return;
  const modal = document.getElementById("appointmentModal");
  const form = document.getElementById("appointmentForm");
  const btnCancel = document.getElementById("btnCancel");
  const btnDelete = document.getElementById("btnDelete");
  const modalTitle = document.getElementById("modalTitle");
  const btnNew = document.getElementById("addNew");

  let opener, saving = false, searchTimer, searchController;
  const csrf = () => form.querySelector('[name=csrfmiddlewaretoken]').value;
  function hideSuggestions() {
    document.getElementById('patientSuggestions').classList.add('hidden');
    document.getElementById('apptPatientInput').setAttribute('aria-expanded', 'false');
  }
  function openModal(data = {}) {
    opener = document.activeElement;
    searchController?.abort();
    clearTimeout(searchTimer);
    hideSuggestions();
    document.getElementById("appointmentError").hidden = true;
    document.body.classList.add("modal-open");
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    modalTitle.textContent = data.id ? "Ndrysho terminin" : "Termin i ri";
    btnDelete.classList.toggle("hidden", !data.id);
    document.getElementById("apptId").value = data.id || "";
    document.getElementById("apptPatient").value = data.patient || "";
    document.getElementById("apptPatientInput").value = data.patient_name || "";
    document.getElementById("apptDoctor").value = data.doctor || "Dr. Labi";
    document.getElementById("apptTitle").value = data.title || "";
    document.getElementById("apptStart").value = data.start || "";
    document.getElementById("apptEnd").value = data.end || "";
    document.getElementById("apptStatus").value = data.status || "scheduled";
    document.getElementById("apptNotes").value = data.notes || "";
    document.getElementById("apptPatientInput").focus();
  }

  function closeModal() {
    if (saving) return;
    searchController?.abort();
    clearTimeout(searchTimer);
    hideSuggestions();
    document.body.classList.remove("modal-open");
    modal.classList.add("hidden");
    modal.classList.remove("flex");
    if (opener?.isConnected) opener.focus();
  }

  const calendar = new FullCalendar.Calendar(document.getElementById("calendar"), {
    initialView: window.innerWidth < 768 ? "listWeek" : "timeGridDay",
    locale: "sq",
    buttonText: {today: "Sot", day: "Dita", list: "Java"},
    noEventsText: "Nuk ka termine për këtë periudhë.",
    firstDay: 1,
    hiddenDays: [0],
    slotMinTime: "09:00:00",
    slotMaxTime: "20:00:00",
    allDaySlot: false,
    height: "auto",
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "timeGridDay,listWeek"
    },
    dayHeaderFormat: { weekday: 'long' },
    slotLabelFormat: { hour: '2-digit', minute: '2-digit', hour12: false },
    slotLabelContent: (arg) => "Ora: " + arg.text,
    selectable: true,
    editable: false, // Changes are saved through the validated appointment form.
    events: "/appointments/events/",
    eventContent: (info) => {
      let title = info.event.title || "";
      let doctor = info.event.extendedProps.doctor ? " (" + info.event.extendedProps.doctor + ")" : "";
      const label = document.createElement("span"); label.textContent = title + doctor; return { domNodes: [label] };
    },
    eventClassNames: (info) => info.event.extendedProps.status,
    eventClick: (info) => openModal({
      id: info.event.id,
      patient: info.event.extendedProps.patient,
      patient_name: info.event.extendedProps.patient_name,
      doctor: info.event.extendedProps.doctor,
      title: info.event.extendedProps.service_title || info.event.title,
      start: info.event.startStr.slice(0,16),
      end: info.event.endStr ? info.event.endStr.slice(0,16) : "",
      status: info.event.extendedProps.status,
      notes: info.event.extendedProps.notes
    }),
    select: (info) => openModal({
      start: info.startStr.slice(0,16),
      end: info.endStr ? info.endStr.slice(0,16) : ""
    })
  });
  calendar.render();
  const patientContext = document.getElementById('appointment-patient-context');
  const selectedPatient = patientContext ? JSON.parse(patientContext.textContent) : null;
  if (selectedPatient) openModal({ patient: selectedPatient.id, patient_name: selectedPatient.name });
  else if (new URLSearchParams(location.search).get("new") === "1") openModal();

  // Autocomplete për pacientët
  const patientInput = document.getElementById("apptPatientInput");
  const patientHidden = document.getElementById("apptPatient");
  const suggestions = document.getElementById("patientSuggestions");

  patientInput.addEventListener("input", function() {
    patientHidden.value = "";
    searchController?.abort();
    clearTimeout(searchTimer);
    hideSuggestions();
    const q = this.value.trim();
    if (!q) return;
    searchTimer = setTimeout(async () => {
      const controller = searchController = new AbortController();
      try {
        const res = await fetch(`/patients/search/?q=${encodeURIComponent(q)}`, {signal: controller.signal});
        if (!res.ok) throw new Error();
        const data = await res.json();
        if (controller.signal.aborted) return;
        suggestions.replaceChildren();
        data.forEach(p => {
          const li = document.createElement("li");
          li.textContent = `${p.emri_mbiemri} (${p.telefoni || "pa numër"})`;
          li.className = "px-3 py-2 hover:bg-emerald-50 cursor-pointer";
          li.tabIndex = 0;
          li.setAttribute('role', 'option');
          li.setAttribute('aria-selected', 'false');
          li.onclick = () => {
            patientInput.value = p.emri_mbiemri;
            patientHidden.value = p.id;
            hideSuggestions();
            patientInput.focus();
          };
          li.addEventListener('keydown', event => {
            if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); li.click(); }
            if (event.key === 'ArrowDown') { event.preventDefault(); (li.nextElementSibling || li).focus(); }
            if (event.key === 'ArrowUp') { event.preventDefault(); (li.previousElementSibling || patientInput).focus(); }
          });
          suggestions.append(li);
        });
        suggestions.classList.toggle("hidden", data.length === 0);
        patientInput.setAttribute('aria-expanded', String(data.length > 0));
      } catch (error) {
        if (error.name !== 'AbortError') {
          const feedback = document.getElementById('appointmentError');
          feedback.textContent = 'Kërkimi i pacientit dështoi. Provo përsëri.';
          feedback.hidden = false;
        }
      }
    }, 250);
  });
  patientInput.addEventListener('keydown', event => {
    if (event.key === 'ArrowDown' && !suggestions.classList.contains('hidden')) {
      event.preventDefault(); suggestions.firstElementChild?.focus();
    }
  });
  document.addEventListener('keydown', event => {
    if (modal.classList.contains('hidden')) return;
    if (event.key === 'Escape') {
      event.preventDefault();
      if (!suggestions.classList.contains('hidden')) { hideSuggestions(); patientInput.focus(); }
      else closeModal();
    }
    if (event.key !== 'Tab') return;
    const focusable = [...modal.querySelectorAll('button,input,select,textarea,[tabindex="0"]')]
      .filter(e => !e.disabled && e.type !== 'hidden' && e.getClientRects().length);
    const first = focusable[0], last = focusable[focusable.length - 1];
    if (!modal.contains(document.activeElement)) { event.preventDefault(); first?.focus(); }
    else if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });
  document.addEventListener("click", e => {
    if (!patientInput.contains(e.target) && !suggestions.contains(e.target)) hideSuggestions();
  });

  btnNew.addEventListener("click", () => openModal());

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (saving) return;
    const id = document.getElementById("apptId").value;
    const payload = {
      patient: patientHidden.value,
      doctor: document.getElementById("apptDoctor").value,
      title: document.getElementById("apptTitle").value,
      start: document.getElementById("apptStart").value,
      end: document.getElementById("apptEnd").value || null,
      status: document.getElementById("apptStatus").value,
      notes: document.getElementById("apptNotes").value
    };
    const error = document.getElementById('appointmentError');
    const submit = form.querySelector('button[type="submit"]');
    error.hidden = true;
    if (!payload.patient) { error.textContent='Zgjidh pacientin nga lista e rezultateve.'; error.hidden=false; return; }
    if (payload.end && payload.end <= payload.start) { error.textContent='Mbarimi duhet të jetë pas fillimit të vizitës.'; error.hidden=false; return; }
    saving = true;
    submit.disabled = true;
    try {
      const response = await fetch(id ? `/appointments/update/${id}/` : "/appointments/create/", {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() }, body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error('save');
      if (selectedPatient && !id) { window.location.assign(`/patients/${selectedPatient.id}/`); return; }
      saving = false; closeModal(); calendar.refetchEvents();
    } catch (_) { error.textContent='Termini nuk u ruajt. Kontrollo të dhënat dhe provo përsëri.'; error.hidden=false; }
    finally { saving=false; submit.disabled=false; }
  });

  btnDelete.addEventListener("click", async () => {
    const id = document.getElementById("apptId").value;
    if (!id || saving || !confirm("A je i sigurt që dëshiron ta fshish këtë termin?")) return;
    saving = true;
    btnDelete.disabled = true;
    try {
      const response = await fetch(`/appointments/delete/${id}/`, {
        method: "POST", headers: {"X-CSRFToken": csrf()}
      });
      if (!response.ok) throw new Error();
      saving = false; closeModal(); calendar.refetchEvents();
    } catch (_) {
      const feedback = document.getElementById('appointmentError');
      feedback.textContent = 'Termini nuk u fshi. Provo përsëri.';
      feedback.hidden = false;
    } finally { saving = false; btnDelete.disabled = false; }
  });

  btnCancel.addEventListener("click", closeModal);
});
