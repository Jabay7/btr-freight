# Apple Wallet recruiting card — BTR Freight Inc.

A Wallet card showing **BTR FREIGHT INC · NOW HIRING · CDL-A · (224) 477-5782** with a
**QR code** on it. A driver points their phone camera at your screen and the DOT driver
application opens on *their* phone — no app, no paperwork, no typing a URL.

Apple requires every Wallet pass to be cryptographically signed, so you can't just
double-click a file into Wallet. It has to be built by a service that signs on your behalf
(free) or signed with your own Apple Developer certificate.

## The pass is built

**`../btr-freight.pkpass`** — live at
<https://jabay7.github.io/btr-freight/card/btr-freight.pkpass>. Open that on an iPhone and
tap **Add**. That link is also the one to text anyone who wants it: GitHub Pages serves
`.pkpass` as `application/vnd.apple.pkpass`, so iOS hands it straight to Wallet instead of
downloading a file. The card page links it too.

It was built through WalletWallet (below) and is signed by them, which means:

- The face carries the logo, **BTR FREIGHT INC**, **NOW HIRING · CDL-A / (224) 477-5782**,
  and the QR to `apply.html`.
- It's near-black (`rgb(24,24,27)`) rather than brand navy, has no back side, and lists
  **WalletWallet** as the organization — their free tool allows one field pair and six
  preset colors, none of them navy.

The richer design in `BTRCard.pass/pass.json` — five front fields, amber labels, a full
back with tappable links, why-drive-with-BTR, the qualifications and the hiring process —
is still there, unused, waiting for either Pass2U or your own certificate.

> **Privacy note.** WalletWallet's page says it "runs directly from your browser", and its
> *barcode scanner* does. Generating the pass does not: clicking Download POSTs the logo
> and every field to `v2-walletwallet-alen-ro-api.workers2000.workers.dev/api/pkpass`, and
> the page also loads PostHog and askanalytics telemetry. Nothing sensitive went over —
> the logo, phone number and apply URL are all already public on the website — but don't
> put anything private through it.

## Rebuilding it — WalletWallet (free, no account, ~3 min)

Best done **on your iPhone in Safari** so the finished pass drops straight into Wallet.

1. Save the logo: open
   `https://raw.githubusercontent.com/Jabay7/btr-freight/main/card/logo-mark.png`
   → long-press the image → **Add to Photos**.
2. Go to **<https://walletwallet.alen.ro/>**
3. Barcode format: **QR**. Barcode data (type it in):
   `https://jabay7.github.io/btr-freight/apply.html`
4. Fill in the fields — every label and value is in **`recipe.txt`**, ready to copy-paste.
   The essentials: title `BTR FREIGHT INC`, card color **black** (the closest preset to
   brand navy — their blue is a bright royal that fights the logo), logo = the image you
   saved.
5. Tap **Download Apple pass** → the Add-to-Wallet screen opens → **Add**.
6. Replace `../btr-freight.pkpass` with the new file and push.

## Richer alternative — Pass2U (free tier, needs the app/account)

More room for the full back-of-card text. Create a **Generic** pass and copy the front and
back fields out of `BTRCard.pass/pass.json`, navy `#0B1F3A` background, amber `#F5A623`
labels, QR barcode with the apply URL above, and upload `BTRCard.pass/logo@3x.png`.

## Pro — sign it yourself (no third-party branding, Apple Developer $99/yr)

`BTRCard.pass/` is a complete, correct pass bundle already — `build.py` validates it on
every run (required keys, one style key, unique field keys, required images, and that the
barcode still points at `apply.html`). The only things missing are your Apple identifiers
and a signature. Follow the header comments in `sign.sh`, set `passTypeIdentifier` and
`teamIdentifier` in `pass.json`, then:

```bash
bash sign.sh <your key password>     # -> BTRCard.pkpass
```

## Handing the card to a driver

- **Any phone, no app:** open the pass in Wallet and let them point their camera at the QR.
  Works on iPhone and Android, and it's the whole point of the card.
- **iPhone to iPhone:** open the pass → **•••** → **AirDrop** → tap their icon. (The
  tap-phones-together gesture is Apple's *NameDrop*, which only shares contact cards, not
  passes — so AirDrop is the right tool here.)
- **Anyone at all:** text them `https://jabay7.github.io/btr-freight/card/`.

## If you move to btrfreight.com

The pass keeps working — GitHub Pages 301-redirects the old `github.io` URL to a custom
domain, so the QR inside still lands on the application. You'd only rebuild if you want the
pass pointing at the new domain directly, and note that a signed pass is immutable: anyone
who already added the old one keeps it until they delete and re-add.

## Where the images come from

`BTRCard.pass/icon*.png` and `logo*.png` are generated from the site logo by `../build.py`
(`uv run build.py` from the `card` folder). Don't hand-edit them — regenerate instead.
