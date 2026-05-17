// Inyecta el aviso legal directamente en el DOM, sin depender de .watermark
(function () {
  var BANNER_ID = "ry-legal-disclaimer";
  var DISCLAIMER_HTML =
    "⚠️ <strong>¡IMPORTANTE!</strong> " +
    "Este asistente virtual brinda información general y no sustituye el asesoramiento legal individualizado. " +
    "Encuentra la información oficial más actualizada en " +
    '<a href="https://www.inclusion.gob.es/regularizacion" target="_blank" rel="noopener noreferrer">' +
    "inclusion.gob.es/regularizacion</a>.";

  function injectBanner() {
    if (document.getElementById(BANNER_ID)) return;

    var banner = document.createElement("div");
    banner.id = BANNER_ID;
    banner.innerHTML = DISCLAIMER_HTML;
    document.body.appendChild(banner);
  }

  // Ocultar el watermark original de Chainlit para evitar duplicados
  function hideWatermark() {
    var style = document.getElementById("ry-hide-watermark");
    if (style) return;
    var s = document.createElement("style");
    s.id = "ry-hide-watermark";
    s.textContent = ".watermark { display: none !important; }";
    document.head.appendChild(s);
  }

  function init() {
    hideWatermark();
    injectBanner();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
