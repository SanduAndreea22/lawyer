(function () {
  var bar = document.getElementById("sticky-book-cta");
  if (!bar) return;

  var threshold = window.innerHeight * 0.6;
  var ticking = false;

  function update() {
    if (window.scrollY > threshold) {
      bar.classList.add("visible");
    } else {
      bar.classList.remove("visible");
    }
    ticking = false;
  }

  window.addEventListener(
    "scroll",
    function () {
      if (!ticking) {
        window.requestAnimationFrame(update);
        ticking = true;
      }
    },
    { passive: true }
  );

  update();
})();
