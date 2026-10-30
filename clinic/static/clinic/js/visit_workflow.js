(() => {
  const form = document.getElementById("historyForm");
  if (!form) return;
  const panels = [...form.querySelectorAll("[data-visit-panel]")];
  const steps = [...document.querySelectorAll("[data-visit-step]")];
  const back = document.getElementById("visitBack"),
    next = document.getElementById("visitNext");
  let current = 0;
  const agreement = document.getElementById("fldAgreement");
  const editing = form.dataset.editing === "true";
  const linked = () => form.elements.registration_mode.value === "agreement";
  const sequence = () => (linked() || editing) ? [0, 2] : [0, 1, 2];
  function syncRegistration() {
    document.getElementById("treatment-agreement").hidden = !linked();
    agreement.disabled = !linked() || editing;
    agreement.required = linked() && !editing;
    steps[1].hidden = linked() || editing;
    steps[2].querySelector("span").textContent = sequence().length === 2 ? "02" : "03";
    document.querySelector(".visit-steps").classList.toggle("agreement-flow", sequence().length === 2);
    for (const input of form.querySelectorAll('[data-visit-panel="1"] input, [data-visit-panel="1"] select')) input.disabled = linked() || editing;
    show(0);
  }
  form.querySelectorAll('[name="registration_mode"]').forEach(input => input.addEventListener("change", syncRegistration));
  const value = (name) => form.elements.namedItem(name)?.value?.trim() || "—";
  function review() {
    const target = document.getElementById("visitReview");
    target.replaceChildren();
    const rows = [
      ["Doktori", value("doctor")],
      ["Dhëmbët", value("dhembi")],
      ["Diagnoza", value("diagnoza")],
      ["Trajtimi", value("trajtimi")],
      ["Punimi protetikor", value("punim_protetikor")],
    ];
    rows.unshift(["Regjistrimi", linked() ? "Pjesë e marrëveshjes" : "Trajtim i veçantë"]);
    if (linked()) rows.splice(1, 0, ["Marrëveshja", agreement.selectedOptions[0]?.textContent || "—"]);
    else if (!editing) rows.push(["Vlera", (value("vlera") === "—" ? "0.00" : value("vlera")) + " €"], ["Paguar në këtë vizitë", (value("paguar") === "—" ? "0.00" : value("paguar")) + " €"]);
    rows.forEach(([label, text]) => {
      const wrap = document.createElement("div"),
        dt = document.createElement("dt"),
        dd = document.createElement("dd");
      dt.textContent = label;
      dd.textContent = text;
      wrap.append(dt, dd);
      target.append(wrap);
    });
  }
  function validStep(step) {
    for (const panel of panels.filter(
      (p) => Number(p.dataset.visitPanel) === step,
    )) {
      for (const input of panel.querySelectorAll("input,select,textarea")) {
        if (!input.disabled && !input.checkValidity()) {
          show(step);
          input.reportValidity();
          return false;
        }
      }
    }
    return true;
  }
  function show(step) {
    if (!sequence().includes(step)) return;
    current = step;
    panels.forEach((p) => (p.hidden = Number(p.dataset.visitPanel) !== step));
    steps.forEach((b, i) => {
      if (i === step) b.setAttribute("aria-current", "step");
      else b.removeAttribute("aria-current");
    });
    back.hidden = step === 0;
    next.hidden = step === 2;
    const position = sequence().indexOf(step) + 1;
    document.getElementById("visitStepHint").textContent = `Hapi ${position} nga ${sequence().length}`;
    if (step === 2) review();
  }
  steps.forEach((b, i) =>
    b.addEventListener("click", () => {
      if (
        i <= current ||
        sequence().filter(n => n < i).every(validStep)
      )
        show(i);
    }),
  );
  next.addEventListener("click", () => {
    if (validStep(current)) {
      show(sequence()[sequence().indexOf(current) + 1]);
      steps[current].focus();
    }
  });
  back.addEventListener("click", () => {
    show(sequence()[Math.max(0, sequence().indexOf(current) - 1)]);
    steps[current].focus();
  });
  form.addEventListener(
    "invalid",
    (event) => {
      const panel = event.target.closest("[data-visit-panel]");
      if (panel) show(Number(panel.dataset.visitPanel));
    },
    true,
  );
  form.addEventListener("submit", event => {
    if (current !== 2) {
      event.preventDefault();
      if (validStep(current)) show(sequence()[sequence().indexOf(current) + 1]);
      return;
    }
    if (!sequence().every(validStep)) event.preventDefault();
  });
  form.classList.add("visit-form-ready");
  syncRegistration();
})();
