(() => {
  const form = document.getElementById("historyForm");
  if (!form) return;
  const panels = [...form.querySelectorAll("[data-visit-panel]")];
  const steps = [...document.querySelectorAll("[data-visit-step]")];
  const back = document.getElementById("visitBack"),
    next = document.getElementById("visitNext");
  let current = 0;
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
      [
        "Vlera",
        value("agreement_id") !== "—"
          ? "Përfshirë në marrëveshje"
          : (value("vlera") === "—" ? "0.00" : value("vlera")) + " €",
      ],
      [
        "Paguar në këtë vizitë",
        (value("paguar") === "—" ? "0.00" : value("paguar")) + " €",
      ],
    ];
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
    current = step;
    panels.forEach((p) => (p.hidden = Number(p.dataset.visitPanel) !== step));
    steps.forEach((b, i) => {
      if (i === step) b.setAttribute("aria-current", "step");
      else b.removeAttribute("aria-current");
    });
    back.hidden = step === 0;
    next.hidden = step === 2;
    document.getElementById("visitStepHint").textContent = [
      "Hapi 1 nga 3 · Kujdesi klinik",
      "Hapi 2 nga 3 · Vlera dhe arkëtimi",
      "Hapi 3 nga 3 · Kontrollo të dhënat",
    ][step];
    if (step === 2) review();
  }
  steps.forEach((b, i) =>
    b.addEventListener("click", () => {
      if (
        i <= current ||
        Array.from({ length: i }, (_, n) => n).every(validStep)
      )
        show(i);
    }),
  );
  next.addEventListener("click", () => {
    if (validStep(current)) {
      show(current + 1);
      steps[current].focus();
    }
  });
  back.addEventListener("click", () => {
    show(Math.max(0, current - 1));
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
  form.addEventListener("submit", (event) => {
    if (current !== 2) {
      event.preventDefault();
      if (validStep(current)) show(current + 1);
    }
  });
  form.classList.add("visit-form-ready");
  show(0);
})();
