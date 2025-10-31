
  const svgBase = window.STATIC_IMG_BASE || "/static/assets/img/";
  const U_LEFT=[18,17,16,15,14,13,12,11],U_RIGHT=[21,22,23,24,25,26,27,28],
        L_LEFT=[48,47,46,45,44,43,42,41],L_RIGHT=[31,32,33,34,35,36,37,38];
  const selected=new Set(),dhembiInput=document.getElementById("dhembiInput"),
        dhembiDisplay=document.getElementById("dhembiDisplay"),
        badge=document.getElementById("teethBadge");
  const HAS_SVG=new Set([11,12,13,14,15,16,17,18,21,22,23,24,25,26,27,28,31,32,33,34,35,36,37,38,41,42,43,44,45,46,47,48]);
  function makeToothElement(code){const w=document.createElement("div");w.className="tooth-wrapper";
    if(HAS_SVG.has(code)){const i=document.createElement("img");i.src=svgBase+code+".svg";i.alt=code;i.className="tooth-img";i.dataset.code=code;i.addEventListener("click",()=>toggle(i,w));w.appendChild(i);}
    else{const s=document.createElement("span");s.className="tooth-fallback";s.textContent=code;s.dataset.code=code;s.addEventListener("click",()=>toggle(s,w));w.appendChild(s);}
    const l=document.createElement("span");l.className="tooth-label";l.textContent=code;w.appendChild(l);return w;}
  function mountRow(id,codes){const el=document.getElementById(id);codes.forEach(c=>el.appendChild(makeToothElement(c)));}
  function toggle(n,w){const c=n.dataset.code;if(selected.has(c)){selected.delete(c);n.classList.remove("active");w.classList.remove("active");}
    else{selected.add(c);n.classList.add("active");w.classList.add("active");}sync();}
  function sync(){const arr=Array.from(selected).map(Number).sort((a,b)=>a-b);const val=arr.join(",");dhembiInput.value=dhembiDisplay.value=val;badge.textContent=val||"asnjë";}
  mountRow("upperLeft",U_LEFT);mountRow("upperRight",U_RIGHT);mountRow("lowerLeft",L_LEFT);mountRow("lowerRight",L_RIGHT);
  (function preload(){const raw=dhembiInput.value||dhembiDisplay.value||"";if(!raw)return;raw.split(",").map(s=>s.trim()).filter(Boolean).forEach(c=>{selected.add(c);document.querySelector(`[data-code="${c}"]`)?.classList.add("active");document.querySelector(`[data-code="${c}"]`)?.parentElement.classList.add("active");});sync();})();
  document.getElementById("btnClear").addEventListener("click",()=>{selected.clear();document.querySelectorAll("[data-code].active").forEach(n=>{n.classList.remove("active");n.parentElement?.classList.remove("active");});sync();});
  document.getElementById("btnInvert").addEventListener("click",()=>{document.querySelectorAll("[data-code]").forEach(n=>{const c=n.dataset.code;if(selected.has(c)){selected.delete(c);n.classList.remove("active");n.parentElement?.classList.remove("active");}else{selected.add(c);n.classList.add("active");n.parentElement?.classList.add("active");}});sync();});

  const fldAgreement=document.getElementById("fldAgreement"),
        fldIncluded=document.getElementById("fldIncluded"),
        priceRow=document.getElementById("priceRow"),
        vlera=document.getElementById("fldVlera");
  function togglePriceFields(){const included=fldIncluded.checked;priceRow.querySelectorAll("input").forEach(inp=>{if(included)inp.value="";inp.disabled=included;});
    priceRow.classList.toggle("opacity-55",included);priceRow.classList.toggle("pointer-events-none",included);}
  fldAgreement.addEventListener("change",()=>{fldIncluded.checked=!!fldAgreement.value;togglePriceFields();});
  fldIncluded.addEventListener("change",togglePriceFields);togglePriceFields();

  document.getElementById("historyForm").addEventListener("submit", e=>{
    const vleraVal=parseFloat(vlera.value)||0;
    const paguarVal=parseFloat(document.getElementById("fldPaguar").value)||0;

    if(vleraVal===0 && paguarVal>0){
      e.preventDefault();
      alert("❌ Nuk mund të regjistrohet pagesë nëse vlera është 0.");
      return;
    }

    
    if(vleraVal===0 && paguarVal===0) return;
    if(fldIncluded.checked || fldAgreement.value) return;

    // ❌ Në raste tjera kërko vlerë ose marrëveshje
    if(!fldAgreement.value && vleraVal<=0 && paguarVal<=0){
      e.preventDefault();
      alert("Ju lutem shënoni vlerën e shërbimit ose zgjidhni një marrëveshje.");
    }
  });

  const radioPo=document.getElementById("radioPo"),radioJo=document.getElementById("radioJo"),punimFields=document.getElementById("punimFields");
  function togglePunimFields(){if(radioPo.checked){punimFields.classList.remove("hidden");}else{punimFields.querySelectorAll("input,textarea").forEach(el=>el.value="");punimFields.classList.add("hidden");}}
  radioPo.addEventListener("change",togglePunimFields);radioJo.addEventListener("change",togglePunimFields);
  document.addEventListener("DOMContentLoaded",()=>{const hasData=document.querySelector("textarea[name='punim_protetikor']").value.trim()||document.querySelector("input[name='tekniku']").value.trim();if(hasData){radioPo.checked=true;togglePunimFields();}});

