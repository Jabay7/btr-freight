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
