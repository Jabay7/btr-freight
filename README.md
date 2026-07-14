# BTR Freight Inc. — Website

Official website for **BTR Freight Inc.**, a freight trucking & logistics company
serving the lower 48 — company info, services, driver recruitment, and the online
DOT driver employment application.

Static site: plain HTML, CSS, and vanilla JavaScript. No build step, no dependencies.

## Structure

| Path | Purpose |
|------|---------|
| `index.html` | Home |
| `services.html` | Freight services |
| `about.html` | Company & safety/compliance |
| `careers.html` | Driver recruitment |
| `apply.html` | Online DOT driver application (multi-step, e-signed) |
| `contact.html` | Contact + request a quote |
| `assets/` | CSS, JS, images, downloadable PDF application |
| `sitemap.xml`, `robots.txt`, `404.html` | SEO & error page |
| `tests/` | Automated checks (`pytest`) |

## Local preview

```
python -m http.server
```

Then open <http://localhost:8000>.

## Notes

- Form submissions are handled by a hosted form endpoint. The driver application
  collects sensitive personal data (SSN) — it must only ever be wired to a
  secure, privacy-compliant endpoint over HTTPS.
- Security: the site sets a Content-Security-Policy, referrer policy, a
  clickjacking guard, and form spam honeypots. HTTPS is enforced in hosting.
