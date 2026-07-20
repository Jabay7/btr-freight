"""
BTR Freight website test suite.

Static checks validate the built HTML/assets locally; the `live` tests hit the
deployed GitHub Pages site (auto-skip if it's unreachable).

Run:   uv run --with pytest pytest -q
Skip live tests: uv run --with pytest pytest -q -m "not live"
"""
import json
import re
import urllib.request
import urllib.error
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "services.html", "about.html", "careers.html", "apply.html", "contact.html"]
LIVE_BASE = "https://jabay7.github.io/btr-freight/"
PDF = "assets/downloads/BTR-Freight-Driver-Application.pdf"


# --------------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------------- #
class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []        # href/src references
        self.h1 = 0
        self.title = ""
        self.metas = {}        # name|property -> content
        self.canonical = None
        self.has_nav = False
        self.has_footer = False
        self.ld = []           # parsed JSON-LD blocks (raw text)
        self.forms = 0
        self.data_forms = 0
        self.has_form_status = False
        self.required_names = set()
        self.all_input_names = set()
        self.data_add = []
        self.data_repeat = []
        self._in_title = False
        self._in_ld = False
        self._ld_buf = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "nav":
            self.has_nav = True
        elif tag == "footer":
            self.has_footer = True
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.metas[key] = a.get("content", "")
        elif tag == "link":
            if a.get("rel") == "canonical":
                self.canonical = a.get("href")
            if a.get("href"):
                self.links.append(a["href"])
        elif tag in ("script", "img") and a.get("src"):
            self.links.append(a["src"])
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld = True
            self._ld_buf = ""
        if tag == "form":
            self.forms += 1
            if "data-form" in a:
                self.data_forms += 1
        if tag in ("input", "select", "textarea"):
            name = a.get("name")
            if name:
                self.all_input_names.add(name)
                if "required" in a:
                    self.required_names.add(name)
        if "data-add" in a:
            self.data_add.append(a["data-add"])
        if "data-repeat" in a:
            self.data_repeat.append(a["data-repeat"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_ld:
            self._in_ld = False
            self.ld.append(self._ld_buf)

    def handle_data(self, data):
        if self._in_title:
            self.title += data.strip()
        if self._in_ld:
            self._ld_buf += data


def parse(page):
    p = Page()
    p.feed((ROOT / page).read_text(encoding="utf-8"))
    if 'class="form-status"' in (ROOT / page).read_text(encoding="utf-8"):
        p.has_form_status = True
    return p


def text(page):
    return (ROOT / page).read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Existence & structure
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("page", PAGES)
def test_page_exists(page):
    assert (ROOT / page).is_file(), f"{page} missing"


@pytest.mark.parametrize("page", PAGES)
def test_head_essentials(page):
    p = parse(page)
    assert p.title, f"{page}: empty <title>"
    assert "BTR Freight" in p.title, f"{page}: brand not in title"
    assert p.metas.get("description"), f"{page}: missing meta description"
    assert p.canonical, f"{page}: missing canonical link"
    assert "assets/css/styles.css" in p.links, f"{page}: stylesheet not linked"
    assert "assets/js/main.js" in p.links, f"{page}: main.js not linked"
    assert "assets/img/favicon.svg" in p.links, f"{page}: favicon not linked"


@pytest.mark.parametrize("page", PAGES)
def test_single_h1(page):
    assert parse(page).h1 == 1, f"{page}: expected exactly one <h1>"


@pytest.mark.parametrize("page", PAGES)
def test_nav_and_footer(page):
    p = parse(page)
    assert p.has_nav, f"{page}: no <nav>"
    assert p.has_footer, f"{page}: no <footer>"


@pytest.mark.parametrize("page", PAGES)
def test_lang_attribute(page):
    assert '<html lang="en">' in text(page), f"{page}: missing lang attribute"


@pytest.mark.parametrize("page", PAGES)
def test_canonical_points_to_self(page):
    c = parse(page).canonical
    expected = "/" if page == "index.html" else page
    assert c.rstrip("/").endswith(expected.rstrip("/")) or c.endswith("/"), \
        f"{page}: canonical {c} doesn't match page"


# --------------------------------------------------------------------------- #
# Links / assets resolve
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("page", PAGES)
def test_internal_links_resolve(page):
    p = parse(page)
    broken = []
    for href in p.links:
        if href.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
            continue
        target = href.split("#")[0].split("?")[0]
        if not target:
            continue
        if not (ROOT / target).exists():
            broken.append(href)
    assert not broken, f"{page}: unresolved local references: {broken}"


def test_pdf_present_and_substantial():
    pdf = ROOT / PDF
    assert pdf.is_file(), "driver application PDF missing"
    assert pdf.stat().st_size > 50_000, "PDF unexpectedly small"


@pytest.mark.parametrize("page", ["careers.html", "apply.html"])
def test_pdf_download_link(page):
    t = text(page)
    assert PDF in t, f"{page}: PDF not linked"
    # the PDF anchor should offer a download
    assert re.search(r'href="' + re.escape(PDF) + r'"[^>]*download', t) or \
           re.search(r'download[^>]*href="' + re.escape(PDF) + r'"', t), \
           f"{page}: PDF link missing download attribute"


# --------------------------------------------------------------------------- #
# Forms
# --------------------------------------------------------------------------- #
def test_forms_wired():
    for page in ("contact.html", "apply.html"):
        p = parse(page)
        assert p.data_forms >= 1, f"{page}: no data-form form"
        assert p.has_form_status, f"{page}: no .form-status element"
        assert 'action="' in text(page), f"{page}: form missing action"


def test_careers_uses_online_application():
    """Quick-apply was removed; careers routes drivers to the step-by-step
    online application (still offering the PDF)."""
    p = parse("careers.html")
    t = text("careers.html")
    assert "<form" not in t, "careers.html should no longer host a form (quick apply removed)"
    assert 'id="quick-form"' not in t, "stale quick-apply form remains"
    assert "apply.html" in p.links, "careers.html must link to the online application"


def test_full_application_completeness():
    p = parse("apply.html")
    t = text("apply.html")
    assert t.count('class="form-section"') >= 10, "apply.html should have 10 sections"
    assert "data-wizard" in t, "apply.html should be a step-by-step wizard"
    for needed in ("First Name", "Last Name", "CDL Number", "Signature", "SSN",
                   "Employer Name", "Employer From", "Employer To",
                   "10-Year History Certified"):
        assert needed in p.required_names, f"apply.html missing required '{needed}'"
    # enforce 3-year minimum verifiable CDL experience
    assert re.search(r'name="Years Experience"[^>]*min="3"', t), \
        "apply.html should require min 3 years of CDL experience"
    # certification & consent checkboxes
    assert "Certification" in p.all_input_names
    assert "Background Consent" in p.all_input_names
    assert "HOS Acknowledged" in p.all_input_names
    # repeatable sections wired correctly
    for key in ("address", "accident", "conviction", "employer"):
        assert key in p.data_repeat, f"apply.html missing data-repeat={key}"
        assert key in p.data_add, f"apply.html missing data-add={key}"


# --------------------------------------------------------------------------- #
# SEO files & structured data
# --------------------------------------------------------------------------- #
def test_robots_txt():
    r = (ROOT / "robots.txt").read_text(encoding="utf-8")
    assert "Sitemap:" in r and "sitemap.xml" in r


def test_sitemap_lists_all_pages():
    sm = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    import xml.etree.ElementTree as ET
    ET.fromstring(sm)  # must be well-formed
    for page in PAGES:
        frag = "/" if page == "index.html" else page
        assert frag in sm, f"sitemap missing {page}"


def test_404_exists():
    assert (ROOT / "404.html").is_file()


@pytest.mark.parametrize("page", PAGES)
def test_jsonld_valid(page):
    for block in parse(page).ld:
        json.loads(block)  # raises if invalid


def test_structured_data_types():
    home = " ".join(parse("index.html").ld)
    assert "MovingCompany" in home or "Organization" in home
    careers = " ".join(parse("careers.html").ld)
    assert "JobPosting" in careers, "careers missing JobPosting schema"
    assert "FAQPage" in careers, "careers missing FAQPage schema"


# --------------------------------------------------------------------------- #
# Content correctness (recent edits)
# --------------------------------------------------------------------------- #
def test_insurance_is_5m_not_1m():
    for page in ("index.html", "about.html"):
        t = text(page)
        assert "$5M" in t, f"{page}: $5M coverage missing"
        assert "$1M" not in t, f"{page}: stale $1M coverage present"


def test_on_time_stat_removed():
    for page in ("index.html", "about.html"):
        assert 'data-count="98"' not in text(page), f"{page}: 98% stat still present"


# --------------------------------------------------------------------------- #
# Live deployment (network) — auto-skip if unreachable
# --------------------------------------------------------------------------- #
def _fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "btr-tests"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""


@pytest.fixture(scope="session")
def live_ok():
    try:
        status, _ = _fetch(LIVE_BASE)
        return status == 200
    except (urllib.error.URLError, OSError):
        return False


@pytest.mark.live
@pytest.mark.parametrize("page", PAGES)
def test_live_pages_return_200(page, live_ok):
    if not live_ok:
        pytest.skip("live site unreachable")
    url = LIVE_BASE + ("" if page == "index.html" else page)
    status, _ = _fetch(url)
    assert status == 200, f"{url} returned {status}"


@pytest.mark.live
def test_live_serves_current_content(live_ok):
    if not live_ok:
        pytest.skip("live site unreachable")
    _, html = _fetch(LIVE_BASE)
    assert "$5M" in html, "live home not serving $5M coverage yet"
    assert "98%" not in html, "live home still shows 98% stat"


# --------------------------------------------------------------------------- #
# Digital recruiting card (card/)
# --------------------------------------------------------------------------- #
CARD = ROOT / "card"
APPLY_URL = LIVE_BASE + "apply.html"


def test_card_assets_present():
    """Everything index.html and the Wallet bundle reference is generated."""
    for f in ("index.html", "qr.png", "qr-print.png", "logo-mark.png",
              "emblem.png", "btr-freight.vcf", "build.py"):
        p = CARD / f
        assert p.exists() and p.stat().st_size > 500, f"card/{f} missing or stub"
    for f in ("icon.png", "icon@2x.png", "icon@3x.png",
              "logo.png", "logo@2x.png", "logo@3x.png", "pass.json"):
        assert (CARD / "wallet" / "BTRCard.pass" / f).exists(), f"wallet asset {f} missing"


def test_card_qr_targets_the_application_everywhere():
    """The whole point of the card: every code and copy sheet aims at apply.html.

    A printed QR can't be corrected after the fact, so a drifting URL here is
    the one defect in this folder that costs real money.
    """
    pass_json = (CARD / "wallet" / "BTRCard.pass" / "pass.json").read_text(encoding="utf-8")
    recipe = (CARD / "wallet" / "recipe.txt").read_text(encoding="utf-8")
    for name, src in (("wallet/BTRCard.pass/pass.json", pass_json), ("wallet/recipe.txt", recipe)):
        assert APPLY_URL in src, f"card/{name} does not point at {APPLY_URL}"

    # build.py composes the target from SITE_URL, so check what it resolves to
    # rather than looking for the literal.
    build = (CARD / "build.py").read_text(encoding="utf-8")
    site = re.search(r'^SITE_URL = "([^"]+)"', build, re.M).group(1)
    apply_expr = re.search(r'^APPLY_URL = SITE_URL \+ "([^"]+)"', build, re.M).group(1)
    assert site + apply_expr == APPLY_URL, "build.py builds a different QR target"

    barcode = json.loads(pass_json)["barcodes"][0]
    assert barcode["message"] == APPLY_URL
    assert barcode["format"] == "PKBarcodeFormatQR"


def test_card_page_links_resolve():
    html = (CARD / "index.html").read_text(encoding="utf-8")
    html = re.sub(r"(?s)<!--.*?-->", "", html)          # skip the parked Wallet link
    for ref in re.findall(r'(?:href|src)="([^"#]+)"', html):
        if ref.startswith(("http", "mailto:", "tel:", "sms:", "data:")):
            continue
        assert (CARD / ref).resolve().exists(), f"card/index.html -> {ref} is broken"


def test_card_generated_files_are_not_published():
    """Sources stay out of the Jekyll build; the page and its images ship."""
    cfg = (ROOT / "_config.yml").read_text(encoding="utf-8")
    for excluded in ("card/build.py", "card/README.md", "card/wallet"):
        assert excluded in cfg, f"_config.yml should exclude {excluded}"
    assert "card/index.html" not in cfg, "the card page itself must be published"


def test_card_is_noindex():
    """A hand-out card shouldn't compete with careers.html in search."""
    html = (CARD / "index.html").read_text(encoding="utf-8")
    assert 'name="robots" content="noindex' in html
