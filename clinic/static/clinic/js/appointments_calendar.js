document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("appointmentModal");
  const form = document.getElementById("appointmentForm");
  const btnCancel = document.getElementById("btnCancel");
  const btnDelete = document.getElementById("btnDelete");
  const modalTitle = document.getElementById("modalTitle");
  const btnNew = document.getElementById("addNew");

  function openModal(data = {}) {
    document.body.classList.add("modal-open");
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    modalTitle.textContent = data.id ? "✏️ Ndrysho Termin" : "➕ Termin i Ri";
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
  }

  function closeModal() {
    document.body.classList.remove("modal-open");
    modal.classList.add("hidden");
  }

  const calendar = new FullCalendar.Calendar(document.getElementById("calendar"), {
    initialView: window.innerWidth < 768 ? "listWeek" : "timeGridDay",
    locale: "sq",
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
    editable: true,
    events: "/appointments/events/",
    eventContent: (info) => {
      let title = info.event.title || "";
      let doctor = info.event.extendedProps.doctor ? " (" + info.event.extendedProps.doctor + ")" : "";
      return { html: `<b>${title}</b>${doctor}` };
    },
    eventClassNames: (info) => info.event.extendedProps.status,
    eventClick: (info) => openModal({
      id: info.event.id,
      patient: info.event.extendedProps.patient,
      patient_name: info.event.extendedProps.patient_name,
      doctor: info.event.extendedProps.doctor,
      title: info.event.title,
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

  // Autocomplete për pacientët
  const patientInput = document.getElementById("apptPatientInput");
  const patientHidden = document.getElementById("apptPatient");
  const suggestions = document.getElementById("patientSuggestions");

  patientInput.addEventListener("input", async function() {
    const q = this.value.trim();
    if (!q) { suggestions.classList.add("hidden"); return; }
    const res = await fetch(`/patients/search/?q=${encodeURIComponent(q)}`);
    const data = await res.json();
    suggestions.innerHTML = "";
    data.forEach(p => {
      const li = document.createElement("li");
      li.innerHTML = `<strong>${p.emri_mbiemri}</strong> <span class="text-gray-500 text-xs">(${p.telefoni || "pa numër"})</span>`;
      li.className = "px-3 py-2 hover:bg-emerald-50 cursor-pointer";
      li.onclick = () => {
        patientInput.value = p.emri_mbiemri;
        patientHidden.value = p.id;
        suggestions.classList.add("hidden");
      };
      suggestions.appendChild(li);
    });
    suggestions.classList.toggle("hidden", data.length === 0);
  });

  document.addEventListener("click", (e) => {
    if (!patientInput.contains(e.target) && !suggestions.contains(e.target)) suggestions.classList.add("hidden");
  });

  btnNew.addEventListener("click", () => openModal());

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const id = document.getElementById("apptId").value;
    const payload = {
      patient: patientHidden.value,
      doctor: document.getElementById("apptDoctor").value,
      title: document.getElementById("apptTitle").value,
      start: document.getElementById("apptStart").value,
      end: document.getElementById("apptEnd").value,
      status: document.getElementById("apptStatus").value,
      notes: document.getElementById("apptNotes").value
    };
    fetch(id ? `/appointments/update/${id}/` : "/appointments/create/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }).then(() => { closeModal(); calendar.refetchEvents(); });
  });

  btnDelete.addEventListener("click", () => {
    const id = document.getElementById("apptId").value;
    if (!id) return;
    if (confirm("A je i sigurt që dëshiron ta fshish këtë termin?")) {
      fetch(`/appointments/delete/${id}/`, {
        method: "POST",
        headers: { "X-CSRFToken": "{{ csrf_token }}" }
      }).then(() => { closeModal(); calendar.refetchEvents(); });
    }
  });

  btnCancel.addEventListener("click", closeModal);
});
