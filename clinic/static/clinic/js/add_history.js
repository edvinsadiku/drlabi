(() => {
  if (!document.getElementById("historyForm")) return;

  const sprite = document.querySelector(".dental-picker").dataset.spriteUrl;
  const rows = {
    upperLeft: [18, 17, 16, 15, 14, 13, 12, 11],
    upperRight: [21, 22, 23, 24, 25, 26, 27, 28],
    lowerLeft: [48, 47, 46, 45, 44, 43, 42, 41],
    lowerRight: [31, 32, 33, 34, 35, 36, 37, 38],
  };
  const selected = new Set();
  const dhembiInput = document.getElementById("dhembiInput");
  const dhembiDisplay = document.getElementById("dhembiDisplay");
  const badge = document.getElementById("teethBadge");
  const chips = document.getElementById("selectedTeeth");
  const buttons = new Map();
  const toothKind = (code) => {
    const n = code % 10;
    return n >= 6
      ? "molar"
      : n >= 4
        ? "premolar"
        : n === 3
          ? "canine"
          : "incisor";
  };
  function toggle(code) {
    selected.has(code) ? selected.delete(code) : selected.add(code);
    sync();
  }
  function makeTooth(code) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "tooth-wrapper";
    button.dataset.code = String(code);
    button.setAttribute("aria-label", `Dhëmbi ${code}`);
    button.setAttribute("aria-pressed", "false");
    const figure = document.createElement("span");
    figure.className = "tooth-figure";
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 64 100");
    svg.setAttribute("aria-hidden", "true");
    svg.classList.add("dental-tooth");
    const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
    use.setAttribute("href", `${sprite}#${toothKind(code)}`);
    svg.append(use);
    figure.append(svg);
    const check = document.createElement("span");
    check.className = "tooth-check";
    check.textContent = "✓";
    check.setAttribute("aria-hidden", "true");
    figure.append(check);
    const label = document.createElement("span");
    label.className = "tooth-label";
    label.textContent = code;
    button.append(figure, label);
    button.addEventListener("click", () => toggle(code));
    buttons.set(code, button);
    return button;
  }
  function sync() {
    const values = [...selected].sort((a, b) => a - b);
    dhembiInput.value = dhembiDisplay.value = values.join(",");
    badge.textContent = values.length
      ? `${values.length} ${values.length === 1 ? "dhëmb i zgjedhur" : "dhëmbë të zgjedhur"}`
      : "Asnjë dhëmb i zgjedhur";
    buttons.forEach((button, code) => {
      button.classList.toggle("active", selected.has(code));
      button.setAttribute("aria-pressed", String(selected.has(code)));
    });
    chips.replaceChildren();
    values.forEach((code) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.textContent = `${code} ×`;
      chip.setAttribute("aria-label", `Hiq dhëmbin ${code}`);
      chip.addEventListener("click", () => {
        toggle(code);
        buttons.get(code)?.focus();
      });
      chips.append(chip);
    });
    document.getElementById("btnClear").disabled = !values.length;
  }
  Object.entries(rows).forEach(([id, codes]) => {
    const row = document.getElementById(id);
    codes.forEach((code) => row.append(makeTooth(code)));
  });
  (dhembiInput.value.match(/\d+/g) || [])
    .map(Number)
    .forEach((code) => selected.add(code));
  document.getElementById("btnClear").addEventListener("click", () => {
    selected.clear();
    sync();
  });
  document.getElementById("btnInvert").addEventListener("click", () => {
    buttons.forEach((_, code) =>
      selected.has(code) ? selected.delete(code) : selected.add(code),
    );
    sync();
  });
  sync();

  const fldAgreement = document.getElementById("fldAgreement"),
    fldIncluded = document.getElementById("fldIncluded"),
    priceRow = document.getElementById("priceRow"),
    vlera = document.getElementById("fldVlera");
  function togglePriceFields() {
    const included = fldIncluded.checked;
    priceRow.querySelectorAll("input").forEach((inp) => {
      if (included) inp.value = "";
      inp.disabled = included;
    });
    priceRow.classList.toggle("opacity-55", included);
    priceRow.classList.toggle("pointer-events-none", included);
  }
  fldAgreement.addEventListener("change", () => {
    fldIncluded.checked = !!fldAgreement.value;
    togglePriceFields();
  });
  fldIncluded.addEventListener("change", togglePriceFields);
  togglePriceFields();

  document.getElementById("historyForm").addEventListener("submit", (e) => {
    const vleraVal = parseFloat(vlera.value) || 0;
    const paguarVal =
      parseFloat(document.getElementById("fldPaguar").value) || 0;

    if (vleraVal === 0 && paguarVal > 0) {
      e.preventDefault();
      alert("❌ Nuk mund të regjistrohet pagesë nëse vlera është 0.");
      return;
    }

    if (vleraVal === 0 && paguarVal === 0) return;
    if (fldIncluded.checked || fldAgreement.value) return;

    // ❌ Në raste tjera kërko vlerë ose marrëveshje
    if (!fldAgreement.value && vleraVal <= 0 && paguarVal <= 0) {
      e.preventDefault();
      alert(
        "Ju lutem shënoni vlerën e shërbimit ose zgjidhni një marrëveshje.",
      );
    }
  });

  const radioPo = document.getElementById("radioPo"),
    radioJo = document.getElementById("radioJo"),
    punimFields = document.getElementById("punimFields");
  function togglePunimFields() {
    if (radioPo.checked) {
      punimFields.classList.remove("hidden");
    } else {
      punimFields
        .querySelectorAll("input,textarea")
        .forEach((el) => (el.value = ""));
      punimFields.classList.add("hidden");
    }
  }
  radioPo.addEventListener("change", togglePunimFields);
  radioJo.addEventListener("change", togglePunimFields);
  document.addEventListener("DOMContentLoaded", () => {
    const hasData =
      document
        .querySelector("textarea[name='punim_protetikor']")
        .value.trim() ||
      document.querySelector("input[name='tekniku']").value.trim();
    if (hasData) {
      radioPo.checked = true;
      togglePunimFields();
    }
  });
})();
