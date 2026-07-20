# BTR Freight Inc. — digital recruiting card

A business card you hold up on your phone. A driver points their camera at the QR on it and
the **official DOT driver application opens on their phone** — no app, no paper, no typing
a URL, no landing page in between.

- **Live page:** <https://jabay7.github.io/btr-freight/card/>
- **What the QR encodes:** <https://jabay7.github.io/btr-freight/apply.html>

## Files

| File | Purpose |
|------|---------|
| `index.html` | The card page. Self-contained — no build step, no JS, no external CSS. |
| `qr.png` | QR to the application, navy on white with the truck emblem in the middle. For screens. |
| `qr-print.png` | Plain black-and-white QR. For flyers, truck stop boards, a trailer decal, a real paper card. |
| `logo-mark.png` | The site logo (`assets/img/BTR-OFF.png`) inverted to white line art on transparent, 2x, so it reads on the navy card. |
| `emblem.png` | Just the circular truck emblem, square and white on transparent — QR badge, Wallet icon, share preview. |
| `btr-freight.vcf` | The contact file the "Save Our Contact" button hands over, with the emblem as the contact photo. |
| `btr-freight.pkpass` | The live Apple Wallet pass, signed by WalletWallet. Not built by `build.py` — see [`wallet/README.md`](wallet/README.md). |
| `wallet/` | Apple Wallet pass sources — the full `pass.json` bundle, a copy-paste recipe, a signing script. |
| `build.py` | Regenerates every image, both QR codes and the `.vcf`. |

Everything except `index.html`, `btr-freight.pkpass`, `build.py` and the READMEs is
**generated**. To change the
phone number, the QR target, or the artwork, edit `build.py` and `index.html`, then:

```bash
cd card && uv run build.py
```

`build.py` and `wallet/` are excluded from the published site in `_config.yml`, the same way
`tests/` is — they're sources, not pages.

## Deploying

The card lives in the website repo, so it ships with the site:

```bash
git add card _config.yml && git commit -m "Add digital recruiting card" && git push
```

GitHub Pages redeploys on its own within a minute or two.

## Why the QR goes to the application instead of to this page

Because the card *is* the page — the recruiter is already holding it. The driver is the one
scanning, and the only thing they need is the first question of the application, not another
menu to tap through. Every extra screen between a QR and a form is applicants lost.

The card page still carries everything else — call, text, email, save-contact, the PDF, and
the qualifications — for the person holding the phone, and for anyone you text the link to.

## Before printing anything

The codes were decoded after generation and read correctly down to **140px**. Two rules if
you restyle them:

- **Never invert them.** Light modules on a dark field looks sharp in brand colors and a
  fair number of scanners — including the iPhone camera in poor light — refuse to read it.
  Both codes are dark-on-light for that reason.
- **Decode them again before you print.** Especially after any change to the emblem badge
  in the middle.

If the site ever moves to `btrfreight.com`, **every printed code has to be reprinted** —
update `APPLY_URL` in `build.py`, rerun it, and reprint. That's the one real cost of pointing
a physical code at a URL, and the reason the QR uses the address that's live today.
