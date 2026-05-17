// Persistent legal disclaimer banner for Regularización Ya chatbot
(function () {
  function injectBanner() {
    if (document.getElementById("legal-disclaimer")) return;

    const banner = document.createElement("div");
    banner.id = "legal-disclaimer";
    banner.innerHTML =
      '<div class="disclaimer-inner">' +
        '<span class="disclaimer-icon">⚠️</span>' +
        '<p><strong>¡IMPORTANTE!</strong> Este asistente virtual brinda información general y no sustituye el asesoramiento legal individualizado. ' +
        'Encuentra la información oficial más actualizada en ' +
        '<a href="https://www.inclusion.gob.es/regularizacion" target="_blank" rel="noopener noreferrer">inclusion.gob.es/regularizacion</a>.</p>' +
        '<button class="disclaimer-close" aria-label="Cerrar aviso" title="Cerrar">✕</button>' +
      "</div>";

    // Close button hides the banner
    banner.querySelector(".disclaimer-close").addEventListener("click", function () {
      banner.style.display = "none";
    });

    document.body.appendChild(banner);
  }

  // Inject as soon as possible
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectBanner);
  } else {
    injectBanner();
  }

  // Fallback: re-inject if the banner gets removed (SPA re-renders)
  const observer = new MutationObserver(function () {
    if (!document.getElementById("legal-disclaimer")) {
      injectBanner();
    }
  });

  observer.observe(document.body || document.documentElement, {
    childList: true,
    subtree: false,
  });
})();
