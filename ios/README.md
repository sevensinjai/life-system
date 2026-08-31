# System for iOS

Native, offline-first SwiftUI app. It requires iOS 17 or later.

1. Open `LifeSystem.xcodeproj` in Xcode.
2. Select the LifeSystem target and configure the `iCloud.uk.tomchan.LifeSystem` CloudKit container for your Apple Developer team.
3. Select an iPhone simulator or device and press Run.

App data is written immediately to SwiftData on the device. When the user is signed into iCloud, SwiftData mirrors the private store through CloudKit. The app remains usable offline and falls back to local-only storage when iCloud is unavailable.

## Lock Screen quote widget

The `QuoteWidget` extension supports rectangular and inline Lock Screen widgets, plus a small Home Screen widget. After installing and opening the app at least once:

1. Touch and hold the Lock Screen and choose **Customize**.
2. Select the Lock Screen, then tap the widget area.
3. Find **System Quote** and add the desired layout.

The app copies today's locally stored quote into its App Group and asks WidgetKit to reload. It refreshes on app entry and from **More → Refresh Lock Screen quote**. Xcode must configure the `group.uk.tomchan.LifeSystem` App Group for both the app and widget targets before running on a physical device.
