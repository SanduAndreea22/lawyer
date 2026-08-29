document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("textarea[maxlength]").forEach((textarea) => {
    const max = textarea.getAttribute("maxlength");
    const counter = document.createElement("small");
    counter.className = "char-counter";
    const update = () => {
      counter.textContent = `${textarea.value.length}/${max} characters`;
    };
    update();
    textarea.addEventListener("input", update);
    textarea.insertAdjacentElement("afterend", counter);
  });
});
