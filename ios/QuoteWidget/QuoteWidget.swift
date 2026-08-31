import SwiftUI
import WidgetKit

private let appGroup = "group.uk.tomchan.LifeSystem"
private let cacheKey = "daily-quote"

struct QuoteEntry: TimelineEntry {
    let date: Date
    let text: String
    let author: String?
    let refreshAfter: Date
    let isPlaceholder: Bool
}

private struct CachedQuote: Codable {
    let text: String
    let author: String?
    let localDate: String
    let refreshAfter: Date
}

struct QuoteProvider: TimelineProvider {
    func placeholder(in context: Context) -> QuoteEntry {
        sample(placeholder: true)
    }

    func getSnapshot(in context: Context, completion: @escaping (QuoteEntry) -> Void) {
        completion(context.isPreview ? sample() : current())
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<QuoteEntry>) -> Void) {
        let entry = current()
        completion(Timeline(entries: [entry], policy: .after(entry.refreshAfter)))
    }

    private func current() -> QuoteEntry {
        guard let data = UserDefaults(suiteName: appGroup)?.data(forKey: cacheKey),
              let cached = try? JSONDecoder().decode(CachedQuote.self, from: data) else {
            return QuoteEntry(
                date: .now,
                text: "Open System to choose today’s quote.",
                author: nil,
                refreshAfter: Date().addingTimeInterval(60 * 30),
                isPlaceholder: false
            )
        }
        return QuoteEntry(
            date: .now,
            text: cached.text,
            author: cached.author,
            refreshAfter: cached.refreshAfter,
            isPlaceholder: false
        )
    }

    private func sample(placeholder: Bool = false) -> QuoteEntry {
        QuoteEntry(
            date: .now,
            text: "The work you do today becomes your strength tomorrow.",
            author: "The System",
            refreshAfter: Date().addingTimeInterval(60 * 60 * 12),
            isPlaceholder: placeholder
        )
    }
}

struct QuoteWidgetView: View {
    @Environment(\.widgetFamily) private var family
    let entry: QuoteEntry

    var body: some View {
        switch family {
        case .accessoryInline:
            Label(entry.text, systemImage: "diamond.fill")
        case .accessoryRectangular:
            VStack(alignment: .leading, spacing: 3) {
                HStack(spacing: 4) {
                    Image(systemName: "diamond.fill")
                    Text("SYSTEM").font(.caption2.bold()).tracking(1.5)
                }
                .widgetAccentable()
                Text(entry.text)
                    .font(.system(.caption, design: .rounded, weight: .semibold))
                    .lineLimit(3)
                    .minimumScaleFactor(0.72)
                if let author = entry.author {
                    Text("— \(author)")
                        .font(.caption2)
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
        case .systemMedium:
            VStack(alignment: .leading, spacing: 10) {
                HStack {
                    Label("SYSTEM", systemImage: "diamond.fill")
                        .font(.caption.bold())
                        .tracking(1.8)
                        .widgetAccentable()
                    Spacer()
                    Text("TODAY")
                        .font(.caption2.bold())
                        .foregroundStyle(.secondary)
                }
                Spacer(minLength: 0)
                Text(entry.text)
                    .font(.system(.title3, design: .rounded, weight: .bold))
                    .lineLimit(3)
                    .minimumScaleFactor(0.75)
                if let author = entry.author {
                    Text("— \(author)")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.secondary)
                        .lineLimit(1)
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
            .padding(2)
        default:
            VStack(spacing: 8) {
                Image(systemName: "diamond.fill").font(.title2).widgetAccentable()
                Text(entry.text)
                    .font(.system(.subheadline, design: .rounded, weight: .semibold))
                    .multilineTextAlignment(.center)
                    .lineLimit(5)
            }
            .padding(4)
        }
    }
}

struct DailyQuoteWidget: Widget {
    let kind = "DailyQuoteWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: QuoteProvider()) { entry in
            QuoteWidgetView(entry: entry)
                .containerBackground(for: .widget) { Color.black.opacity(0.18) }
                .widgetURL(URL(string: "lifesystem://quotes/today"))
        }
        .configurationDisplayName("Daily System Quote")
        .description("Keep today’s chosen quote on your Lock Screen.")
        .supportedFamilies([.accessoryInline, .accessoryRectangular])
    }
}

struct QuickActionsWidgetView: View {
    let actions: [(title: String, icon: String, path: String)] = [
        ("Home", "house.fill", "home"),
        ("Board", "checklist", "board"),
        ("Practice", "figure.run", "system"),
        ("Skills", "point.3.connected.trianglepath.dotted", "skills"),
    ]

    var body: some View {
        VStack(alignment: .leading, spacing: 7) {
            Label("QUICK ACTIONS", systemImage: "bolt.fill")
                .font(.system(size: 9, weight: .bold))
                .tracking(1)
                .widgetAccentable()

            HStack(spacing: 5) {
                ForEach(actions, id: \.path) { action in
                    Link(destination: URL(string: "lifesystem://\(action.path)")!) {
                        Image(systemName: action.icon)
                            .font(.system(size: 13, weight: .semibold))
                            .frame(maxWidth: .infinity, maxHeight: .infinity)
                            .background(.primary.opacity(0.12), in: RoundedRectangle(cornerRadius: 7))
                            .accessibilityLabel(action.title)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .leading)
    }
}

@main
struct QuickActionsWidget: Widget {
    let kind = "QuickActionsWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: QuoteProvider()) { _ in
            QuickActionsWidgetView()
                .containerBackground(for: .widget) { Color.black.opacity(0.18) }
        }
        .configurationDisplayName("System Quick Actions")
        .description("Open key areas of System from your Lock Screen.")
        .supportedFamilies([.accessoryRectangular])
    }
}

#Preview("Quick Actions", as: .accessoryRectangular) {
    QuickActionsWidget()
} timeline: {
    QuoteEntry(date: .now, text: "", author: nil, refreshAfter: .distantFuture, isPlaceholder: false)
}
