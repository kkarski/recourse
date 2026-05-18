/**
 * Spectr spec view: section headings, Markdown bodies, fixed outline (jQuery).
 * Loaded into the spec iframe by chrome.js (after jQuery, markdown-it, DOMPurify).
 */
(function (global) {
  "use strict";

  var SECTION_H2 = {
    definitions: "Definitions",
    "business-rules": "Business rules",
    "acceptance-criteria": "Acceptance criteria",
    questions: "Questions",
    feedback: "Feedback",
    plan: "Plan",
  };

  var NESTED_H3 = {
    actors: "Actors",
    preconditions: "Preconditions",
    postconditions: "Postconditions",
    "business-rules": "Business rules",
    "acceptance-criteria": "Acceptance criteria",
    questions: "Questions",
  };

  var MARKDOWN_P_TYPES = [
    "desc",
    "business-rule",
    "acceptance-criteria",
    "question",
    "answer",
    "feedback",
    "actor",
    "precondition",
    "postcondition",
  ];

  var usedIds = Object.create(null);

  function uniqueId(preferred) {
    var base =
      (preferred || "section")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "") || "section";
    var id = base;
    var n = 2;
    while (usedIds[id]) {
      id = base + "-" + n;
      n += 1;
    }
    usedIds[id] = true;
    return id;
  }

  function insertHeading(doc, before, tag, text, idHint) {
    var h = doc.createElement(tag);
    h.textContent = text;
    h.id = uniqueId(idHint || text);
    before.parentNode.insertBefore(h, before);
    return h;
  }

  function enhanceDefinitions(defDiv, doc) {
    var lastSection = null;
    var children = Array.prototype.slice.call(defDiv.children);
    children.forEach(function (ch) {
      if (ch.tagName !== "P" || ch.getAttribute("type") !== "definition") {
        return;
      }
      var sec = (ch.getAttribute("section") || "").trim();
      if (sec && sec !== lastSection) {
        insertHeading(doc, ch, "h3", sec, "def-" + sec);
        lastSection = sec;
      }
    });
  }

  function enhanceUseCase(uc, doc) {
    var h3 = uc.querySelector(":scope > h3");
    var title = h3 ? h3.textContent.trim() : "Use case";
    var sid = (uc.getAttribute("sid") || "").trim();
    var label = sid ? sid + " " + title : title;
    var idHint = sid || title;

    if (h3) {
      var h2 = doc.createElement("h2");
      h2.textContent = label;
      h2.id = uniqueId(idHint);
      h3.parentNode.replaceChild(h2, h3);
    } else {
      insertHeading(doc, uc.firstChild || uc, "h2", label, idHint);
    }

    var trigger = uc.querySelector(':scope > p[type="trigger"]');
    if (trigger) {
      insertHeading(doc, trigger, "h4", "Trigger", "trigger");
    }

    Array.prototype.forEach.call(uc.querySelectorAll(":scope > div[type]"), function (nested) {
      var t = nested.getAttribute("type");
      var label3 = NESTED_H3[t] || t;
      insertHeading(doc, nested, "h3", label3, "uc-" + t);
    });
  }

  function enhanceBody(body, doc) {
    Array.prototype.forEach.call(body.querySelectorAll(':scope > ul[type="references"]'), function (ul) {
      insertHeading(doc, ul, "h2", "References", "references");
    });

    Array.prototype.forEach.call(body.querySelectorAll(":scope > div[type]"), function (div) {
      var t = div.getAttribute("type");
      if (t === "use-case") {
        enhanceUseCase(div, doc);
        return;
      }
      var label = SECTION_H2[t] || t;
      insertHeading(doc, div, "h2", label, t);
      if (t === "definitions") {
        enhanceDefinitions(div, doc);
      }
    });

    var h1 = body.querySelector(":scope > h1");
    if (h1 && !h1.id) {
      h1.id = uniqueId("title");
    }
  }

  function createMarkdownRenderer(win) {
    var md = new win.markdownit({ html: false, linkify: true, breaks: false });
    md.renderer.rules.heading_open = function (tokens, idx) {
      var level = tokens[idx].tag.slice(1);
      return '<p class="spectr-md-heading" data-level="' + level + '"><strong>';
    };
    md.renderer.rules.heading_close = function () {
      return "</strong></p>";
    };
    return md;
  }

  function sanitizeMarkdownHtml(win, html) {
    return win.DOMPurify.sanitize(html, {
      ADD_ATTR: ["data-level", "target", "rel"],
      ADD_TAGS: ["code", "pre"],
    });
  }

  function renderMarkdownSource(md, purify, source) {
    var text = (source || "").trim();
    if (!text) {
      return "";
    }
    return purify(md.render(text));
  }

  function setRenderedHtml(el, html) {
    el.classList.add("spectr-markdown");
    el.innerHTML = html;
  }

  function renderPlainParagraph(p, md, purify) {
    var html = renderMarkdownSource(md, purify, p.textContent);
    if (!html) {
      return;
    }
    setRenderedHtml(p, html);
  }

  function definitionBodyText(p) {
    var termSpan = p.querySelector('span[type="term"]');
    if (!termSpan) {
      return p.textContent;
    }
    var parts = [termSpan.tail || ""];
    var seen = false;
    Array.prototype.forEach.call(p.childNodes, function (node) {
      if (node === termSpan) {
        seen = true;
        return;
      }
      if (seen && node.nodeType === 1) {
        parts.push(node.textContent);
      }
    });
    return parts.join("").trim();
  }

  function clearDefinitionBody(p, termSpan) {
    termSpan.tail = "";
    var next = termSpan.nextSibling;
    while (next) {
      var remove = next;
      next = next.nextSibling;
      p.removeChild(remove);
    }
  }

  function renderDefinitionParagraph(p, doc, md, purify) {
    var body = definitionBodyText(p);
    var html = renderMarkdownSource(md, purify, body);
    if (!html) {
      return;
    }
    var termSpan = p.querySelector('span[type="term"]');
    if (termSpan) {
      clearDefinitionBody(p, termSpan);
      var wrap = doc.createElement("span");
      wrap.className = "spectr-markdown spectr-markdown--definition-body";
      wrap.innerHTML = html;
      p.appendChild(wrap);
    } else {
      setRenderedHtml(p, html);
    }
  }

  function renderAllMarkdown(doc) {
    var win = doc.defaultView;
    if (!win || !win.markdownit || !win.DOMPurify) {
      return;
    }
    var md = createMarkdownRenderer(win);
    var purify = function (html) {
      return sanitizeMarkdownHtml(win, html);
    };

    doc.body.querySelectorAll('p[type="desc"]').forEach(function (p) {
      renderPlainParagraph(p, md, purify);
    });

    doc.body.querySelectorAll('p[type="definition"]').forEach(function (p) {
      renderDefinitionParagraph(p, doc, md, purify);
    });

    MARKDOWN_P_TYPES.forEach(function (ptype) {
      if (ptype === "desc") {
        return;
      }
      doc.body.querySelectorAll('p[type="' + ptype + '"]').forEach(function (p) {
        renderPlainParagraph(p, md, purify);
      });
    });

    doc.body.querySelectorAll('div[type="use-case"] > p:not([type="trigger"])').forEach(
      function (p) {
        var pt = (p.getAttribute("type") || "").trim();
        if (pt) {
          return;
        }
        renderPlainParagraph(p, md, purify);
      }
    );

    doc.body.querySelectorAll('ol[type="phase"] li[type="task"]').forEach(function (li) {
      var html = renderMarkdownSource(md, purify, li.textContent);
      if (!html) {
        return;
      }
      setRenderedHtml(li, html);
    });
  }

  function buildNav(doc, $) {
    var $body = $(doc.body);
    var $nav = $("#spectr-doc-nav", doc);
    if (!$nav.length) {
      $nav = $(
        '<nav id="spectr-doc-nav" aria-label="On this page">' +
          '<div class="spectr-doc-nav-title">On this page</div>' +
          "</nav>"
      );
      $body.append($nav);
    }

    var $list = $('<div class="spectr-doc-nav-list"></div>');
    $nav.find(".spectr-doc-nav-list").remove();

    $(doc.body)
      .find("h1, h2, h3, h4")
      .each(function () {
        var el = this;
        var level = parseInt(el.tagName.slice(1), 10);
        if (!el.id) {
          el.id = uniqueId(el.textContent.trim().slice(0, 32));
        }
        var text = (el.textContent || "").trim().replace(/\s+/g, " ");
        if (!text) {
          return;
        }
        var $a = $("<a></a>")
          .attr("href", "#" + el.id)
          .addClass("spectr-nav-h" + level)
          .text(text.length > 72 ? text.slice(0, 69) + "…" : text);
        $list.append($a);
      });

    $nav.append($list);

    var $links = $nav.find("a");
    var headings = $(doc.body).find("h1, h2, h3, h4").get();

    function setActive() {
      var top = $(doc.defaultView).scrollTop() + 72;
      var current = headings[0];
      for (var i = 0; i < headings.length; i += 1) {
        if ($(headings[i]).offset().top <= top) {
          current = headings[i];
        }
      }
      $links.removeClass("active");
      if (current && current.id) {
        $links.filter('[href="#' + current.id + '"]').addClass("active");
      }
    }

    $links.on("click", function (e) {
      e.preventDefault();
      var id = $(this).attr("href").slice(1);
      var $target = $("#" + id, doc);
      if ($target.length) {
        $("html, body", doc).animate(
          { scrollTop: $target.offset().top - 56 },
          280
        );
        if (doc.defaultView.history && doc.defaultView.history.replaceState) {
          doc.defaultView.history.replaceState(null, "", "#" + id);
        }
      }
    });

    $(doc.defaultView).on("scroll.spectrNav resize.spectrNav", setActive);
    setActive();
  }

  function spectrEnhanceView(doc) {
    var $ = doc.defaultView && doc.defaultView.jQuery;
    if (!$ || !doc.body || doc.body.dataset.spectrViewEnhanced) {
      return;
    }
    doc.body.dataset.spectrViewEnhanced = "1";
    doc.body.classList.add("spectr-view-enhanced");
    usedIds = Object.create(null);
    enhanceBody(doc.body, doc);
    renderAllMarkdown(doc);
    buildNav(doc, $);
  }

  global.spectrEnhanceView = spectrEnhanceView;
})(typeof window !== "undefined" ? window : this);
