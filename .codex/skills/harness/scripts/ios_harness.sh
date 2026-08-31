#!/usr/bin/env bash
set -euo pipefail

action="${1:-all}"
repo_root="$(git rev-parse --show-toplevel)"
ios_dir="$repo_root/ios"
project="$ios_dir/LifeSystem.xcodeproj"
simulator="${IOS_SIMULATOR_NAME:-iPhone 17 Pro}"
screenshot="${IOS_SCREENSHOT_PATH:-$ios_dir/Screenshots/harness.png}"
derived_data="${IOS_DERIVED_DATA_PATH:-$repo_root/.build/ios-derived-data}"
app="$derived_data/Build/Products/Debug-iphonesimulator/LifeSystem.app"

build() {
  xcodebuild \
    -project "$project" \
    -scheme LifeSystem \
    -destination "platform=iOS Simulator,name=$simulator" \
    -configuration Debug \
    -derivedDataPath "$derived_data" \
    CODE_SIGNING_ALLOWED=NO \
    build
}

boot() {
  xcrun simctl boot "$simulator" 2>/dev/null || true
  xcrun simctl bootstatus "$simulator" -b
}

launch() {
  boot
  if [[ ! -d "$app" ]]; then
    build
  fi
  xcrun simctl install "$simulator" "$app"
  xcrun simctl launch --terminate-running-process "$simulator" uk.tomchan.LifeSystem
}

capture() {
  boot
  mkdir -p "$(dirname "$screenshot")"
  xcrun simctl io "$simulator" screenshot "$screenshot"
  echo "Screenshot: $screenshot"
}

case "$action" in
  build) build ;;
  launch) launch ;;
  screenshot) capture ;;
  all) build; launch; sleep 2; capture ;;
  *) echo "Usage: $0 {build|launch|screenshot|all}" >&2; exit 2 ;;
esac
