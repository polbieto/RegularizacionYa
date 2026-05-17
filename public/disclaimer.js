// Replace Chainlit's default watermark with the legal disclaimer
(function () {
  var SELECTOR = ".watermark";
  var DISCLAIMER_HTML =
    "⚠️ <strong>¡IMPORTANTE!</strong> " +
    "Este asistente virtual brinda información general y no sustituye el asesoramiento legal individualizado. " +
    "Encuentra la información oficial más actualizada en " +
    '<a href="https://www.inclusion.gob.es/regularizacion" target="_blank" rel="noopener noreferrer">' +
    "inclusion.gob.es/regularizacion</a>.";

  function replaceWatermark() {
    var el = document.querySelector(SELECTOR);
    if (!el || el.dataset.replaced) return;

    el.dataset.replaced = "true";

    // Clear all inline styles and children
    el.removeAttribute("style");
    el.innerHTML = DISCLAIMER_HTML;
  }

  // Watch for the watermark to be rendered by React
  var observer = new MutationObserver(function () {
    replaceWatermark();
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true,
  });

  if (document.readyState !== "loading") {
    replaceWatermark();
  } else {
    document.addEventListener("DOMContentLoaded", replaceWatermark);
  }
})();
