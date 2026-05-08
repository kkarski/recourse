/**
 * Injects Spectr read typography into the embedded spec document (same origin).
 * Extend this file for future client-side behavior (e.g. outline, search).
 */
(function () {
  function injectStylesheet(frame) {
    var doc = frame.contentDocument;
    if (!doc) return;
    if (doc.getElementById("spectr-view-css")) return;
    var link = doc.createElement("link");
    link.id = "spectr-view-css";
    link.rel = "stylesheet";
    link.href = "/__spectr__/view.css";
    var head = doc.head || doc.getElementsByTagName("head")[0] || doc.documentElement;
    head.appendChild(link);
  }

  function wireFrame(frame) {
    if (!frame || frame.dataset.spectrWired) return;
    frame.dataset.spectrWired = "1";
    frame.addEventListener("load", function () {
      injectStylesheet(frame);
    });
    if (frame.contentDocument && frame.contentDocument.readyState === "complete") {
      injectStylesheet(frame);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("iframe.spectr-spec-frame").forEach(wireFrame);
  });
})();
