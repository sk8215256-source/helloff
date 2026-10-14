const toggle = document.getElementById("themeToggle");
if (toggle) {
  const saved = localStorage.getItem("omni-theme");
  if (saved === "light") document.body.classList.add("light");
  toggle.addEventListener("click", () => {
    document.body.classList.toggle("light");
    localStorage.setItem("omni-theme", document.body.classList.contains("light") ? "light" : "dark");
    toggle.animate([{transform:"scale(1)"},{transform:"scale(.82) rotate(-15deg)"},{transform:"scale(1)"}], {duration:260,easing:"ease-out"});
  });
}
document.querySelectorAll(".btn,.icon-btn,.feature-card,.tool-card,.sidebar nav a").forEach(el => {
  el.addEventListener("pointerdown", () => {
    el.animate([{filter:"brightness(1)"},{filter:"brightness(1.25)"},{filter:"brightness(1)"}], {duration:240});
  });
});
document.querySelectorAll('input[type="file"]').forEach(input => input.addEventListener("change", () => {
  const label = input.closest("label");
  if (label && input.files && input.files[0]) label.title = input.files[0].name;
}));
