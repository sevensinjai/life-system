import SwiftUI

struct DashboardSnapshot {
    let player: PlayerStatus
    let quests: [Quest]
    let quote: DailyQuote?
    let latestEvent: SystemEvent?
}

struct DashboardView: View {
    let openBoard: () -> Void
    let openSystem: () -> Void

    @State private var snapshot: DashboardSnapshot?
    @State private var errorMessage: String?
    @State private var hasReset = false

    var body: some View {
        NavigationStack {
            Group {
                if let snapshot {
                    DashboardContent(
                        snapshot: snapshot,
                        openBoard: openBoard,
                        openSystem: openSystem,
                        refresh: load
                    )
                } else if let errorMessage {
                    ContentUnavailableView(
                        "System unavailable",
                        systemImage: "wifi.exclamationmark",
                        description: Text(errorMessage)
                    )
                } else {
                    VStack(spacing: 14) {
                        ProgressView().tint(SystemTheme.cyan)
                        Text("Synchronising System…")
                            .font(.caption.monospaced())
                            .foregroundStyle(SystemTheme.muted)
                    }
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(SystemBackdrop())
            .toolbar(.hidden, for: .navigationBar)
            .task { await enterSystem() }
        }
    }

    private func enterSystem() async {
        if !hasReset {
            hasReset = true
            let _: DailyReset? = try? await LocalDataStore.shared.request(
                "/system/daily-reset",
                method: "POST"
            )
        }
        await load()
        await QuoteWidgetSync.refresh()
    }

    private func load() async {
        do {
            async let playerRequest: PlayerStatus = LocalDataStore.shared.request("/players/me")
            async let questRequest: [Quest] = LocalDataStore.shared.request("/quests/today")
            async let quoteRequest: DailyQuote? = try? LocalDataStore.shared.request("/quotes/today")
            async let eventRequest: [SystemEvent]? = try? LocalDataStore.shared.request("/system/events?limit=1")

            let player = try await playerRequest
            let quests = try await questRequest
            let quote = await quoteRequest
            let events = await eventRequest
            snapshot = DashboardSnapshot(
                player: player,
                quests: quests,
                quote: quote,
                latestEvent: events?.first
            )
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

private struct DashboardContent: View {
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    let snapshot: DashboardSnapshot
    let openBoard: () -> Void
    let openSystem: () -> Void
    let refresh: () async -> Void

    private var progress: Double {
        let instances = snapshot.quests.compactMap(\.currentInstance)
        let completed = instances.reduce(0) { $0 + min($1.progress, $1.targetCount) }
        let target = instances.reduce(0) { $0 + $1.targetCount }
        return target == 0 ? 0 : Double(completed) / Double(target)
    }

    private var usesAccessibilityLayout: Bool {
        dynamicTypeSize.isAccessibilitySize
    }

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                welcome
                levelCard
                quoteCard
                missionCard
                attributes
                transmission
            }
            .padding(.horizontal, 16)
            .padding(.top, 14)
            .padding(.bottom, 28)
        }
        .refreshable { await refresh() }
        .background(SystemBackdrop())
    }

    private var welcome: some View {
        let layout = usesAccessibilityLayout
            ? AnyLayout(VStackLayout(alignment: .leading, spacing: 12))
            : AnyLayout(HStackLayout(alignment: .top))

        return layout {
            VStack(alignment: .leading, spacing: 4) {
                Text(Date.now.formatted(.dateTime.weekday(.wide).month(.wide).day()))
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(SystemTheme.cyan)
                Text("Welcome back,")
                    .font(.system(.title3, design: .serif))
                    .foregroundStyle(SystemTheme.muted)
                Text(snapshot.player.name)
                    .font(.system(.largeTitle, design: .serif, weight: .semibold))
                    .foregroundStyle(SystemTheme.parchment)
            }
            if !usesAccessibilityLayout { Spacer() }
            Image(systemName: "flame.fill")
                .font(.title2)
                .foregroundStyle(SystemTheme.ember)
                .shadow(color: SystemTheme.ember.opacity(0.8), radius: 10)
                .padding(10)
                .background(Color.black.opacity(0.35))
                .overlay { Rectangle().stroke(SystemTheme.gold.opacity(0.3)) }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .dynamicTypeSize(...DynamicTypeSize.accessibility2)
    }

    private var levelCard: some View {
        NavigationLink { StatusView() } label: {
            SystemCard {
                VStack(spacing: 13) {
                    adaptiveRow(alignment: .leading) {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("PLAYER STATUS")
                                .font(.caption2.bold()).tracking(1.8)
                                .foregroundStyle(SystemTheme.cyan)
                                .dynamicTypeSize(...DynamicTypeSize.accessibility2)
                            Text("Level \(snapshot.player.level)")
                                .font(.system(.title2, design: .serif, weight: .semibold))
                                .foregroundStyle(SystemTheme.parchment)
                        }
                        if !usesAccessibilityLayout { Spacer() }
                        Text("\(Int(snapshot.player.expProgress * 100))%")
                            .font(.title3.bold().monospaced())
                    }
                    ProgressView(value: snapshot.player.expProgress)
                        .tint(SystemTheme.cyan)
                    adaptiveRow(alignment: .leading) {
                        Text("\(snapshot.player.exp) / \(snapshot.player.expToNextLevel) EXP")
                        if !usesAccessibilityLayout { Spacer() }
                        if snapshot.player.statPoints > 0 {
                            Label("\(snapshot.player.statPoints) points", systemImage: "sparkles")
                                .foregroundStyle(SystemTheme.gold)
                        } else {
                            Text("View status  ›")
                        }
                    }
                    .font(.caption.monospaced())
                    .foregroundStyle(SystemTheme.muted)
                }
            }
        }
        .buttonStyle(.plain)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Player status, level \(snapshot.player.level), \(snapshot.player.exp) of \(snapshot.player.expToNextLevel) experience, \(snapshot.player.statPoints) unspent stat points")
        .accessibilityHint("Opens Player State")
    }

    private var quoteCard: some View {
        SystemCard {
            VStack(alignment: .leading, spacing: 10) {
                Label("TODAY'S WORDS", systemImage: "quote.opening")
                    .font(.caption2.bold()).tracking(1.5)
                    .foregroundStyle(SystemTheme.cyan)
                    .dynamicTypeSize(...DynamicTypeSize.accessibility2)
                if let quote = snapshot.quote?.quote {
                    Text("“\(quote.text)”")
                        .font(.system(.title3, design: .serif, weight: .medium))
                        .foregroundStyle(SystemTheme.parchment)
                        .fixedSize(horizontal: false, vertical: true)
                    if let author = quote.author {
                        Text("— \(author)")
                            .font(.caption)
                            .foregroundStyle(SystemTheme.muted)
                    }
                } else {
                    Text("Add a quote to give the System something worth repeating.")
                        .font(.subheadline)
                        .foregroundStyle(SystemTheme.muted)
                }
                Label("Kept in your daily player record", systemImage: "book.closed")
                    .font(.caption2)
                    .foregroundStyle(SystemTheme.muted)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }

    private var missionCard: some View {
        Button(action: openBoard) {
            SystemCard {
                VStack(spacing: 13) {
                    adaptiveRow(alignment: .leading) {
                        VStack(alignment: .leading, spacing: 2) {
                            Text("TODAY'S MISSIONS")
                                .font(.caption2.bold()).tracking(1.5)
                                .foregroundStyle(SystemTheme.cyan)
                                .dynamicTypeSize(...DynamicTypeSize.accessibility2)
                            Text(snapshot.quests.isEmpty ? "Board clear" : "\(snapshot.quests.count) active")
                                .font(.title3.bold())
                        }
                        if !usesAccessibilityLayout { Spacer() }
                        Text("\(Int(progress * 100))%")
                            .font(.headline.monospaced())
                    }
                    ProgressView(value: progress).tint(SystemTheme.blue)
                    ForEach(snapshot.quests.prefix(3)) { quest in
                        let instance = quest.currentInstance
                        let unit = quest.unit ?? "items"
                        let questLayout = usesAccessibilityLayout
                            ? AnyLayout(VStackLayout(alignment: .leading, spacing: 8))
                            : AnyLayout(HStackLayout(spacing: 10))
                        questLayout {
                            Text(quest.difficulty)
                                .font(.caption.bold().monospaced())
                                .foregroundStyle(SystemTheme.cyan)
                                .frame(width: 26, height: 26)
                                .background(SystemTheme.surfaceRaised)
                                .overlay { Rectangle().stroke(SystemTheme.gold.opacity(0.25)) }
                            Text(quest.title)
                                .lineLimit(usesAccessibilityLayout ? nil : 1)
                            if !usesAccessibilityLayout { Spacer() }
                            if let instance {
                                Text("\(instance.progress)/\(instance.targetCount)")
                                    .font(.caption.monospaced())
                                    .foregroundStyle(SystemTheme.muted)
                            }
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .accessibilityElement(children: .ignore)
                        .accessibilityLabel("\(quest.title), \(quest.difficulty) rank, \(instance?.progress ?? 0) of \(instance?.targetCount ?? quest.targetCount) \(unit)")
                    }
                    Text("Open quest board  ›")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(SystemTheme.cyan)
                        .frame(maxWidth: .infinity, alignment: usesAccessibilityLayout ? .leading : .trailing)
                }
            }
        }
        .buttonStyle(.plain)
        .accessibilityHint("Opens today's quest board")
    }

    private var attributes: some View {
        VStack(alignment: .leading, spacing: 9) {
            Text("ATTRIBUTES")
                .font(.caption2.bold()).tracking(1.5)
                .foregroundStyle(SystemTheme.muted)
                .dynamicTypeSize(...DynamicTypeSize.accessibility2)
            if usesAccessibilityLayout {
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 9) {
                    ForEach(snapshot.player.stats.rows, id: \.0) { stat in
                        attributeCell(stat)
                    }
                }
            } else {
                HStack(spacing: 7) {
                    ForEach(snapshot.player.stats.rows, id: \.0) { stat in
                        attributeCell(stat)
                    }
                }
            }
        }
    }

    private func attributeCell(_ stat: (String, Int, String)) -> some View {
        VStack(spacing: 5) {
            Image(systemName: stat.2).font(.caption).foregroundStyle(SystemTheme.cyan)
            Text("\(stat.1)").font(.subheadline.bold().monospaced())
            Text(usesAccessibilityLayout ? stat.0 : String(stat.0.prefix(3)).uppercased())
                .font(usesAccessibilityLayout ? .caption.bold() : .system(size: 8, weight: .bold))
                .foregroundStyle(SystemTheme.muted)
        }
        .frame(maxWidth: .infinity, minHeight: 58)
        .padding(.vertical, 10)
        .background(SystemTheme.surface)
        .overlay { Rectangle().stroke(SystemTheme.gold.opacity(0.2)) }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(stat.0), \(stat.1)")
    }

    @ViewBuilder private var transmission: some View {
        if let event = snapshot.latestEvent {
            Button(action: openSystem) {
                let layout = usesAccessibilityLayout
                    ? AnyLayout(VStackLayout(alignment: .leading, spacing: 10))
                    : AnyLayout(HStackLayout(spacing: 12))
                layout {
                    Image(systemName: "wave.3.right").foregroundStyle(SystemTheme.cyan)
                    VStack(alignment: .leading, spacing: 3) {
                        Text("LATEST TRANSMISSION").font(.caption2.bold()).tracking(1.3).foregroundStyle(SystemTheme.cyan)
                            .dynamicTypeSize(...DynamicTypeSize.accessibility2)
                        Text(event.message)
                            .font(.subheadline)
                            .lineLimit(usesAccessibilityLayout ? nil : 2)
                    }
                    if !usesAccessibilityLayout { Spacer() }
                    Image(systemName: "chevron.right").font(.caption).foregroundStyle(SystemTheme.muted)
                }
                .padding(14)
                .background(SystemTheme.surface)
                .overlay { Rectangle().stroke(SystemTheme.gold.opacity(0.24)) }
            }
            .buttonStyle(.plain)
            .accessibilityHint("Opens activity history")
        }
    }

    private func adaptiveRow<Content: View>(
        alignment: HorizontalAlignment,
        @ViewBuilder content: () -> Content
    ) -> some View {
        let layout = usesAccessibilityLayout
            ? AnyLayout(VStackLayout(alignment: alignment, spacing: 8))
            : AnyLayout(HStackLayout(alignment: .center))
        return layout(content)
            .frame(maxWidth: .infinity, alignment: .leading)
    }
}

struct DashboardPreviewScreen: View {
    var body: some View {
        DashboardContent(
            snapshot: DashboardFixtures.snapshot,
            openBoard: {},
            openSystem: {},
            refresh: {}
        )
        .background(SystemBackdrop())
        .preferredColorScheme(.dark)
    }
}

private enum DashboardFixtures {
    static let snapshot = DashboardSnapshot(
        player: PlayerStatus(
            id: 1, name: "Shadow Developer", level: 7, exp: 340,
            expToNextLevel: 520, expProgress: 0.65, totalExpEarned: 2_410,
            statPoints: 3,
            stats: StatBlock(strength: 18, agility: 15, vitality: 17, intelligence: 14, perception: 16),
            timezone: "Europe/London"
        ),
        quests: [
            Quest(id: 1, title: "Morning strength training", description: nil, schedule: QuestSchedule(label: "Every day"), difficulty: "C", targetCount: 100, unit: "reps", practiceMinutes: 20, statReward: "strength", statRewardAmount: 1, isActive: true, currentInstance: QuestInstance(id: 1, progress: 40, targetCount: 100, status: "active", periodEnd: "Today"), nextDueDate: nil),
            Quest(id: 2, title: "Focused reading", description: nil, schedule: QuestSchedule(label: "Every day"), difficulty: "D", targetCount: 30, unit: "minutes", practiceMinutes: 30, statReward: nil, statRewardAmount: 0, isActive: true, currentInstance: QuestInstance(id: 2, progress: 20, targetCount: 30, status: "active", periodEnd: "Today"), nextDueDate: nil)
        ],
        quote: DailyQuote(localDate: "2026-08-31", quote: QuoteSummary(id: 1, text: "The work you do today becomes your strength tomorrow.", author: "The System"), poolSize: 8, refreshAfter: "2026-09-01T00:00:00Z"),
        latestEvent: SystemEvent(id: 1, eventType: "quest_completed", message: "You cleared yesterday's training and gained 20 EXP.", createdAt: "2026-08-31T08:00:00Z")
    )
}

#Preview("Dashboard") {
    DashboardPreviewScreen()
}

#Preview("Dashboard AX5") {
    DashboardPreviewScreen()
        .environment(\.dynamicTypeSize, .accessibility5)
}
