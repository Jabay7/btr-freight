# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "qrcode"]
# ///
"""Build every generated asset for the BTR Freight digital business card.

Run with:  uv run build.py     (from this folder)

Outputs (all regenerable, safe to delete):
  logo-mark.png              full logo, white line art on transparent, 2x
  emblem.png                 square truck emblem, white on transparent
  qr.png                     QR to the driver application, navy on white, emblem in the middle
  qr-print.png               plain black/white QR for signs, flyers and truck decals
  btr-freight.vcf            contact file with the emblem as the contact photo
  wallet/BTRCard.pass/*.png  Apple Wallet icon + logo, @1x/@2x/@3x
"""

import base64
import json
import io
import os

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_LOGO = os.path.join(HERE, "..", "assets", "img", "BTR-OFF.png")
PASS_DIR = os.path.join(HERE, "wallet", "BTRCard.pass")

SITE_URL = "https://jabay7.github.io/btr-freight/"
# The whole point of this card: the code goes straight to the DOT application,
# not to a landing page the driver then has to navigate.
APPLY_URL = SITE_URL + "apply.html"

NAVY = (11, 31, 58)      # --navy-800
PHONE = "+12244775782"
EMAIL = "onboarding@btrfreight.com"


def out(path):
    """Absolute path under card/, creating the parent directory if needed."""
    p = os.path.join(HERE, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


# --------------------------------------------------------------- artwork
# The source logo is black line art on a flat white field, so luminance *is*
# the coverage map: alpha = 255 - L keeps every antialiased edge pixel at
# exactly the right opacity, with none of the fringing a color-key or a
# threshold would leave behind. Recoloring is then just a flat fill.
def tint(gray, rgb):
    """Line art in `rgb` on transparent, built from a grayscale plate."""
    layer = Image.new("RGBA", gray.size, rgb + (0,))
    layer.putalpha(Image.eval(gray, lambda v: 255 - v))
    return layer


def ink_rows(gray):
    """Per-row ink counts, used to find where the logo's parts start and stop."""
    px = gray.load()
    return [sum(1 for x in range(gray.width) if px[x, y] < 200) for y in range(gray.height)]


def emblem_box(gray):
    """Bounding box of the circular truck emblem above the wordmark.

    The logo stacks emblem / BTR FREIGHT INC / SINCE 2020 with blank bands
    between them, so the emblem is everything before the first blank band that
    follows ink. Measuring it rather than hardcoding a crop means a re-exported
    logo at a different size still lands correctly.
    """
    rows = ink_rows(gray)
    top = next(y for y, c in enumerate(rows) if c)
    bottom = next(y for y in range(top, len(rows)) if rows[y] == 0) - 1

    px = gray.load()
    cols = [x for x in range(gray.width)
            if any(px[x, y] < 200 for y in range(top, bottom + 1))]
    return cols[0], top, cols[-1] + 1, bottom + 1


def square(layer, pad=0.06):
    """Center a layer on a transparent square canvas with breathing room."""
    side = int(max(layer.size) * (1 + pad * 2))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.alpha_composite(layer, ((side - layer.width) // 2, (side - layer.height) // 2))
    return canvas


print("· reading", os.path.basename(SOURCE_LOGO))
gray = Image.open(SOURCE_LOGO).convert("L")
box = emblem_box(gray)
emblem_gray = gray.crop(box)

def upscale(layer, size):
    """Enlarge line art without the mush a plain resample leaves behind.

    The source logo is only 253px wide and the card shows it at ~218px CSS, so
    on the 3x phone screen this page is actually opened on it has to be scaled
    up. LANCZOS alone reads soft — the truck's grille slats and the thin ring
    around it blur into each other — so the alpha channel gets an unsharp pass
    afterwards to pull those edges back. Sharpening alpha rather than color is
    what keeps it from ringing: the art is a flat fill, so all of its detail
    lives in the coverage mask and nowhere else.
    """
    r, g, b, a = layer.resize(size, Image.LANCZOS).split()
    a = a.filter(ImageFilter.UnsharpMask(radius=1.6, percent=110, threshold=2))
    return Image.merge("RGBA", (r, g, b, a))


print("· building logo-mark.png (white on transparent)")
white_logo = upscale(tint(gray, (255, 255, 255)), (gray.width * 2, gray.height * 2))
white_logo.save(out("logo-mark.png"), optimize=True)

print("· building emblem.png (white on transparent)")
white_emblem = upscale(square(tint(emblem_gray, (255, 255, 255))), (512, 512))
white_emblem.save(out("emblem.png"), optimize=True)

# The QR badge sits on the code's white field, so that copy has to be dark.
navy_emblem = upscale(square(tint(emblem_gray, NAVY)), (512, 512))


# ------------------------------------------------- apple wallet images
# icon: shown in notifications and on the lock screen (29pt square).
# logo: shown top-left on the pass face, capped at 160x50pt. Apple wants
#       @1x/@2x/@3x for both. The pass background is brand navy, so both use
#       the white art.
#
# Both are sized off their *height* and given whatever width the artwork's own
# aspect calls for — writing 160x50 literally would squash the wordmark to half
# its width, since Apple's numbers are a bounding box, not a target shape.
print("· building Apple Wallet image set")
os.makedirs(PASS_DIR, exist_ok=True)
for name, pt, art in (("icon", 29, white_emblem), ("logo", 50, white_logo)):
    for suffix, scale in (("", 1), ("@2x", 2), ("@3x", 3)):
        h = pt * scale
        w = round(art.width * h / art.height)
        assert w <= 160 * scale, f"{name}{suffix} is {w}px wide, past Apple's cap"
        art.resize((w, h), Image.LANCZOS) \
           .save(os.path.join(PASS_DIR, f"{name}{suffix}.png"), optimize=True)


# -------------------------------------------------- apple wallet bundle check
# Apple rejects a malformed pass at install time with no useful diagnostic, and
# by then it has already been signed — so the cheap checks happen here instead,
# before anyone spends a signing round-trip on it.
print("· checking the Wallet bundle")
with open(os.path.join(PASS_DIR, "pass.json"), encoding="utf-8") as f:
    pass_json = json.load(f)

REQUIRED_KEYS = {"description", "formatVersion", "organizationName",
                 "passTypeIdentifier", "serialNumber", "teamIdentifier"}
STYLES = ("boardingPass", "coupon", "eventTicket", "generic", "storeCard")

problems = []
missing = REQUIRED_KEYS - pass_json.keys()
if missing:
    problems.append(f"pass.json is missing required key(s): {sorted(missing)}")

styles = [k for k in STYLES if k in pass_json]
if len(styles) != 1:
    problems.append(f"pass.json needs exactly one style key, found {styles}")
else:
    # Field keys identify a field to Wallet; duplicates make it drop one silently.
    keys = [f["key"] for group in pass_json[styles[0]].values() for f in group]
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    if dupes:
        problems.append(f"duplicate field keys in pass.json: {dupes}")

# icon.png is the one image Apple actually requires — without it a pass that is
# otherwise perfect still refuses to install.
for required_img in ("icon.png", "icon@2x.png", "logo.png"):
    if not os.path.exists(os.path.join(PASS_DIR, required_img)):
        problems.append(f"missing pass image {required_img}")

for code in pass_json.get("barcodes", []):
    if code["message"] != APPLY_URL:
        problems.append(f"barcode points at {code['message']}, not {APPLY_URL}")

if problems:
    raise SystemExit("  pass bundle invalid:\n" + "\n".join("   ✗ " + p for p in problems))
print(f"  pass.json OK · {len(pass_json[styles[0]])} field groups · barcode -> apply.html")
if "REPLACE" in pass_json["passTypeIdentifier"] + pass_json["teamIdentifier"]:
    print("  note: Apple identifiers are still placeholders — see wallet/README.md")


# ------------------------------------------------------------------ QR
def make_qr(fill, back, path, badge=None):
    # Always dark-modules-on-light. A light-on-dark ("inverted") code looks
    # sharp in brand colors and a fair number of scanners — including the
    # iPhone camera in poor light — refuse to read it. This code's entire job
    # is being scanned off a phone screen, in a truck stop, by a stranger.
    qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_H, box_size=20, border=3)
    qr.add_data(APPLY_URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill, back_color=back).convert("RGBA")

    if badge is not None:
        # Highest error correction recovers ~30% of the code, so an emblem over
        # the middle fifth stays comfortably inside what a scanner can rebuild.
        side = img.size[0] // 5
        art = badge.resize((side, side), Image.LANCZOS)
        plate = Image.new("RGBA", (side + 24, side + 24), back + (255,))
        plate.alpha_composite(art, (12, 12))
        img.paste(plate, ((img.size[0] - plate.size[0]) // 2,) * 2, plate)
    img.save(path, optimize=True)
    print(f"  {os.path.basename(path)}  {img.size[0]}px")


print("· building QR codes ->", APPLY_URL)
make_qr(NAVY, (255, 255, 255), out("qr.png"), badge=navy_emblem)
make_qr("black", "white", out("qr-print.png"))


# --------------------------------------------------------------- vCard
def fold(line):
    """Wrap a vCard line at 75 octets; continuations start with one space.

    Measured in bytes and never split mid-character, both of which a plain
    character slice gets wrong: the em dashes in the note are three octets
    each, so slicing at 75 *characters* overruns the limit, and slicing a
    UTF-8 sequence in half corrupts it outright.
    """
    out, cur = [], ""
    for ch in line:
        if len((cur + ch).encode()) > 75:
            out.append(cur)
            cur = " " + ch          # the continuation's space counts too
        else:
            cur += ch
    out.append(cur)
    return "\r\n".join(out)


print("· building btr-freight.vcf")
# Contact photos get cropped to a circle by iOS, so the photo is the emblem —
# the wordmark would lose its ends. Navy on white rather than the white art,
# because a contact photo lands on whatever background the phone chooses.
buf = io.BytesIO()
photo_src = Image.new("RGB", navy_emblem.size, (255, 255, 255))
photo_src.paste(navy_emblem, (0, 0), navy_emblem)
photo_src.resize((300, 300), Image.LANCZOS).save(buf, format="JPEG", quality=86, optimize=True)
photo = base64.b64encode(buf.getvalue()).decode("ascii")

lines = [
    "BEGIN:VCARD",
    "VERSION:3.0",
    # Saved as a company, not a person: no recruiter's name goes stale, and iOS
    # files it under B for BTR instead of under an empty last name.
    "N:;;;;",
    "FN:BTR Freight Inc. — Driver Recruiting",
    "ORG:BTR Freight Inc.;Driver Recruiting",
    "X-ABShowAs:COMPANY",
    f"TEL;TYPE=WORK,VOICE:{PHONE}",
    f"EMAIL;TYPE=INTERNET,WORK:{EMAIL}",
    f"URL:{SITE_URL}",
    f"URL;TYPE=WORK:{APPLY_URL}",
    "ADR;TYPE=WORK:;Unit 208;4728 Oakton St;Skokie;IL;60076;USA",
    "NOTE:Now hiring experienced CDL-A drivers — competitive pay, steady miles, "
    "modern equipment and real home time. Apply online in about 15 minutes at "
    f"{APPLY_URL} — or call recruiting at (224) 477-5782. Equal Opportunity Employer.",
    "PHOTO;ENCODING=b;TYPE=JPEG:" + photo,
    "END:VCARD",
]
with open(out("btr-freight.vcf"), "w", encoding="utf-8", newline="") as f:
    f.write("\r\n".join(fold(l) for l in lines) + "\r\n")

print("\ndone.")
