/* =================================================================
   BTR Freight Inc. — Site Scripts
   ================================================================= */
(function () {
  "use strict";

  /* ---------- Header: solid-on-scroll ---------- */
  const header = document.querySelector(".site-header");
  const isInteriorPage = header && header.classList.contains("solid");
  function onScroll() {
    if (!header || isInteriorPage) return;
    header.classList.toggle("scrolled", window.scrollY > 30);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- Mobile nav ---------- */
  const toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      const open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.querySelectorAll(".nav a").forEach(function (link) {
      link.addEventListener("click", function () {
        document.body.classList.remove("nav-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------- Scroll reveal ---------- */
  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealEls.length) {
    const io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---------- Animated stat counters ---------- */
  const counters = document.querySelectorAll("[data-count]");
  if ("IntersectionObserver" in window && counters.length) {
    const cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        const el = e.target;
        const target = parseFloat(el.dataset.count);
        const decimals = (el.dataset.decimals && parseInt(el.dataset.decimals, 10)) || 0;
        const dur = 1500, start = performance.now();
        function tick(now) {
          const p = Math.min((now - start) / dur, 1);
          const eased = 1 - Math.pow(1 - p, 3);
          el.textContent = (target * eased).toFixed(decimals);
          if (p < 1) requestAnimationFrame(tick);
          else el.textContent = target.toFixed(decimals);
        }
        requestAnimationFrame(tick);
        cio.unobserve(el);
      });
    }, { threshold: 0.5 });
    counters.forEach(function (c) { cio.observe(c); });
  }

  /* ---------- FAQ accordion ---------- */
  document.querySelectorAll(".faq-q").forEach(function (q) {
    q.addEventListener("click", function () {
      const item = q.closest(".faq-item");
      const answer = item.querySelector(".faq-a");
      const open = item.classList.toggle("open");
      q.setAttribute("aria-expanded", open ? "true" : "false");
      answer.style.maxHeight = open ? answer.scrollHeight + "px" : null;
    });
  });

  /* ---------- Footer year ---------- */
  const yearEl = document.getElementById("year");
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  /* ---------- Repeatable form blocks (online application) ----------
     A [data-add="key"] button clones the last [data-item] inside the
     matching [data-repeat="key"] container, clears its inputs, and
     renumbers the visible block headings.
  ------------------------------------------------------------------ */
  function renumber(container) {
    container.querySelectorAll("[data-item] .repeat-num").forEach(function (n, i) {
      n.textContent = i + 1;
    });
  }
  document.querySelectorAll("[data-add]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const key = btn.getAttribute("data-add");
      const container = document.querySelector('[data-repeat="' + key + '"]');
      if (!container) return;
      const items = container.querySelectorAll("[data-item]");
      const last = items[items.length - 1];
      const clone = last.cloneNode(true);
      clone.querySelectorAll("input, select, textarea").forEach(function (el) {
        if (el.type === "checkbox" || el.type === "radio") el.checked = false;
        else el.value = "";
      });
      // keep radio groups independent per cloned block
      const idx = items.length;
      clone.querySelectorAll("input[type=radio]").forEach(function (el) {
        if (el.name) el.name = el.name.replace(/(\s#\d+)?$/, " #" + (idx + 1));
      });
      container.appendChild(clone);
      renumber(container);
      const firstField = clone.querySelector("input, select, textarea");
      if (firstField) firstField.focus();
    });
  });
  // initial numbering
  document.querySelectorAll("[data-repeat]").forEach(renumber);

  /* ---------- Stamp today's date into [data-today] fields ---------- */
  const todayISO = new Date().toISOString().slice(0, 10);
  document.querySelectorAll("[data-today]").forEach(function (el) {
    if (!el.value) el.value = todayISO;
  });

  /* ---------- Forward-only date fields (pickup / start dates) ----------
     [data-min-today] prevents picking a date in the past. */
  document.querySelectorAll("[data-min-today]").forEach(function (el) {
    el.min = todayISO;
  });

  /* ---------- Floating UI: back-to-top + mobile call/quote bar ----------
     Injected here so every page that loads this script gets them without
     repeating markup. The phone number is read from the header link so
     there's a single source of truth. */
  (function floatingUI() {
    const phoneLink = document.querySelector(".header-phone");
    const tel = phoneLink ? phoneLink.getAttribute("href") : "tel:+12244775782";

    // Back-to-top
    const toTop = document.createElement("button");
    toTop.type = "button";
    toTop.className = "to-top";
    toTop.setAttribute("aria-label", "Back to top");
    toTop.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    toTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
    document.body.appendChild(toTop);
    window.addEventListener(
      "scroll",
      function () {
        toTop.classList.toggle("show", window.scrollY > 600);
      },
      { passive: true }
    );

    // Mobile sticky action bar (Call + Get a Quote)
    const bar = document.createElement("div");
    bar.className = "mobile-cta";
    bar.innerHTML =
      '<a href="' + tel + '" class="btn btn-dark">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z" stroke-linejoin="round"/></svg>Call</a>' +
      '<a href="contact.html#quote" class="btn btn-primary">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke-linejoin="round"/></svg>Get a Quote</a>';
    document.body.appendChild(bar);
    document.body.classList.add("has-mobile-cta");
  })();

  /* ---------- AJAX form handling (Formspree-compatible) ----------
     Each [data-form] submits via fetch when its action points to a
     configured endpoint. If the action still contains "REPLACE_", it
     short-circuits to a friendly "demo mode" message so nothing breaks
     before the owner wires up a real endpoint.
  ------------------------------------------------------------------ */
  document.querySelectorAll("form[data-form]").forEach(function (form) {
    const status = form.querySelector(".form-status");
    const submitBtn = form.querySelector("[type=submit]");

    function setStatus(type, msg) {
      if (!status) return;
      status.className = "form-status show " + type;
      status.textContent = msg;
    }

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }

      const action = form.getAttribute("action") || "";
      const demo = action.indexOf("REPLACE_") !== -1 || action === "" || action === "#";

      if (demo) {
        setStatus("ok",
          "✓ Thanks! Your details were captured. (Demo mode: connect a form endpoint or your Google Form to start receiving submissions — see README.)");
        form.reset();
        return;
      }

      const original = submitBtn ? submitBtn.textContent : "";
      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = "Sending…"; }

      fetch(action, {
        method: "POST",
        body: new FormData(form),
        headers: { Accept: "application/json" }
      })
        .then(function (res) {
          if (res.ok) {
            setStatus("ok", "✓ Thank you! Your information has been received. Our team will be in touch shortly.");
            form.reset();
          } else {
            setStatus("err", "Something went wrong. Please call us or email and we'll help right away.");
          }
        })
        .catch(function () {
          setStatus("err", "Network error. Please check your connection and try again, or contact us directly.");
        })
        .finally(function () {
          if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = original; }
        });
    });
  });

  /* ---------- Current year in copyright already handled above ---------- */
})();
