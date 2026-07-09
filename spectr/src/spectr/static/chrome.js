/**
 * Injects Spectr view assets into the embedded spec document (same origin).
 */
(function () {
  "use strict";

  var JQUERY_URL = "https://code.jquery.com/jquery-3.7.1.min.js";
  var MARKDOWN_IT_URL =
    "https://cdn.jsdelivr.net/npm/markdown-it@14.1.0/dist/markdown-it.min.js";
  var DOMPURIFY_URL =
    "https://cdn.jsdelivr.net/npm/dompurify@3.2.4/dist/purify.min.js";
  var MERMAID_URL =
    "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js";

  var VIEW_SCRIPTS = [
    { id: "spectr-jquery", src: JQUERY_URL },
    { id: "spectr-markdown-it", src: MARKDOWN_IT_URL },
    { id: "spectr-dompurify", src: DOMPURIFY_URL },
    { id: "spectr-mermaid", src: MERMAID_URL },
    { id: "spectr-view-js", src: "/__spectr__/view.js" },
  ];

  function appendToHead(doc, node) {
    var head = doc.head || doc.getElementsByTagName("head")[0] || doc.documentElement;
    head.appendChild(node);
  }

  function injectStylesheet(doc) {
    if (doc.getElementById("spectr-view-css")) {
      return;
    }
    var link = doc.createElement("link");
    link.id = "spectr-view-css";
    link.rel = "stylesheet";
    link.href = "/__spectr__/view.css";
    appendToHead(doc, link);
  }

  function injectScript(doc, id, src, done) {
    if (doc.getElementById(id)) {
      if (typeof done === "function") {
        done();
      }
      return;
    }
    var script = doc.createElement("script");
    script.id = id;
    script.src = src;
    script.onload = function () {
      if (typeof done === "function") {
        done();
      }
    };
    script.onerror = function () {
      if (typeof done === "function") {
        done(new Error("failed to load " + src));
      }
    };
    appendToHead(doc, script);
  }

  function injectScripts(doc, specs, index, done) {
    if (index >= specs.length) {
      if (typeof done === "function") {
        done();
      }
      return;
    }
    var spec = specs[index];
    injectScript(doc, spec.id, spec.src, function (err) {
      if (err) {
        if (typeof done === "function") {
          done(err);
        }
        return;
      }
      injectScripts(doc, specs, index + 1, done);
    });
  }

  function runEnhance(doc) {
    var win = doc.defaultView;
    if (win && typeof win.spectrEnhanceView === "function") {
      win.spectrEnhanceView(doc);
    }
  }

  function injectView(doc) {
    if (!doc.body) {
      return;
    }
    injectStylesheet(doc);
    injectScripts(doc, VIEW_SCRIPTS, 0, function (err) {
      if (!err) {
        runEnhance(doc);
      }
    });
  }

  function wireFrame(frame) {
    if (!frame || frame.dataset.spectrWired) {
      return;
    }
    frame.dataset.spectrWired = "1";
    frame.addEventListener("load", function () {
      var doc = frame.contentDocument;
      if (doc) {
        injectView(doc);
      }
    });
    var doc = frame.contentDocument;
    if (doc && doc.readyState === "complete") {
      injectView(doc);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("iframe.spectr-spec-frame").forEach(wireFrame);
  });
})();
