document.querySelectorAll(".nav-toggle").forEach(function (toggle) {
  toggle.addEventListener("click", function () {
    var links = toggle.closest("nav").querySelector(".links");
    if (!links) return;
    var isOpen = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
  });
});
