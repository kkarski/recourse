/**
 * Spectr spec view: section headings, Markdown bodies, fixed outline (jQuery).
 * Loaded into the spec iframe by chrome.js (after jQuery, markdown-it, DOMPurify).
 */
(function (global) {
  "use strict";

  var SECTION_H2 = {
    definitions: "Definitions",
    "term-fact-model": "Term fact model",
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

  var UC_STRUCTURED_P_HEADINGS = {
    "scope-preconditions": "Scope & preconditions",
    trigger: "Trigger",
    "main-flow": "Main flow",
    "post-conditions": "Post conditions",
  };

  var UC_FLOW_P_TYPES = {
    "scope-preconditions": true,
    "main-flow": true,
    "post-conditions": true,
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

  function sidBadgeClass(sid) {
    var prefix = (sid || "").split("-")[0];
    if (prefix === "br") {
      return "spectr-sid-badge spectr-sid-badge--br";
    }
    if (prefix === "ac") {
      return "spectr-sid-badge spectr-sid-badge--ac";
    }
    if (prefix === "uc") {
      return "spectr-sid-badge spectr-sid-badge--uc";
    }
    return "spectr-sid-badge";
  }

  function prependSidBadge(el, doc) {
    var sid = (el.getAttribute("sid") || "").trim();
    if (!sid || el.querySelector(":scope > .spectr-sid-badge")) {
      return;
    }
    var badge = doc.createElement("span");
    badge.className = sidBadgeClass(sid);
    badge.textContent = sid;
    el.insertBefore(badge, el.firstChild);
  }

  function enhanceUseCase(uc, doc) {
    var h3 = uc.querySelector(":scope > h3");
    var title = h3 ? h3.textContent.trim() : "Use case";
    var sid = (uc.getAttribute("sid") || "").trim();
    var idHint = sid || title;

    if (h3) {
      var h2 = doc.createElement("h2");
      h2.id = uniqueId(idHint);
      if (sid) {
        var badge = doc.createElement("span");
        badge.className = sidBadgeClass(sid);
        badge.textContent = sid;
        h2.appendChild(badge);
        h2.appendChild(doc.createTextNode(" " + title));
      } else {
        h2.textContent = title;
      }
      h3.parentNode.replaceChild(h2, h3);
    } else {
      insertHeading(doc, uc.firstChild || uc, "h2", title, idHint);
      if (sid) {
        var inserted = uc.querySelector(":scope > h2");
        if (inserted) {
          inserted.setAttribute("sid", sid);
          prependSidBadge(inserted, doc);
        }
      }
    }

    Object.keys(UC_STRUCTURED_P_HEADINGS).forEach(function (ptype) {
      var el = uc.querySelector(':scope > p[type="' + ptype + '"]');
      if (el) {
        insertHeading(doc, el, "h4", UC_STRUCTURED_P_HEADINGS[ptype], ptype);
      }
    });

    if (!uc.querySelector(':scope > p[type="main-flow"]')) {
      var legacyFlow = uc.querySelector(":scope > p:not([type])");
      if (legacyFlow) {
        insertHeading(doc, legacyFlow, "h4", "Main flow", "main-flow");
      }
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
    return new win.markdownit({ html: false, linkify: true, breaks: false });
  }

  function sanitizeMarkdownHtml(win, html) {
    return win.DOMPurify.sanitize(html, {
      ADD_ATTR: ["target", "rel"],
      ADD_TAGS: ["code", "pre"],
    });
  }

  function dedentMarkdownSource(source) {
    var lines = String(source || "").replace(/\r\n/g, "\n").split("\n");
    var indents = [];
    lines.forEach(function (line) {
      if (!line.trim()) {
        return;
      }
      var m = line.match(/^(\s+)/);
      if (m) {
        indents.push(m[1].length);
      }
    });
    if (!indents.length) {
      return lines.join("\n").trim();
    }
    var strip = Math.min.apply(null, indents);
    return lines
      .map(function (line) {
        if (!line.trim()) {
          return "";
        }
        if (line.length >= strip && /^\s+$/.test(line.slice(0, strip))) {
          return line.slice(strip);
        }
        return line;
      })
      .join("\n")
      .trim();
  }

  function renderMarkdownSource(md, purify, source) {
    var text = dedentMarkdownSource(source);
    if (!text) {
      return "";
    }
    return purify(md.render(text));
  }

  function setRenderedHtml(el, html) {
    el.classList.add("spectr-markdown");
    el.innerHTML = html;
  }

  function isUseCaseFlowParagraph(p) {
    var pt = (p.getAttribute("type") || "").trim();
    if (UC_FLOW_P_TYPES[pt]) {
      return true;
    }
    if (pt) {
      return false;
    }
    var parent = p.parentElement;
    return !!(parent && parent.getAttribute("type") === "use-case");
  }

  function isBlockMarkdownParagraph(p) {
    if ((p.getAttribute("type") || "").trim() === "desc") {
      return true;
    }
    return isUseCaseFlowParagraph(p);
  }

  function replaceWithMarkdownBlock(p, html) {
    var doc = p.ownerDocument;
    var block = doc.createElement("div");
    block.className = "spectr-markdown";
    var id = p.getAttribute("id");
    if (id) {
      block.id = id;
    }
    Array.prototype.forEach.call(p.attributes, function (attr) {
      if (attr.name === "id" || attr.name === "type") {
        return;
      }
      block.setAttribute(attr.name, attr.value);
    });
    block.innerHTML = html;
    p.parentNode.replaceChild(block, p);
  }

  function renderPlainParagraph(p, md, purify) {
    var source = p.textContent;
    var badge = p.querySelector(":scope > .spectr-sid-badge");
    if (badge) {
      source = source.replace(badge.textContent, "").replace(/^\s+/, "");
    }
    if ((p.getAttribute("type") || "").trim() === "acceptance-criteria") {
      renderAcceptanceCriteria(p, md, purify, source, badge);
      return;
    }
    var html = renderMarkdownSource(md, purify, source);
    if (!html) {
      return;
    }
    setRenderedHtml(p, html);
    if (badge) {
      p.insertBefore(badge, p.firstChild);
    }
  }

  function renderAcceptanceCriteria(p, md, purify, source, badge) {
    var doc = p.ownerDocument;
    var parts = String(source || "").split(/\b(?=(?:Given|When|Then)\b)/);
    var htmlParts = [];
    parts.forEach(function (part) {
      var m = part.match(/^(Given|When|Then)\b([\s\S]*)$/);
      if (!m) {
        var preamble = renderMarkdownSource(md, purify, part);
        if (preamble) {
          htmlParts.push(preamble);
        }
        return;
      }
      var kw = m[1];
      var rest = m[2].replace(/^\s+/, " ");
      var restHtml = renderMarkdownSource(md, purify, rest.trim());
      // Prefer inline rest text; strip wrapping <p> from markdown-it.
      restHtml = String(restHtml || "")
        .replace(/^<p>/, "")
        .replace(/<\/p>\s*$/, "");
      if (!restHtml && rest.trim()) {
        restHtml = purify(md.renderInline(rest.trim()));
      } else if (!restHtml) {
        restHtml = "";
      }
      htmlParts.push(
        '<span class="spectr-ac-clause spectr-ac-clause--' +
          kw.toLowerCase() +
          '"><span class="spectr-ac-kw">' +
          kw +
          "</span> " +
          restHtml +
          "</span>"
      );
    });
    var html = htmlParts.join("");
    if (!html) {
      return;
    }
    setRenderedHtml(p, html);
    if (badge) {
      p.insertBefore(badge, p.firstChild);
    }
  }

  function renderBlockMarkdownParagraph(p, md, purify) {
    var html = renderMarkdownSource(md, purify, p.textContent);
    if (!html) {
      return;
    }
    replaceWithMarkdownBlock(p, html);
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

  function renderMermaidDiagrams(doc) {
    var win = doc.defaultView;
    if (!win || !win.mermaid) {
      return;
    }
    var nodes = doc.body.querySelectorAll('p[type="mermaid"]');
    if (!nodes.length) {
      return;
    }
    win.mermaid.initialize({
      startOnLoad: false,
      securityLevel: "loose",
      er: { useMaxWidth: true },
    });
    Array.prototype.forEach.call(nodes, function (p) {
      var source = (p.textContent || "").trim();
      if (!source) {
        return;
      }
      var host = doc.createElement("div");
      host.className = "spectr-mermaid";
      var id = p.getAttribute("id");
      if (id) {
        host.id = id;
      }
      var pre = doc.createElement("pre");
      pre.className = "mermaid";
      pre.textContent = source;
      host.appendChild(pre);
      p.parentNode.replaceChild(host, p);
    });
    try {
      win.mermaid.run({ querySelector: ".spectr-mermaid pre.mermaid" });
    } catch (_err) {
      /* leave source pre in place if render fails */
    }
  }

  function decorateEntityBadges(doc) {
    doc.body
      .querySelectorAll(
        'p[type="business-rule"][sid], p[type="acceptance-criteria"][sid]'
      )
      .forEach(function (p) {
        prependSidBadge(p, doc);
      });
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

    doc.body.querySelectorAll("p").forEach(function (p) {
      if (!isBlockMarkdownParagraph(p)) {
        return;
      }
      renderBlockMarkdownParagraph(p, md, purify);
    });

    doc.body.querySelectorAll('ol[type="phase"] li[type="task"]').forEach(function (li) {
      var html = renderMarkdownSource(md, purify, li.textContent);
      if (!html) {
        return;
      }
      setRenderedHtml(li, html);
    });

    decorateEntityBadges(doc);
  }

  function escapeRegExp(s) {
    return String(s).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function extractAliases(text) {
    var m = String(text || "").match(/Aliases?:\s*([^.]+)/i);
    if (!m) {
      return [];
    }
    return m[1]
      .split(/[,;]/)
      .map(function (a) {
        return a.replace(/\s*\(.*?\)\s*/g, "").trim();
      })
      .filter(function (a) {
        return a && !/^(none|n\/a)$/i.test(a);
      });
  }

  function collectGlossaryPhrases(doc) {
    var phrases = [];
    var seen = Object.create(null);
    doc.body.querySelectorAll('p[type="definition"]').forEach(function (p) {
      var termEl = p.querySelector('span[type="term"]');
      if (!termEl) {
        return;
      }
      var term = termEl.textContent.trim();
      if (!term) {
        return;
      }
      var sid = (p.getAttribute("sid") || "").trim();
      if (!p.id) {
        p.id = sid || uniqueId("def-" + term);
      }
      usedIds[p.id] = true;
      var bodyEl = p.querySelector(".spectr-markdown--definition-body");
      var definition = "";
      if (bodyEl) {
        definition = bodyEl.textContent.trim();
      } else {
        definition = p.textContent.replace(term, "").replace(/^:\s*/, "").trim();
      }
      var aliases = extractAliases(definition);
      definition = definition.replace(/\s*Aliases?:\s*[^.]+\.?/gi, "").trim();
      if (!definition) {
        return;
      }
      var variants = [term].concat(aliases);
      variants.forEach(function (text) {
        var key = text.toLowerCase();
        if (seen[key]) {
          return;
        }
        seen[key] = true;
        phrases.push({
          text: text,
          term: term,
          definition: definition,
        });
      });
    });
    phrases.sort(function (a, b) {
      return b.text.length - a.text.length;
    });
    return phrases;
  }

  function shouldSkipTermTipParent(el) {
    if (!el) {
      return true;
    }
    if (
      el.closest(
        "a, code, pre, .spectr-sid-badge, .spectr-ac-kw, .spectr-term-tip, span[type='term'], p[type='definition']"
      )
    ) {
      return true;
    }
    return false;
  }

  function makeTermTip(doc, matched, meta) {
    var wrap = doc.createElement("span");
    wrap.className = "spectr-term-tip";
    wrap.tabIndex = 0;
    wrap.textContent = matched;

    var panel = doc.createElement("span");
    panel.className = "spectr-term-tip-panel";
    panel.setAttribute("role", "tooltip");

    var title = doc.createElement("span");
    title.className = "spectr-term-tip-title";
    title.textContent = meta.term;

    var body = doc.createElement("span");
    body.className = "spectr-term-tip-body";
    body.textContent = meta.definition;

    panel.appendChild(title);
    panel.appendChild(body);
    wrap.appendChild(panel);
    return wrap;
  }

  function linkifyTextNode(node, pattern, lookup, doc) {
    var text = node.nodeValue;
    if (!text) {
      return;
    }
    pattern.lastIndex = 0;
    if (!pattern.test(text)) {
      pattern.lastIndex = 0;
      return;
    }
    pattern.lastIndex = 0;
    var frag = doc.createDocumentFragment();
    var last = 0;
    var match;
    var found = false;
    while ((match = pattern.exec(text))) {
      found = true;
      if (match.index > last) {
        frag.appendChild(doc.createTextNode(text.slice(last, match.index)));
      }
      var matched = match[1];
      var meta = lookup[matched] || lookup[matched.toLowerCase()];
      if (!meta) {
        frag.appendChild(doc.createTextNode(matched));
      } else {
        frag.appendChild(makeTermTip(doc, matched, meta));
      }
      last = match.index + match[0].length;
    }
    if (!found) {
      return;
    }
    if (last < text.length) {
      frag.appendChild(doc.createTextNode(text.slice(last)));
    }
    node.parentNode.replaceChild(frag, node);
  }

  function linkifyGlossaryInElement(el, pattern, lookup, doc) {
    if (!el || !pattern) {
      return;
    }
    var win = doc.defaultView;
    var NodeFilterRef = win.NodeFilter;
    var walker = doc.createTreeWalker(el, NodeFilterRef.SHOW_TEXT, {
      acceptNode: function (node) {
        if (shouldSkipTermTipParent(node.parentElement)) {
          return NodeFilterRef.FILTER_REJECT;
        }
        if (!node.nodeValue || !node.nodeValue.trim()) {
          return NodeFilterRef.FILTER_REJECT;
        }
        return NodeFilterRef.FILTER_ACCEPT;
      },
    });
    var nodes = [];
    while (walker.nextNode()) {
      nodes.push(walker.currentNode);
    }
    nodes.forEach(function (node) {
      linkifyTextNode(node, pattern, lookup, doc);
    });
  }

  function linkifyGlossaryTerms(doc) {
    var phrases = collectGlossaryPhrases(doc);
    if (!phrases.length) {
      return null;
    }
    var lookup = Object.create(null);
    phrases.forEach(function (p) {
      lookup[p.text] = p;
      lookup[p.text.toLowerCase()] = p;
    });
    var pattern = new RegExp(
      "(?<![A-Za-z0-9_])(" +
        phrases.map(function (p) {
          return escapeRegExp(p.text);
        }).join("|") +
        ")(?![A-Za-z0-9_])",
      "g"
    );

    var selectors = [
      'p[type="business-rule"]',
      'p[type="acceptance-criteria"]',
      'p[type="requirement"]',
      'p[type="requirements"]',
      'p[type="actor"]',
      'p[type="precondition"]',
      'p[type="postcondition"]',
      'p[type="trigger"]',
      'div[type="use-case"] > p:not([type])',
      'div[type="use-case"] > .spectr-markdown',
      'div[type="use-case"] > p[type="main-flow"]',
      'div[type="use-case"] > p[type="scope-preconditions"]',
      'div[type="use-case"] > p[type="post-conditions"]',
    ];
    doc.body.querySelectorAll(selectors.join(",")).forEach(function (el) {
      linkifyGlossaryInElement(el, pattern, lookup, doc);
    });
    return phrases;
  }

  function headingBefore(el) {
    var prev = el.previousElementSibling;
    if (prev && prev.tagName === "H2") {
      return prev;
    }
    return null;
  }

  function takeSectionWithHeading(el, into) {
    if (!el) {
      return;
    }
    var heading = headingBefore(el);
    if (heading) {
      into.push(heading);
    }
    into.push(el);
  }

  function buildTabs(doc, $) {
    var body = doc.body;
    if (body.querySelector(":scope > .spectr-tabs")) {
      return null;
    }

    var defNodes = [];
    takeSectionWithHeading(
      body.querySelector(':scope > div[type="definitions"]'),
      defNodes
    );
    takeSectionWithHeading(
      body.querySelector(':scope > div[type="term-fact-model"]'),
      defNodes
    );

    var ucNodes = [];
    Array.prototype.forEach.call(
      body.querySelectorAll(':scope > div[type="use-case"]'),
      function (uc) {
        ucNodes.push(uc);
      }
    );

    var extraTabs = [];
    ["business-rules", "acceptance-criteria", "questions", "feedback", "plan"].forEach(
      function (type) {
        var el = body.querySelector(':scope > div[type="' + type + '"]');
        if (!el) {
          return;
        }
        // Nested BR/AC live inside use cases; only top-level extras become tabs.
        var nodes = [];
        takeSectionWithHeading(el, nodes);
        if (nodes.length) {
          extraTabs.push({
            id: type,
            label: SECTION_H2[type] || type,
            nodes: nodes,
          });
        }
      }
    );

    var tabs = [];
    if (defNodes.length) {
      tabs.push({ id: "definitions", label: "Definitions", nodes: defNodes });
    }
    if (ucNodes.length) {
      tabs.push({ id: "use-cases", label: "Use Cases", nodes: ucNodes });
    }
    tabs = tabs.concat(extraTabs);

    if (tabs.length < 2) {
      return null;
    }

    var anchor = doc.createComment("spectr-tabs");
    tabs[0].nodes[0].parentNode.insertBefore(anchor, tabs[0].nodes[0]);

    var tabsRoot = doc.createElement("div");
    tabsRoot.className = "spectr-tabs";

    var tablist = doc.createElement("div");
    tablist.className = "spectr-tablist";
    tablist.setAttribute("role", "tablist");
    tablist.setAttribute("aria-label", "Specification sections");

    var panels = doc.createElement("div");
    panels.className = "spectr-tab-panels";

    var hashTab = "";
    if (doc.defaultView && doc.defaultView.location) {
      var m = String(doc.defaultView.location.hash || "").match(
        /^#tab=([a-z0-9-]+)/i
      );
      if (m) {
        hashTab = m[1];
      }
    }
    var initial =
      tabs.find(function (t) {
        return t.id === hashTab;
      }) || tabs[0];

    tabs.forEach(function (tab) {
      var btn = doc.createElement("button");
      btn.type = "button";
      btn.className = "spectr-tab";
      btn.setAttribute("role", "tab");
      btn.setAttribute("id", "spectr-tab-" + tab.id);
      btn.setAttribute("aria-controls", "spectr-panel-" + tab.id);
      btn.setAttribute("data-tab", tab.id);
      btn.textContent = tab.label;
      tablist.appendChild(btn);

      var panel = doc.createElement("div");
      panel.className = "spectr-tab-panel";
      panel.setAttribute("role", "tabpanel");
      panel.id = "spectr-panel-" + tab.id;
      panel.setAttribute("aria-labelledby", "spectr-tab-" + tab.id);
      panel.setAttribute("data-tab", tab.id);
      tab.nodes.forEach(function (node) {
        // Tab label replaces the top-level "Definitions" heading.
        if (
          tab.id === "definitions" &&
          node.tagName === "H2" &&
          (node.id === "definitions" || node.textContent.trim() === "Definitions")
        ) {
          if (node.parentNode) {
            node.parentNode.removeChild(node);
          }
          return;
        }
        panel.appendChild(node);
      });
      panels.appendChild(panel);
    });

    tabsRoot.appendChild(tablist);
    tabsRoot.appendChild(panels);
    anchor.parentNode.insertBefore(tabsRoot, anchor);
    anchor.parentNode.removeChild(anchor);
    function activate(tabId, opts) {
      opts = opts || {};
      tabs.forEach(function (tab) {
        var selected = tab.id === tabId;
        var btn = tablist.querySelector('[data-tab="' + tab.id + '"]');
        var panel = panels.querySelector('[data-tab="' + tab.id + '"]');
        if (btn) {
          btn.setAttribute("aria-selected", selected ? "true" : "false");
          btn.tabIndex = selected ? 0 : -1;
          btn.classList.toggle("active", selected);
        }
        if (panel) {
          if (selected) {
            panel.removeAttribute("hidden");
          } else {
            panel.setAttribute("hidden", "hidden");
          }
        }
      });
      body.setAttribute("data-active-tab", tabId);
      if (opts.updateHash !== false && doc.defaultView && doc.defaultView.history) {
        doc.defaultView.history.replaceState(null, "", "#tab=" + tabId);
      }
      $(body).trigger("spectr:tabchange", [tabId]);
    }

    $(tablist)
      .on("click.spectrTabs", ".spectr-tab", function () {
        activate($(this).attr("data-tab"));
      })
      .on("keydown.spectrTabs", ".spectr-tab", function (e) {
        var keys = { ArrowLeft: -1, ArrowRight: 1, Home: "start", End: "end" };
        var action = keys[e.key];
        if (action == null) {
          return;
        }
        e.preventDefault();
        var buttons = Array.prototype.slice.call(
          tablist.querySelectorAll(".spectr-tab")
        );
        var idx = buttons.indexOf(e.currentTarget);
        var next = idx;
        if (action === "start") {
          next = 0;
        } else if (action === "end") {
          next = buttons.length - 1;
        } else {
          next = (idx + action + buttons.length) % buttons.length;
        }
        buttons[next].focus();
        activate(buttons[next].getAttribute("data-tab"));
      });

    activate(initial.id, { updateHash: !!hashTab });
    return {
      activate: activate,
      tabs: tabs,
    };
  }

  function visibleNavHeadings(doc) {
    var activeTab = doc.body.getAttribute("data-active-tab");
    var list = [];
    Array.prototype.forEach.call(
      doc.body.querySelectorAll("h1, h2, h3"),
      function (el) {
        if (el.closest && el.closest("#spectr-doc-nav")) {
          return;
        }
        var panel = el.closest ? el.closest(".spectr-tab-panel") : null;
        if (panel) {
          if (panel.hasAttribute("hidden")) {
            return;
          }
          if (
            activeTab &&
            panel.getAttribute("data-tab") &&
            panel.getAttribute("data-tab") !== activeTab
          ) {
            return;
          }
        }
        // Skip tablist chrome
        if (el.closest && el.closest(".spectr-tablist")) {
          return;
        }
        list.push(el);
      }
    );
    return list;
  }

  function headingNavLabel(el) {
    var clone = el.cloneNode(true);
    Array.prototype.forEach.call(
      clone.querySelectorAll(
        ".spectr-sid-badge, .spectr-term-tip-panel, [aria-hidden='true']"
      ),
      function (node) {
        if (node.parentNode) {
          node.parentNode.removeChild(node);
        }
      }
    );
    var text = (clone.textContent || "").replace(/\s+/g, " ").trim();
    // Drop any leftover leading entity ids (uc-…, br-…, ac-…, def-…).
    text = text.replace(
      /^(?:(?:uc|br|ac|def|ref|tsk|ph)-[a-z0-9]+(?:\s+)+)+/i,
      ""
    );
    return text.trim();
  }

  function buildNav(doc, $) {
    var $body = $(doc.body);
    var $win = $(doc.defaultView);

    var $nav = $("#spectr-doc-nav", doc);
    if (!$nav.length) {
      $nav = $(
        '<aside id="spectr-doc-nav" class="spectr-doc-nav" aria-label="On this page">' +
          '<div class="spectr-doc-nav-header">' +
          '<div class="spectr-doc-nav-title">On this page</div>' +
          "</div>" +
          '<div class="spectr-doc-nav-body"></div>' +
          "</aside>"
      );
      $body.prepend($nav);
    } else if (!$nav.find(".spectr-doc-nav-body").length) {
      $nav.append('<div class="spectr-doc-nav-body"></div>');
    }

    function rebuildList() {
      var $list = $('<nav class="spectr-doc-nav-list"></nav>');
      $nav.find(".spectr-doc-nav-list").remove();

      var headings = visibleNavHeadings(doc);
      headings.forEach(function (el) {
        var level = parseInt(el.tagName.slice(1), 10);
        var text = headingNavLabel(el);
        if (!text) {
          return;
        }
        if (!el.id) {
          el.id = uniqueId(text.slice(0, 32));
        }
        var $a = $("<a></a>")
          .attr("href", "#" + el.id)
          .addClass("spectr-nav-item spectr-nav-h" + level)
          .text(text.length > 72 ? text.slice(0, 69) + "…" : text);
        $list.append($a);
      });

      $nav.find(".spectr-doc-nav-body").append($list);

      function setActive() {
        var visible = visibleNavHeadings(doc);
        var top = $win.scrollTop() + 72;
        var current = visible[0];
        for (var i = 0; i < visible.length; i += 1) {
          if ($(visible[i]).offset().top <= top) {
            current = visible[i];
          }
        }
        var $links = $nav.find(".spectr-doc-nav-list a");
        $links.removeClass("active");
        if (current && current.id) {
          $links.filter('[href="#' + current.id + '"]').addClass("active");
        }
      }

      $nav
        .find(".spectr-doc-nav-list a")
        .off("click.spectrNav")
        .on("click.spectrNav", function (e) {
          e.preventDefault();
          var id = $(this).attr("href").slice(1);
          var $target = $("#" + id, doc);
          if ($target.length) {
            var panel = $target.closest(".spectr-tab-panel")[0];
            if (panel && panel.hasAttribute("hidden")) {
              var tabId = panel.getAttribute("data-tab");
              $(doc.body).trigger("spectr:activatetab", [tabId]);
            }
            $("html, body", doc).animate(
              { scrollTop: $target.offset().top - 56 },
              280
            );
            if (doc.defaultView.history && doc.defaultView.history.replaceState) {
              var activeTab = doc.body.getAttribute("data-active-tab");
              var hash = activeTab ? "#tab=" + activeTab : "#" + id;
              if (!activeTab) {
                hash = "#" + id;
              }
              doc.defaultView.history.replaceState(null, "", hash);
            }
          }
        });

      $win.off("scroll.spectrNav resize.spectrNav").on(
        "scroll.spectrNav resize.spectrNav",
        setActive
      );
      setActive();
    }

    rebuildList();
    $body.off("spectr:tabchange.spectrNav").on("spectr:tabchange.spectrNav", function () {
      rebuildList();
    });
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
    linkifyGlossaryTerms(doc);
    renderMermaidDiagrams(doc);
    var tabApi = buildTabs(doc, $);
    if (tabApi) {
      $(doc.body).on("spectr:activatetab", function (_e, tabId) {
        tabApi.activate(tabId);
      });
    }
    buildNav(doc, $);
  }

  global.spectrEnhanceView = spectrEnhanceView;
})(typeof window !== "undefined" ? window : this);
