(function () {
  var figures = document.querySelectorAll("[data-count-to]");
  if (!figures.length) return;

  function formatNumber(value) {
    return value.toLocaleString("en-US");
  }

  function animateCount(el) {
    var target = parseInt(el.getAttribute("data-count-to"), 10);
    var suffix = el.getAttribute("data-suffix") || "";
    var duration = 1400;
    var start = null;

    function step(timestamp) {
      if (start === null) start = timestamp;
      var progress = Math.min((timestamp - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var current = Math.round(eased * target);
      el.textContent = formatNumber(current) + suffix;
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        el.textContent = formatNumber(target) + suffix;
      }
    }

    window.requestAnimationFrame(step);
  }

  if (!("IntersectionObserver" in window)) {
    figures.forEach(animateCount);
    return;
  }

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.5 }
  );

  figures.forEach(function (el) {
    observer.observe(el);
  });
})();
