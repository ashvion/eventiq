// Small script to add 'is-loaded' on DOM ready and reveal elements on scroll.
(function(){
  function onReady(){
    document.documentElement.classList.add('is-loaded');

    var reveals = document.querySelectorAll('.reveal');
    if('IntersectionObserver' in window && reveals.length){
      var obs = new IntersectionObserver(function(entries){
        entries.forEach(function(entry){
          if(entry.isIntersecting){
            entry.target.classList.add('reveal-visible');
            obs.unobserve(entry.target);
          }
        });
      }, {threshold:0.12});
      reveals.forEach(function(el){ obs.observe(el); });
    } else {
      // fallback: reveal immediately
      reveals.forEach(function(el){ el.classList.add('reveal-visible'); });
    }
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', onReady);
  } else {
    onReady();
  }
})();
