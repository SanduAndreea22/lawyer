(function () {
  var bar = document.getElementById("sticky-book-cta");
  if (!bar) return;

  var threshold = window.innerHeight * 0.6;
  var lastY = window.scrollY;
  var ticking = false;
  var idleTimer = null;

  function setVisible(visible) {
    if (bar.classList.contains("visible") === visible) return;
    bar.classList.toggle("visible", visible);
    // Reserve real space for the bar instead of overlaying content -
    // otherwise it permanently covers the footer (and whatever else
    // happens to land at the bottom of the screen) once it's showing.
    document.body.style.paddingBottom = visible ? bar.offsetHeight + "px" : "";
  }

  function isNearBottom() {
    return (
      window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4
    );
  }

  function onScroll() {
    var y = window.scrollY;
    if (y <= threshold) {
      setVisible(false);
    } else if (y < lastY || isNearBottom()) {
      // Scrolling up, or genuinely at the end of the page - show it.
      setVisible(true);
    } else {
      // Actively scrolling down through content - stay out of the way
      // instead of sliding over whatever the reader is looking at.
      setVisible(false);
    }
    lastY = y;

    clearTimeout(idleTimer);
    idleTimer = setTimeout(function () {
      if (window.scrollY > threshold) setVisible(true);
    }, 250);
  }

  window.addEventListener(
    "scroll",
    function () {
      if (!ticking) {
        window.requestAnimationFrame(function () {
          onScroll();
          ticking = false;
        });
        ticking = true;
      }
    },
    { passive: true }
  );

  onScroll();
})();
