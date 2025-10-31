function toggleSidebar(){
  const sb = document.getElementById('sidebar');
  const ov = document.getElementById('overlay');
  const isOpen = !sb.classList.contains('-translate-x-full');

  if(isOpen){
    sb.classList.add('-translate-x-full');
    ov.classList.add('hidden');
  }else{
    sb.classList.remove('-translate-x-full');
    ov.classList.remove('hidden');
  }
}