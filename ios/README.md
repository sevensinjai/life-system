# System for iOS

Native SwiftUI client for the existing FastAPI backend. It requires iOS 17 or later.

1. Start the API from the repository root: `.venv/bin/uvicorn app.main:app --reload`
2. Open `LifeSystem.xcodeproj` in Xcode.
3. Select an iPhone simulator and press Run.

The simulator reaches the Mac API at `http://127.0.0.1:8000`. For a physical device, change `SYSTEM_API_URL` in `LifeSystem/Info.plist` to the Mac's LAN address and ensure both devices are on the same network.

## Lock Screen quote widget

The `QuoteWidget` extension supports rectangular and inline Lock Screen widgets, plus a small Home Screen widget. After installing and opening the app at least once:

1. Touch and hold the Lock Screen and choose **Customize**.
2. Select the Lock Screen, then tap the widget area.
3. Find **System Quote** and add the desired layout.

The signed-in app fetches `/quotes/today`, stores the result in its App Group, and asks WidgetKit to reload. It refreshes on app entry and from **More → Refresh Lock Screen quote**. Xcode must configure the `group.uk.tomchan.LifeSystem` App Group for both the app and widget targets before running on a physical device.
