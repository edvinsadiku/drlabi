  function onModeChange(val){
    document.getElementById('fld_day').classList.toggle('hidden',  val!=='day');
    document.getElementById('fld_week').classList.toggle('hidden', val!=='week');
    document.getElementById('fld_month').classList.toggle('hidden',val!=='month');
    document.getElementById('fld_year').classList.toggle('hidden', val!=='year');
  }
  document.addEventListener("DOMContentLoaded", function() {
    if(document.getElementById("day-picker")){
      flatpickr("#day-picker", { dateFormat: "Y-m-d", defaultDate: "{{ picked_day }}" });
    }
  });
