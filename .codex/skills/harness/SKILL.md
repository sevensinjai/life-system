---
name: harness
description: Build, launch, exercise, and visually verify Life System iOS features with Xcode, the iOS Simulator, backend checks, and screenshots. Use when implementing or testing UI or API-connected behavior under ios/; do not use for backend-only changes with no iOS impact.
---

# Harness

Test iOS work against the real project and simulator instead of treating a successful Swift compile as sufficient.

## Project facts

- Xcode project: `ios/LifeSystem.xcodeproj`
- Scheme and bundle ID: `LifeSystem`, `uk.tomchan.LifeSystem`
- Default simulator: `iPhone 17 Pro`
- Local API: `http://127.0.0.1:8000`
- The ignored `PROJECT_CONTEXT.md` contains local development credentials. Read it only when authenticated testing needs them; never print its password in tool output or commit it.
- The app uses Keychain token storage. Reinstalling the app may not clear the simulator Keychain; explicitly sign out in the UI when a clean authentication state matters.

## Choose the verification depth

Use the smallest level that establishes the feature works:

1. For model, formatting, or isolated view changes, compile and use a `#Preview` with deterministic fixture data.
2. For navigation or local UI behavior, build and run the app in Simulator.
3. For API-connected behavior, run the FastAPI service, verify `/health`, then exercise the feature in Simulator.
4. For repeatable interactions or regression coverage, add an XCTest or XCUITest target/test rather than relying only on manual taps.

## Build and run

Run the helper from the repository root:

```bash
.codex/skills/harness/scripts/ios_harness.sh all
```

It builds for the configured simulator, boots it if needed, installs the current product, launches the app, and writes a screenshot. Use `build`, `launch`, or `screenshot` instead of `all` for a narrower action. Override defaults with `IOS_SIMULATOR_NAME` or `IOS_SCREENSHOT_PATH`.

If an Xcode build fails, inspect the first compiler error rather than the final summary. Do not report success until `** BUILD SUCCEEDED **` appears.

## API-connected tests

Start the backend in a persistent terminal session:

```bash
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Before using the app, require this check to succeed:

```bash
curl -fsS http://127.0.0.1:8000/health
```

Use the local development account from `PROJECT_CONTEXT.md` when login is part of the scenario. Do not create new accounts on every run unless account creation itself is under test.

## SwiftUI previews

Add or update `#Preview` blocks for newly introduced screens and reusable components. Preview fixtures must not require the backend, mutate the database, or contain real credentials. Keep authenticated screens injectable enough to render with mock state; a preview that immediately starts a network request is not a stable visual test.

Open `ios/LifeSystem.xcodeproj`, select the Swift file containing the preview, then use Xcode Canvas. The Simulator screenshot is the acceptance artifact for full flows because it captures the built app and device layout; Canvas is the fast iteration tool.

## Interaction and evidence

`xcrun simctl` can boot, install, launch, terminate, reset permissions, and capture screenshots, but it is not a general tap/type automation API. Use XCUITest for repeatable interaction. Manual interaction is acceptable for a one-off smoke test, but state exactly what was exercised.

Capture evidence after the target state is visible. Store useful screenshots under `ios/Screenshots/` with a feature-specific name. Inspect the image for clipping, keyboard overlap, safe-area issues, unreadable contrast, incorrect loading/empty/error states, and stale data before reporting the result.

## Completion report

Report the simulator/device, build result, scenario exercised, API state if relevant, and screenshot path. Mention any portion that was compile-only, preview-only, or manually verified so the strength of the evidence is clear.
