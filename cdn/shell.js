/* Shared shell behaviour: the light/dark toggle. Persists to localStorage and
   applies `data-theme` on <html> before paint so there is no flash. */
(function () {
  var KEY = "ui-theme";
  var saved = localStorage.getItem(KEY);
  var theme = saved || (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
  document.documentElement.dataset.theme = theme;
  function bind() {
    document.querySelectorAll(".ui-theme-toggle").forEach(function (el) {
      el.addEventListener("click", function () {
        var next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
        document.documentElement.dataset.theme = next;
        localStorage.setItem(KEY, next);
      });
    });
  }
  if (document.readyState !== "loading") bind();
  else document.addEventListener("DOMContentLoaded", bind);
})();
