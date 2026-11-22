#!/usr/bin/env bash
# Downloads the Sauce Labs "Swag Labs" demo app builds used as the app under test.
set -euo pipefail

VERSION="2.7.1"
BASE="https://github.com/saucelabs/sample-app-mobile/releases/download/${VERSION}"
DEST="$(cd "$(dirname "$0")/.." && pwd)/apps"
mkdir -p "$DEST"

echo "Downloading Android APK..."
curl -fL -o "$DEST/Android.SauceLabs.Mobile.Sample.app.${VERSION}.apk" \
  "$BASE/Android.SauceLabs.Mobile.Sample.app.${VERSION}.apk"

if [[ "$(uname)" == "Darwin" ]]; then
  echo "Downloading iOS simulator build..."
  curl -fL -o "$DEST/iOS.Simulator.SauceLabs.Mobile.Sample.app.${VERSION}.zip" \
    "$BASE/iOS.Simulator.SauceLabs.Mobile.Sample.app.${VERSION}.zip"
  (cd "$DEST" && unzip -oq "iOS.Simulator.SauceLabs.Mobile.Sample.app.${VERSION}.zip")
fi

echo "Done. Files in $DEST:"
ls -1 "$DEST"
