  function onModeChange(val){
    document.getElementById('fld_day').classList.toggle('hidden',  val!=='day');
    document.getElementById('fld_week').classList.toggle('hidden', val!=='week');
    document.getElementById('fld_month').classList.toggle('hidden',val!=='month');
    document.getElementById('fld_year').classList.toggle('hidden', val!=='year');
  }
  // re-render icons if you use lucide in this page
  document.addEventListener('DOMContentLoaded', () => { if(window.lucide){ lucide.createIcons(); } });
