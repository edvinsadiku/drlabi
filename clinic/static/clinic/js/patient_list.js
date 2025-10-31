document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("patientModal");
  const card = document.getElementById("patientCard");
  const form = document.getElementById("patientForm");
  const btnSave = document.getElementById("btnSubmitPatient");
  const title = document.getElementById("patientModalTitle");

  const btnAdd = document.getElementById("btnAddPatient");

  // Shto pacient
  if (btnAdd) {
    btnAdd.addEventListener("click", e => {
      e.preventDefault();
      form.reset();
      form.dataset.url = btnAdd.dataset.url;
      title.textContent = "Shto pacient";
      openPatientModal();
    });
  }

  // Ndrysho pacient
  document.querySelectorAll('a[href*="/edit/"]').forEach(btn => {
    btn.addEventListener("click", async e => {
      e.preventDefault();
      const editUrl = btn.getAttribute("href");
      form.dataset.url = editUrl;
      title.textContent = "Ndrysho pacient";
      try {
        const res = await fetch(editUrl);
        const data = await res.json();
        if (data.success && data.patient) {
          const p = data.patient;
          form.querySelector("[name='emri_mbiemri']").value = p.emri_mbiemri || "";
          form.querySelector("[name='data_e_lindjes']").value = formatDate(p.data_e_lindjes);
          form.querySelector("[name='telefoni']").value = p.telefoni || "";
          form.querySelector("[name='emaili']").value = p.emaili || "";
          form.querySelector("[name='leternjoftimi']").value = p.leternjoftimi || "";
          form.querySelector("[name='adresa']").value = p.adresa || "";
        }
        openPatientModal();
      } catch (err) {
        console.error("Gabim gjatë marrjes së të dhënave:", err);
      }
    });
  });

  // Ruaj pacientin
  btnSave?.addEventListener("click", async () => {
    const formData = new FormData(form);
    const url = form.dataset.url;
    try {
      const res = await fetch(url, {
        method: "POST",
        body: formData,
        headers: { "X-Requested-With": "XMLHttpRequest" }
      });
      const data = await res.json();

      if (data.success) {
        showToast(data.message, "success");
        closePatientModal();
        setTimeout(() => {
          if (data.redirect_url) window.location.href = data.redirect_url;
          else location.reload();
        }, 800);
      } else {
        showToast(data.message || "Gabim gjatë ruajtjes", "error");
      }
    } catch {
      showToast("Gabim në lidhje me serverin", "error");
    }
  });

  // Ndihmës
  function openPatientModal() {
    modal.classList.remove("hidden"); modal.classList.add("flex");
    setTimeout(() => {
      card.classList.remove("opacity-0", "scale-95");
      card.classList.add("opacity-100", "scale-100");
    }, 20);
  }

  function closePatientModal() {
    card.classList.add("opacity-0", "scale-95");
    card.classList.remove("opacity-100", "scale-100");
    setTimeout(() => {
      modal.classList.add("hidden");
      modal.classList.remove("flex");
    }, 150);
  }
  window.closePatientModal = closePatientModal;

  function showToast(msg, type = "success") {
    const toast = document.createElement("div");
    toast.className = `px-4 py-3 rounded-xl text-white shadow-lg text-sm transition-all ${
      type === "success" ? "bg-emerald-600" : "bg-red-600"
    }`;
    toast.textContent = msg;
    document.getElementById("toastStack").appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
  }

  function formatDate(value) {
    if (!value) return "";
    if (value.includes(".")) {
      const [d, m, y] = value.split(".");
      return `${y}-${m}-${d}`;
    }
    return value;
  }
});
