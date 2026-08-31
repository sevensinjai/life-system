import SwiftUI

struct BoardView: View {
    private struct RewardReceipt: Identifiable {
        let id = UUID()
        let title: String
        let exp: Int
        let leveledUp: Bool
    }

    @State private var quests: [Quest] = []
    @State private var errorMessage: String?
    @State private var busyID: Int?
    @State private var showingCreate = false
    @State private var rewardReceipt: RewardReceipt?

    var body: some View {
        NavigationStack {
            ScrollView {
                LazyVStack(spacing: 14) {
                    HStack(alignment: .bottom) {
                        SystemHeader(title: "Quest Board", eyebrow: "Active missions")
                        Button { showingCreate = true } label: {
                            Image(systemName: "plus")
                                .font(.headline.bold())
                                .frame(width: 42, height: 42)
                                .background(SystemTheme.cyan)
                                .foregroundStyle(SystemTheme.background)
                                .overlay { Rectangle().stroke(SystemTheme.gold.opacity(0.4)) }
                        }
                        .accessibilityLabel("Create quest")
                    }
                    if quests.isEmpty && errorMessage == nil {
                        ContentUnavailableView {
                            Label("No missions open", systemImage: "checkmark.seal")
                        } description: {
                            Text("Create a quest or return when the next routine opens.")
                        } actions: {
                            Button("Create a quest") { showingCreate = true }
                                .buttonStyle(.borderedProminent)
                        }
                    }
                    ForEach(quests) { quest in
                        QuestCard(quest: quest, busy: busyID == quest.id) { action in Task { await perform(action, quest: quest) } }
                    }
                    if let errorMessage { Text(errorMessage).foregroundStyle(.red).font(.footnote) }
                }.padding()
            }.background(SystemBackdrop()).toolbar(.hidden, for: .navigationBar)
             .task { await load() }.refreshable { await load() }
             .sheet(isPresented: $showingCreate) {
                 CreateQuestView { _ in Task { await load() } }
             }
             .sheet(item: $rewardReceipt) { receipt in
                 QuestRewardView(title: receipt.title, exp: receipt.exp, leveledUp: receipt.leveledUp)
             }
        }
    }

    private func load() async { do { quests = try await LocalDataStore.shared.request("/quests/today"); errorMessage = nil } catch { errorMessage = error.localizedDescription } }
    private func perform(_ action: QuestCard.Action, quest: Quest) async {
        busyID = quest.id; defer { busyID = nil }
        do {
            let result: QuestAction
            switch action {
            case .add: result = try await LocalDataStore.shared.request("/quests/\(quest.id)/progress", method: "POST", body: ["amount": 1])
            case .complete: result = try await LocalDataStore.shared.request("/quests/\(quest.id)/complete", method: "POST")
            }
            await load()
            if result.completed && result.expGained > 0 {
                rewardReceipt = RewardReceipt(title: quest.title, exp: result.expGained, leveledUp: result.leveledUp)
            }
        } catch { errorMessage = error.localizedDescription }
    }
}

private struct QuestRewardView: View {
    @Environment(\.dismiss) private var dismiss
    let title: String
    let exp: Int
    let leveledUp: Bool

    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                Image(systemName: leveledUp ? "sparkles" : "checkmark.seal.fill")
                    .font(.system(size: 54, weight: .semibold))
                    .foregroundStyle(leveledUp ? SystemTheme.gold : SystemTheme.cyan)
                    .accessibilityHidden(true)
                VStack(spacing: 8) {
                    Text(leveledUp ? "LEVEL UP" : "QUEST CLEARED")
                        .font(.caption.bold()).tracking(2).foregroundStyle(SystemTheme.cyan)
                    Text(title).font(.title2.bold()).multilineTextAlignment(.center)
                }
                SystemCard {
                    HStack {
                        Label("Player EXP", systemImage: "sparkles")
                        Spacer()
                        Text("+\(exp)").font(.title2.bold().monospaced()).foregroundStyle(SystemTheme.gold)
                    }
                }
                if leveledUp {
                    Text("Your new level and stat points are waiting in Player State.")
                        .font(.subheadline).foregroundStyle(SystemTheme.muted).multilineTextAlignment(.center)
                }
                Button("Continue") { dismiss() }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
            }
            .padding(24)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(SystemBackdrop())
            .navigationBarTitleDisplayMode(.inline)
        }
        .presentationDetents([.medium])
        .accessibilityElement(children: .contain)
    }
}

struct QuestRewardPreviewScreen: View {
    var body: some View {
        QuestRewardView(title: "Complete the morning training", exp: 120, leveledUp: true)
            .preferredColorScheme(.dark)
    }
}

struct QuestCard: View {
    enum Action { case add, complete }
    let quest: Quest
    let busy: Bool
    let action: (Action) -> Void

    var body: some View {
        SystemCard {
            VStack(alignment: .leading, spacing: 14) {
                HStack(alignment: .top) {
                    Text(quest.difficulty).font(.headline.monospaced()).foregroundStyle(quest.difficulty.contains(where: "ABS".contains) ? SystemTheme.gold : SystemTheme.cyan)
                        .frame(width: 34, height: 34).background(SystemTheme.surfaceRaised).overlay { Rectangle().stroke(SystemTheme.gold.opacity(0.25)) }
                    VStack(alignment: .leading, spacing: 3) {
                        Text(quest.title).font(.headline)
                        Text("\(quest.practiceMinutes) min · \(quest.practiceMinutes) EXP · \(quest.schedule.label)").font(.caption).foregroundStyle(SystemTheme.muted)
                    }
                }
                if let description = quest.description { Text(description).font(.subheadline).foregroundStyle(SystemTheme.muted) }
                if let instance = quest.currentInstance {
                    let fraction = min(Double(instance.progress) / Double(max(instance.targetCount, 1)), 1)
                    VStack(spacing: 6) {
                        HStack { Text("\(instance.progress) / \(instance.targetCount) \(quest.unit ?? "")"); Spacer(); Text(instance.periodEnd.map { "DUE \($0)" } ?? "NO DEADLINE") }
                            .font(.caption2.monospaced()).foregroundStyle(SystemTheme.muted)
                        ProgressView(value: fraction).tint(SystemTheme.cyan)
                    }
                    HStack {
                        Button { action(.add) } label: { Label("+1", systemImage: "plus") }.buttonStyle(.bordered)
                        Button { action(.complete) } label: { Label("Complete", systemImage: "checkmark") }.buttonStyle(.borderedProminent)
                    }.frame(maxWidth: .infinity, alignment: .trailing).disabled(busy)
                }
            }
        }
    }
}

struct QuestLibraryView: View {
    @State private var quests: [Quest] = []
    @State private var showingCreate = false
    var body: some View {
        NavigationStack {
            List(quests) { quest in
                HStack { Text(quest.difficulty).font(.headline.monospaced()).foregroundStyle(SystemTheme.cyan); VStack(alignment: .leading) { Text(quest.title); Text(quest.schedule.label).font(.caption).foregroundStyle(.secondary) }; Spacer(); Text("\(quest.practiceMinutes) EXP").font(.caption.monospaced()) }
            }
            .navigationTitle("All Quests")
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button { showingCreate = true } label: { Label("New quest", systemImage: "plus") }
                }
            }
            .task { await load() }
            .refreshable { await load() }
            .sheet(isPresented: $showingCreate) {
                CreateQuestView { _ in Task { await load() } }
            }
        }
    }
    private func load() async { quests = (try? await LocalDataStore.shared.request("/quests")) ?? [] }
}
