(function () {
  var els = document.querySelectorAll(".reveal");
  if (!els.length) return;

  if (!("IntersectionObserver" in window)) {
    els.forEach(function (el) {
      el.classList.add("visible");
    });
    return;
  }

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  els.forEach(function (el) {
    observer.observe(el);
  });

  // Safety net: below-the-fold content only reveals once the user scrolls
  // to it, which never happens for a tool that captures the page without
  // scrolling (a full-page screenshot extension, a PDF export, some
  // crawlers) - or if this script's observer somehow never fires. Rather
  // than leave that content permanently invisible, force it visible after
  // a short grace period regardless of scroll position.
  window.setTimeout(function () {
    els.forEach(function (el) {
      el.classList.add("visible");
    });
    observer.disconnect();
  }, 2000);
})();
