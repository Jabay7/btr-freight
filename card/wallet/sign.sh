#!/usr/bin/env bash
# Build a signed BTRCard.pkpass from BTRCard.pass/
#
# You only need this if you want a pass with no third-party branding on it.
# The free route (WalletWallet / Pass2U) is in README.md and needs none of this.
#
# One-time setup:
#   1. Apple Developer Program membership ($99/yr).
#   2. Create a "Pass Type ID" (e.g. pass.com.btrfreight.card) and a Pass Type ID
#      certificate in the Apple Developer portal. Export it from Keychain as pass.p12.
#   3. Download Apple's "Worldwide Developer Relations" (WWDR) intermediate cert (G4).
#   4. Put pass.p12 and the WWDR cert next to this script, then convert to PEM:
#        openssl pkcs12 -in pass.p12 -clcerts -nokeys -out passcert.pem -passin pass:YOURP12PASS
#        openssl pkcs12 -in pass.p12 -nocerts   -out passkey.pem  -passin pass:YOURP12PASS -passout pass:YOURKEYPASS
#        openssl x509 -inform DER -in AppleWWDRCAG4.cer -out wwdr.pem   # skip if already PEM
#   5. Edit pass.json: set passTypeIdentifier and teamIdentifier to YOUR values.
#
# Then run:  bash sign.sh YOURKEYPASS
set -euo pipefail
KEYPASS="${1:?Usage: bash sign.sh <passkey.pem password>}"
DIR="BTRCard.pass"
OUT="BTRCard.pkpass"

cd "$(dirname "$0")"
rm -f "$DIR/manifest.json" "$DIR/signature" "$OUT"

# 1) manifest.json = { filename: sha1, ... } for every file in the pass bundle
python - "$DIR" <<'PY'
import hashlib, json, os, sys
d = sys.argv[1]
m = {}
for f in sorted(os.listdir(d)):
    p = os.path.join(d, f)
    if os.path.isfile(p) and f not in ("manifest.json", "signature"):
        m[f] = hashlib.sha1(open(p, "rb").read()).hexdigest()
json.dump(m, open(os.path.join(d, "manifest.json"), "w"))
print("manifest:", ", ".join(m))
PY

# 2) detached PKCS#7 signature of manifest.json
openssl smime -binary -sign \
  -certfile wwdr.pem \
  -signer passcert.pem \
  -inkey passkey.pem \
  -in "$DIR/manifest.json" \
  -out "$DIR/signature" \
  -outform DER -passin "pass:$KEYPASS"

# 3) zip the bundle contents (not the folder) into the .pkpass
( cd "$DIR" && zip -r -X "../$OUT" . -x '.*' )
echo "Built $OUT"
