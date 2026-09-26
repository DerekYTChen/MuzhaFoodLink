(function () {
  var DICT = window.MFL_I18N, VIDEOS = window.MFL_VIDEOS;
  var STORE = "mfl-lang";

  /* ---------- videos + QR cards ---------- */
  function buildVideos() {
    var grid = document.getElementById("qr-grid");
    if (!grid) return;
    grid.innerHTML = VIDEOS.map(function (v, i) {
      var url = "https://youtu.be/" + v.id;
      return '<article class="qr-card">' +
        '<a class="qr-code" href="' + url + '" target="_blank" rel="noopener">' +
        '<img src="qr/' + v.id + '.svg" width="132" height="132" alt="QR code linking to ' + v.ch + ' on YouTube" loading="lazy" />' +
        "</a>" +
        '<div class="qr-meta">' +
        '<span class="qr-num">' + String(i + 1).padStart(2, "0") + "</span>" +
        '<h3 data-vid-title="' + v.id + '"></h3>' +
        '<p class="qr-channel">' + v.ch + "</p>" +
        '<a class="text-link" href="' + url + '" target="_blank" rel="noopener"><span data-i18n="watch.open"></span> <span aria-hidden="true">↗</span></a>' +
        "</div></article>";
    }).join("");
  }

  /* ---------- i18n ---------- */
  function apply(lang) {
    var d = DICT[lang] || DICT.en;
    document.documentElement.lang = lang === "zh" ? "zh-Hant-TW" : "en";
    document.body.classList.toggle("lang-zh", lang === "zh");
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var k = el.getAttribute("data-i18n");
      if (k in d) el.innerHTML = d[k];
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
      var k = el.getAttribute("data-i18n-placeholder");
      if (k in d) el.setAttribute("placeholder", d[k]);
    });
    document.querySelectorAll("[data-i18n-title]").forEach(function (el) {
      var k = el.getAttribute("data-i18n-title");
      if (k in d) el.setAttribute("title", d[k].replace(/<[^>]+>/g, ""));
    });
    document.querySelectorAll("[data-i18n-alt]").forEach(function (el) {
      var k = el.getAttribute("data-i18n-alt");
      if (k in d) el.setAttribute("alt", d[k].replace(/<[^>]+>/g, ""));
    });
    document.querySelectorAll("[data-i18n-aria-label]").forEach(function (el) {
      var k = el.getAttribute("data-i18n-aria-label");
      if (k in d) el.setAttribute("aria-label", d[k]);
    });
    document.querySelectorAll("[data-vid-title]").forEach(function (el) {
      var v = VIDEOS.filter(function (x) { return x.id === el.getAttribute("data-vid-title"); })[0];
      if (v) el.textContent = lang === "zh" ? v.zh : v.en;
    });
    document.querySelectorAll(".lang-switch button").forEach(function (b) {
      var on = b.getAttribute("data-lang") === lang;
      b.classList.toggle("is-on", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
    syncAudioLabel();
    try { localStorage.setItem(STORE, lang); } catch (e) {}
  }

  function initialLang() {
    var saved = null;
    try { saved = localStorage.getItem(STORE); } catch (e) {}
    if (saved === "en" || saved === "zh") return saved;
    var n = (navigator.language || "en").toLowerCase();
    return /^zh/.test(n) ? "zh" : "en";
  }

  /* ---------- map <-> list linking ---------- */
  function linkMap() {
    var pins = document.querySelectorAll(".m-pin");
    var items = document.querySelectorAll(".stop-list li");
    function set(n, on) {
      pins.forEach(function (p) { if (p.getAttribute("data-stop") === n) p.classList.toggle("is-active", on); });
      items.forEach(function (li) { if (li.getAttribute("data-stop") === n) li.classList.toggle("is-active", on); });
    }
    function wire(el) {
      var n = el.getAttribute("data-stop");
      el.addEventListener("mouseenter", function () { set(n, true); });
      el.addEventListener("mouseleave", function () { set(n, false); });
      el.addEventListener("focus", function () { set(n, true); });
      el.addEventListener("blur", function () { set(n, false); });
    }
    pins.forEach(wire);
    items.forEach(function (li) { li.setAttribute("tabindex", "0"); wire(li); });
  }

  /* ---------- background score ---------- */
  var AKEY = "mfl-audio";
  function syncAudioLabel() {
    var btn = document.getElementById("audio-toggle");
    if (!btn || !window.MFL_AMBIENT) return;
    var lang = document.body.classList.contains("lang-zh") ? "zh" : "en";
    var d = DICT[lang] || DICT.en;
    var on = window.MFL_AMBIENT.isPlaying();
    btn.setAttribute("aria-pressed", on ? "true" : "false");
    var t = btn.querySelector(".audio-text");
    if (t) t.textContent = on ? d["audio.on"] : d["audio.off"];
  }
  function audio() {
    var btn = document.getElementById("audio-toggle");
    if (!btn) return;
    if (!window.MFL_AMBIENT || !(window.AudioContext || window.webkitAudioContext)) {
      btn.hidden = true;
      return;
    }
    btn.addEventListener("click", function () {
      window.MFL_AMBIENT.toggle();
      syncAudioLabel();
      try { localStorage.setItem(AKEY, window.MFL_AMBIENT.isPlaying() ? "on" : "off"); } catch (e) {}
    });
    /* a returning visitor who left it on gets it back, but only after a real
       gesture, because browsers block audio that starts without one */
    var want = null;
    try { want = localStorage.getItem(AKEY); } catch (e) {}
    if (want === "on") {
      var resume = function () {
        document.removeEventListener("pointerdown", resume);
        document.removeEventListener("keydown", resume);
        window.MFL_AMBIENT.start();
        syncAudioLabel();
      };
      document.addEventListener("pointerdown", resume, { once: true });
      document.addEventListener("keydown", resume, { once: true });
    }
    syncAudioLabel();
  }


  /* ---------- contact form (no database: composes an email) ---------- */
  var MAIL_TO = "derekyt.chen@gmail.com";
  function pikmin() {
    var btn = document.getElementById("pk-toggle");
    var cav = document.getElementById("pk-caveat");
    var svg = document.querySelector(".food-map");
    if (!btn || !svg) return;
    var on = localStorage.getItem("mfl-pikmin") === "on";
    function sync() {
      svg.classList.toggle("show-pk", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
      if (cav) cav.hidden = !on;
    }
    btn.addEventListener("click", function () {
      on = !on;
      try { localStorage.setItem("mfl-pikmin", on ? "on" : "off"); } catch (e) {}
      sync();
    });
    sync();
  }

  function petition() {
    var form = document.getElementById("petition-form");
    var ok = document.getElementById("success");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var name = (form.elements.name && form.elements.name.value || "").trim();
      var conn = form.elements.connection;
      var connLabel = conn && conn.options[conn.selectedIndex] ? conn.options[conn.selectedIndex].text : "";
      var email = (form.elements.email && form.elements.email.value || "").trim();
      var zh = document.body.classList.contains("lang-zh");
      var body = zh
        ? ["我想支持木柵食旅連線這個試辦計畫。", "", "姓名：" + name, "身分：" + connLabel, "聯絡信箱：" + email, "", "（此信由 Muzha Food Link 提案頁面自動草擬）"].join("\n")
        : ["I would like to support the Muzha Food Link pilot.", "", "Name: " + name, "Connection: " + connLabel, "Email: " + email, "", "(Drafted from the Muzha Food Link proposal page.)"].join("\n");
      var href = "mailto:" + MAIL_TO +
        "?subject=" + encodeURIComponent((zh ? "木柵食旅連線 支持登記：" : "Muzha Food Link support: ") + (name || "?")) +
        "&body=" + encodeURIComponent(body);
      window.location.href = href;
      if (ok) ok.hidden = false;
    });
  }

  /* ---------- active nav ---------- */
  function activeNav() {
    var links = Array.prototype.slice.call(document.querySelectorAll(".site-header nav a"));
    var secs = links.map(function (a) { return document.querySelector(a.getAttribute("href")); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var i = secs.indexOf(en.target);
        links.forEach(function (a, j) { a.classList.toggle("active", i === j); });
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    secs.forEach(function (s) { if (s) io.observe(s); });
  }

  buildVideos();
  apply(initialLang());
  document.querySelectorAll(".lang-switch button").forEach(function (b) {
    b.addEventListener("click", function () { apply(b.getAttribute("data-lang")); });
  });
  linkMap();
  audio();
  pikmin();
  petition();
  if ("IntersectionObserver" in window) activeNav();
})();
