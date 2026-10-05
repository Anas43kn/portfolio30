const root = document.documentElement;
const toggle = document.getElementById("themeToggle");
const saved = localStorage.getItem("theme");

if (saved) root.setAttribute("data-theme", saved);

if (toggle) {
  toggle.addEventListener("click", () => {
    const current = root.getAttribute("data-theme");
    const next = current === "dark" ? "" : "dark";
    if (next) root.setAttribute("data-theme", next);
    else root.removeAttribute("data-theme");
    localStorage.setItem("theme", next);
  });
}

const revealEls = [...document.querySelectorAll(".reveal")];
if ("IntersectionObserver" in window) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) entry.target.classList.add("is-visible");
    });
  }, { threshold: 0.08 });
  revealEls.forEach((el) => io.observe(el));
} else {
  revealEls.forEach((el) => el.classList.add("is-visible"));
}

const navLinks = [...document.querySelectorAll(".navlink[href^='/#']")];
const sections = navLinks
  .map((link) => document.querySelector(link.getAttribute("href").replace("/", "")))
  .filter(Boolean);

if ("IntersectionObserver" in window) {
  const navIO = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      const id = entry.target.getAttribute("id");
      const link = navLinks.find((item) => item.getAttribute("href") === `/#${id}`);
      if (!link || !entry.isIntersecting) return;
      navLinks.forEach((item) => item.removeAttribute("aria-current"));
      link.setAttribute("aria-current", "true");
    });
  }, { rootMargin: "-45% 0px -45% 0px", threshold: 0.01 });
  sections.forEach((section) => navIO.observe(section));
}

const titleInput = document.querySelector("input[name='title']");
const slugInput = document.querySelector("input[name='slug']");
if (titleInput && slugInput) {
  titleInput.addEventListener("input", () => {
    if (slugInput.dataset.touched === "true" || slugInput.value) return;
    slugInput.value = titleInput.value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  });
  slugInput.addEventListener("input", () => {
    slugInput.dataset.touched = "true";
  });
}
