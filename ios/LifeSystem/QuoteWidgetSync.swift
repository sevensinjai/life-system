import Foundation
import WidgetKit

enum QuoteWidgetSync {
    static let widgetKind = "DailyQuoteWidget"
    private static let suite = "group.uk.tomchan.LifeSystem"
    private static let cacheKey = "daily-quote"

    struct Cache: Codable {
        let text: String
        let author: String?
        let localDate: String
        let refreshAfter: Date
    }

    @MainActor
    static func refresh() async {
        do {
            let response: DailyQuote = try await LocalDataStore.shared.request("/quotes/today")
            guard let quote = response.quote,
                  let refreshAfter = ISO8601DateFormatter().date(from: response.refreshAfter),
                  let defaults = UserDefaults(suiteName: suite),
                  let data = try? JSONEncoder().encode(
                    Cache(
                        text: quote.text,
                        author: quote.author,
                        localDate: response.localDate,
                        refreshAfter: refreshAfter
                    )
                  ) else { return }
            defaults.set(data, forKey: cacheKey)
            WidgetCenter.shared.reloadTimelines(ofKind: widgetKind)
        } catch {
            // Keep the last good quote. A future foreground or widget timeline
            // reload gets another chance without blanking the Lock Screen.
        }
    }

    static func clear() {
        UserDefaults(suiteName: suite)?.removeObject(forKey: cacheKey)
        WidgetCenter.shared.reloadTimelines(ofKind: widgetKind)
    }
}
