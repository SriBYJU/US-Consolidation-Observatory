(function(){
  const loadUi=()=>{const ui=document.createElement('script');ui.src='assets/app-ui.js';ui.defer=true;document.head.appendChild(ui)};
  if(typeof $!=='undefined'){loadUi();return}
  const core=document.createElement('script');core.src='assets/app-core.js';core.onload=loadUi;core.onerror=()=>console.error('Failed to load app core');document.head.appendChild(core);
})();
