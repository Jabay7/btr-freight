# Apple Wallet recruiting card — BTR Freight Inc.

A Wallet card that shows **BTR FREIGHT INC · NOW HIRING CDL-A DRIVERS · (224) 477-5782**
with a **QR code** on it. A driver points their phone camera at your screen and the DOT
driver application opens on *their* phone — no app, no paperwork, no typing a URL.

Apple requires every Wallet pass to be cryptographically signed, so you can't just
double-click a file into Wallet. It has to be built by a service that signs on your behalf
(free) or signed with your own Apple Developer certificate.

> **This pass is not built yet.** `BTRCard.pass/` is a complete, correct pass bundle — the
> images are generated and `pass.json` is filled in — but it has no signature, so there is
> no `.pkpass` in `../` to hand anyone. Pick one of the routes below to produce one. The
> card page and QR codes work today and need none of this.

## Route 1 — WalletWallet (free, no account, ~3 min)

Best done **on your iPhone in Safari** so the finished pass drops straight into Wallet.

1. Save the logo: open
   `https://raw.githubusercontent.com/Jabay7/btr-freight/main/card/logo-mark.png`
   → long-press the image → **Add to Photos**.
2. Go to **<https://walletwallet.alen.ro/>**
3. Barcode format: **QR**. Barcode data (type it in):
   `https://jabay7.github.io/btr-freight/apply.html`
4. Fill in the fields — every label and value is in **`recipe.txt`**, ready to copy-paste.
   The essentials: title `BTR FREIGHT INC`, card color `#0B1F3A`, logo = the image you saved.
5. Tap **Download Apple pass** → the Add-to-Wallet screen opens → **Add**.
6. Drop the resulting `.pkpass` into `card/` as `btr-freight.pkpass` and push, so you can
   text the link to anyone: `https://jabay7.github.io/btr-freight/card/btr-freight.pkpass`
   (GitHub Pages serves it as `application/vnd.apple.pkpass`, so iOS hands it to Wallet
   instead of downloading a file). Then uncomment the Wallet link in `../index.html`.

That tool allows one field pair and six preset colors, so the result is simpler than
`BTRCard.pass/pass.json` — near-black rather than brand navy, no back side, and it lists
WalletWallet as the organization.

## Route 2 — Pass2U (free tier, needs the app/account)

More room for the full back-of-card text. Create a **Generic** pass and copy the front and
back fields out of `BTRCard.pass/pass.json`, navy `#0B1F3A` background, amber `#F5A623`
labels, QR barcode with the apply URL above, and upload `BTRCard.pass/logo@3x.png`.

## Route 3 — sign it yourself (no third-party branding, Apple Developer $99/yr)

`BTRCard.pass/` is ready — the only things missing are your Apple identifiers and a
signature. Follow the header comments in `sign.sh`, set `passTypeIdentifier` and
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

## Where the images come from

`BTRCard.pass/icon*.png` and `logo*.png` are generated from the site logo by `../build.py`
(`uv run build.py` from the `card` folder). Don't hand-edit them — regenerate instead.
