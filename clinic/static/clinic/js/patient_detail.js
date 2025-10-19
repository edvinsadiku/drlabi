// Klik rreshti (arkiva)
document.addEventListener('click', function (e) {
  const stop = e.target.closest('.click-stop');
  if (stop) return;
  const row = e.target.closest('tr[data-href]');
  if (row) window.location.href = row.dataset.href;
});

document.addEventListener('keydown', function (e) {
  if ((e.key === 'Enter' || e.key === ' ') && document.activeElement?.matches('tr[data-href]')) {
    e.preventDefault();
    window.location.href = document.activeElement.dataset.href;
  }
});

// Multi-select për pagesa (histori me borxh)
(function(){
  const boxes = Array.from(document.querySelectorAll('input[name="history_ids"]'));
  const info  = document.getElementById('selectionInfo');
  const selAll = document.getElementById('btnSelectAll');
  const clrAll = document.getElementById('btnClearAll');

  function updateInfo(){
    let c = 0, s = 0;
    boxes.forEach(cb=>{
      if(cb.checked){
        c++;
        s += parseFloat(cb.dataset.debt || '0') || 0;
      }
    });
    if(info) info.textContent = `Të zgjedhura: ${c} • Borxh total: ${s.toFixed(2)}€`;
  }

  boxes.forEach(cb=>cb && cb.addEventListener('change', updateInfo));
  selAll && selAll.addEventListener('click', ()=>{ boxes.forEach(cb=>cb.checked = true); updateInfo(); });
  clrAll && clrAll.addEventListener('click', ()=>{ boxes.forEach(cb=>cb.checked = false); updateInfo(); });
  updateInfo();
})();

// -------- Modal CareHistory --------
let __chCurrentId=null;
window.openCareHistoryModal = function(id){
  __chCurrentId=id;
  const modal=document.getElementById("careHistoryModal");
  const card=document.getElementById("careHistoryCard");
  modal.classList.remove("hidden"); modal.classList.add("flex");
  setTimeout(()=>{card.classList.remove("scale-95","opacity-0");card.classList.add("scale-100","opacity-100");},10);

  fetch(`/care-history/${id}/json/`,{headers:{"X-Requested-With":"XMLHttpRequest"}})
    .then(r=>r.ok?r.json():Promise.reject())
    .then(d=>{
      document.getElementById("chDate").textContent=d.date||"—";
      document.getElementById("chTooth").textContent=d.tooth||"—";
      document.getElementById("chDiagnosis").textContent=d.diagnosis||"—";
      document.getElementById("chTreatment").textContent=d.treatment||"—";
      document.getElementById("chAmount").textContent=(d.amount!=null?d.amount:"0.00")+ "€";
      document.getElementById("chPaid").textContent=(d.paid!=null?d.paid:"0.00") + "€";
      document.getElementById("chDebt").textContent=(d.debt!=null?d.debt:"0.00") + "€";
      document.getElementById("chDoctor").textContent=d.doctor||"—";
      document.getElementById("chTechnician").textContent=d.technician||d.tekniku||"—";
      document.getElementById("chPunim").textContent=d.punim_protetikor||"—";
      document.getElementById("chNotes").textContent=d.notes||"—";
      const agrWrap=document.getElementById("chAgreementWrap");
      const agr=document.getElementById("chAgreement");
      if(d.included_in_agreement && d.agreement && (d.agreement.title||d.agreement.id)){
        agr.textContent=`#${d.agreement.id||""} ${d.agreement.title||""}`.trim();
        agrWrap.classList.remove("hidden");
      } else { agrWrap.classList.add("hidden"); }
      const createdEl=document.getElementById("chCreated");
      const parts=[]; if(d.created_by) parts.push(`Nga: ${d.created_by}`);
      if(d.created_at){ try{ parts.push(new Date(d.created_at).toLocaleString()); }catch(_){} }
      createdEl.textContent=parts.join(" • ")||"";
    })
    .catch(()=>{ document.getElementById("chDiagnosis").textContent="Gabim gjatë ngarkimit."; });
}

window.closeCareHistoryModal = function(){
  const modal=document.getElementById("careHistoryModal");
  const card=document.getElementById("careHistoryCard");
  card.classList.add("scale-95","opacity-0");
  setTimeout(()=>{modal.classList.add("hidden"); modal.classList.remove("flex");},150);
}

document.getElementById("careHistoryModal")?.addEventListener("click",e=>{
  if(e.target.id==="careHistoryModal") closeCareHistoryModal();
});
document.addEventListener("keydown",e=>{
  if(e.key==="Escape") closeCareHistoryModal();
});
