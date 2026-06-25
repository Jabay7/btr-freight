# Driver Quick-Apply — Google Form blueprint

You asked for a Google Form to gather quick info from drivers who want to apply.
A Google Form has to be created inside **your own Google account**, so it can't be generated
from here — but everything is set up so this takes about **2 minutes**. The website already has
a matching built-in quick-apply form working right now; use this if you'd rather collect
responses straight into Google Sheets.

---

## 1. Create the form

1. Go to <https://forms.google.com> → **Blank form**.
2. **Title:** `BTR Freight Inc. — Driver Quick Application`
3. **Description:**
   > Thanks for your interest in driving with BTR Freight! This short pre-qualification takes
   > about 2 minutes. A recruiter will follow up, and a full DOT driver application will be
   > required before hire. Please do not enter your full Social Security number here.

## 2. Add these questions

Click **+** for each. Mark the ones noted as **Required** (toggle at bottom of each question).

| # | Question | Type | Options / notes |
|---|----------|------|-----------------|
| 1 | First name | Short answer | **Required** |
| 2 | Last name | Short answer | **Required** |
| 3 | Email | Short answer | **Required** · turn on Response validation ▸ Text ▸ Email |
| 4 | Phone | Short answer | **Required** |
| 5 | City | Short answer | |
| 6 | State | Short answer | |
| 7 | Position you're interested in | Multiple choice | Company Driver · Owner-Operator · Lease Purchase · Team Driver — **Required** |
| 8 | CDL class | Dropdown | Class A · Class B · Class C · No CDL yet — **Required** |
| 9 | Years of CDL experience | Dropdown | Less than 1 year · 1–2 years · 2–5 years · 5–10 years · 10+ years — **Required** |
| 10 | Equipment experience | Checkboxes | Dry Van · Reefer · Flatbed · Tanker · Step Deck |
| 11 | Endorsements | Short answer | e.g. HAZMAT, Tanker, Doubles |
| 12 | Earliest start date | Date | |
| 13 | Do you currently hold a valid CDL? | Multiple choice | Yes · No — **Required** |
| 14 | Any DOT-reportable accidents in the last 3 years? | Multiple choice | No · Yes |
| 15 | How did you hear about us? | Short answer | |
| 16 | Anything else we should know? | Paragraph | |
| 17 | Consent | Checkboxes | "I consent to BTR Freight Inc. contacting me about driving opportunities." — **Required** |

## 3. Collect responses & get notified

- Top of editor ▸ **Responses** tab ▸ green **Sheets** icon → links responses to a Google Sheet.
- **Responses** tab ▸ ⋮ (three dots) ▸ **Get email notifications for new responses**.
- (Optional) Settings ▸ **Collect email addresses** for an automatic record of each applicant.

---

## 4. Wire it into the website (pick one)

After creating the form, click **Send** (top right).

### A) Link the existing buttons to your form (simplest)
1. **Send ▸ link icon (🔗) ▸ Copy.**
2. In `careers.html`, point the apply buttons at that link. For example, change:
   ```html
   <a href="#quick-form" class="btn btn-primary">Start quick application</a>
   ```
   to:
   ```html
   <a href="PASTE_YOUR_GOOGLE_FORM_LINK" class="btn btn-primary" target="_blank" rel="noopener">Start quick application</a>
   ```
   Do the same for the two **"Quick Apply Online"** buttons (in the page hero and the
   "Two easy ways to apply" card). You can then delete the built-in `<form>…</form>` block
   if you only want the Google Form.

### B) Embed the form directly in the page
1. **Send ▸ < > (Embed HTML) ▸ Copy** — you'll get an `<iframe …></iframe>`.
2. In `careers.html`, replace the entire `<form action="https://formspree.io/...">…</form>`
   block (inside `<div class="form-card" id="quick-form">`) with that iframe. Add
   `style="width:100%;border:0;min-height:1200px"` to the iframe so it fits nicely.

That's it — responses flow into your Google Form/Sheet, and you get notified on each new applicant.
