# BTR Freight Inc. — Website

A professional, modern, fully responsive marketing site for **BTR Freight Inc.**, a freight
trucking & logistics company. Built as a fast, self-contained static site (plain HTML, CSS, and
vanilla JS) — no build step, no dependencies, deploys anywhere.

## Pages

| File | Purpose |
|------|---------|
| `index.html` | Home — hero, services overview, why-us, stats, shipper/driver paths, testimonials |
| `services.html` | Detailed freight services, equipment & coverage, shipping process |
| `about.html` | Company story, mission/vision/values, safety & compliance |
| `careers.html` | **Driver recruitment** — benefits, requirements, hiring process; offers 3 ways to apply |
| `apply.html` | **Full online driver application** — the official DOT employment application as a fillable, e-signed web form |
| `contact.html` | Contact details + **request-a-quote** form |

Plus `robots.txt`, `sitemap.xml`, a branded `404.html`, JSON-LD structured data
(Organization + a **JobPosting** so the driver role can appear in Google for Jobs),
and a `tests/` suite.

```
assets/
  css/styles.css          Design system (navy + amber, responsive)
  js/main.js              Nav, scroll effects, counters, FAQ, AJAX form handling
  img/favicon.svg         Site icon
  downloads/
    BTR-Freight-Driver-Application.pdf   Official DOT driver application (downloadable)
```

## View it locally

Just open `index.html` in a browser. (For forms/fonts to behave exactly like production,
serve it: `python -m http.server` from this folder, then visit `http://localhost:8000`.)

---

## ✅ Before you go live — customize these placeholders

Search/replace across all `.html` files:

| Placeholder | Replace with |
|-------------|--------------|
| `(800) 555-0199` and `+18005550199` | Your real phone number |
| `dispatch@btrfreight.com`, `careers@btrfreight.com` | Your real email addresses |
| `1234 Logistics Pkwy, Suite 100 / Your City, ST 00000` | Your real address |
| `USDOT #0000000`, `MC #000000` | Your real USDOT and MC numbers |
| Stats (`10M+`, `98%`, `48`, etc.) | Your real numbers (in the `data-count` attributes) |
| Hero/section photos | Optional — see "Images" below |

> Tip: the testimonials on the home page are illustrative samples. Swap them for real
> customer/driver quotes when you have them.

---

## 📨 Making the forms actually send (2-minute setup)

Both the **driver quick-apply** (`careers.html`) and **request-a-quote** (`contact.html`) forms
work in friendly **demo mode** out of the box — they show a success message but don't send
anything until you connect an endpoint. Pick **one** option:

### Option A — Formspree (recommended, no server needed)
1. Create a free account at <https://formspree.io>, add a form, and copy its endpoint
   (looks like `https://formspree.io/f/abcwxyz`).
2. In `careers.html` and `contact.html`, replace `https://formspree.io/f/REPLACE_FORM_ID`
   with your real endpoint.
3. Submissions now email you automatically. (Basin and Netlify Forms work the same way.)

### Option B — Google Form (matches the "quick info" form you asked for)
See **`GOOGLE-FORM-SETUP.md`** for a copy-paste blueprint and two ways to wire it into the site.

### ⚠ Security — the full online application (`apply.html`)
The full application can collect sensitive data (date of birth, optional SSN). A basic
Formspree endpoint emails this in plaintext, which is **not ideal for SSNs**. Before
collecting sensitive data online, use a privacy-compliant pipeline — e.g. Formspree with
encryption, a dedicated DQF/onboarding provider (Tenstreet, DriverReach, Foley), or your own
HTTPS backend. The form already marks SSN optional and notes it's verified securely at hire.

## Run the tests

```bash
uv run --with pytest pytest -q              # full suite (incl. live site checks)
uv run --with pytest pytest -q -m "not live"   # static checks only (offline)
```
The `tests/` suite validates page structure, that every internal link/asset resolves, the PDF
download, form wiring, SEO files, valid JSON-LD, and that the deployed site serves current content.

---

## 🚀 Deploy (free, via GitHub Pages)

Same workflow as a typical static site:

```bash
cd C:/Users/Yousi/BTR
git add -A
git commit -m "Launch BTR Freight website"
# create a repo on github.com, then:
git remote add origin https://github.com/<you>/btr-freight.git
git branch -M main
git push -u origin main
```

In the GitHub repo: **Settings ▸ Pages ▸ Build and deployment ▸ Deploy from a branch ▸
`main` / `root`**. Your site goes live at `https://<you>.github.io/btr-freight/`.
You can later point a custom domain (e.g. `btrfreight.com`) at it under the same Pages settings.

---

## Images

Hero and section photos load from Unsplash CDN URLs. Each sits over a navy gradient, so the
layout still looks right even if an image is slow or blocked. To use your own photography,
replace the `https://images.unsplash.com/...` URLs in `index.html`, `services.html`,
`about.html`, and the `.path-*` / `.hero` rules in `assets/css/styles.css`.

## Notes

- Accessible: skip links, ARIA labels, keyboard-friendly nav & accordion, reduced-motion support.
- SEO: per-page titles, meta descriptions, Open Graph tags.
- No tracking or third-party scripts beyond Google Fonts and (optional) your chosen form service.
