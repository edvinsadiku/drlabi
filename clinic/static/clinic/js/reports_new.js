function onModeChange(mode) {
  ['day','week','month','year'].forEach(value => document.getElementById('fld_'+value)?.classList.toggle('hidden', mode!==value));
}
document.addEventListener('DOMContentLoaded', () => {
  const form=document.getElementById('reports-filters');
  if(!form) return;
  const pad=value=>String(value).padStart(2,'0');
  document.querySelectorAll('[data-report-preset]').forEach(button=>button.addEventListener('click',()=>{
    const now=new Date();const preset=button.dataset.reportPreset;const mode=preset==='today'?'day':preset;
    form.elements.mode.value=mode;onModeChange(mode);
    if(mode==='day') form.elements.day.value=`${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}`;
    if(mode==='month') form.elements.month.value=`${now.getFullYear()}-${pad(now.getMonth()+1)}`;
    if(mode==='year') form.elements.year.value=String(now.getFullYear());
    if(mode==='week') {
      const d=new Date(Date.UTC(now.getFullYear(),now.getMonth(),now.getDate()));d.setUTCDate(d.getUTCDate()+4-(d.getUTCDay()||7));
      const week=Math.ceil(((d-new Date(Date.UTC(d.getUTCFullYear(),0,1)))/86400000+1)/7);
      form.elements.week.value=`${d.getUTCFullYear()}-W${pad(week)}`;
    }
    form.requestSubmit();
  }));
});
