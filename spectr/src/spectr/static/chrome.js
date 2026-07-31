/**
 * Injects Spectr view assets into the embedded spec document (same origin).
 * Tailwind (@tailwindcss/browser) + Inter give a Catalyst-inspired look without React.
 */
(function () {
  "use strict";

  var INTER_CSS_URL = "https://rsms.me/inter/inter.css";
  var TAILWIND_BROWSER_URL =
    "https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4";
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

  function injectLink(doc, id, href, rel) {
    if (doc.getElementById(id)) {
      return;
    }
    var link = doc.createElement("link");
    link.id = id;
    link.rel = rel || "stylesheet";
    link.href = href;
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

  function injectViewCss(doc, done) {
    if (doc.getElementById("spectr-view-css")) {
      if (typeof done === "function") {
        done();
      }
      return;
    }
    fetch("/__spectr__/view.css")
      .then(function (res) {
        if (!res.ok) {
          throw new Error("failed to load view.css");
        }
        return res.text();
      })
      .then(function (css) {
        var style = doc.createElement("style");
        style.id = "spectr-view-css";
        style.type = "text/tailwindcss";
        style.textContent = css;
        appendToHead(doc, style);
        if (typeof done === "function") {
          done();
        }
      })
      .catch(function (err) {
        if (typeof done === "function") {
          done(err);
        }
      });
  }

  function runEnhance(doc) {
    var win = doc.defaultView;
    if (win && typeof win.spectrEnhanceView === "function") {
      win.spectrEnhanceView(doc);
    }
  }

  function injectView(doc) {
    if (!doc.body || doc.body.dataset.spectrAssetsInjected) {
      return;
    }
    doc.body.dataset.spectrAssetsInjected = "1";

    injectLink(doc, "spectr-inter-css", INTER_CSS_URL);
    injectScript(doc, "spectr-tailwind-browser", TAILWIND_BROWSER_URL, function (twErr) {
      if (twErr) {
        return;
      }
      injectViewCss(doc, function (cssErr) {
        if (cssErr) {
          return;
        }
        injectScripts(doc, VIEW_SCRIPTS, 0, function (err) {
          if (!err) {
            runEnhance(doc);
          }
        });
      });
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
