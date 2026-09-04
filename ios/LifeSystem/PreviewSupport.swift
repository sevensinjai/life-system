import SwiftUI

private struct ProofSkillPayload: Codable {
    let name: String
    let description: String?
    let parentId: Int?
    let iconKey: String?
}

private struct ProofPracticeAttachment: Codable {
    let kind: String
    let filename: String
    let contentType: String
    let dataBase64: String
}

private struct ProofPracticePayload: Codable {
    let minutes: Int
    let note: String?
    let attachments: [ProofPracticeAttachment]
}

private struct ProofSchedule: Codable { let kind: String }
private struct ProofQuestPayload: Codable {
    let title: String
    let description: String?
    let schedule: ProofSchedule
    let difficulty: String
    let targetCount: Int
    let unit: String?
    let practiceMinutes: Int
    let statReward: String?
    let statRewardAmount: Int
    let skillId: Int?
}

struct ProgressionProofScreen: View {
    @State private var checks: [(String, Bool, String)] = []
    @State private var running = true

    var body: some View {
        NavigationStack {
            List {
                Section {
                    ForEach(Array(checks.enumerated()), id: \.offset) { _, check in
                        HStack(alignment: .top, spacing: 12) {
                            Image(systemName: check.1 ? "checkmark.seal.fill" : "xmark.octagon.fill")
                                .foregroundStyle(check.1 ? .green : .red)
                            VStack(alignment: .leading, spacing: 3) {
                                Text(check.0).font(.headline)
                                Text(check.2).font(.caption.monospaced()).foregroundStyle(.secondary)
                            }
                        }
                    }
                } header: { Text("Durable core loop") }
            }
            .overlay { if running { ProgressView("Exercising progression…") } }
            .navigationTitle("Progression Proof")
            .task { await run() }
        }
    }

    @MainActor private func run() async {
        do {
            let store = LocalDataStore.shared
            let before: PlayerStatus = try await store.request("/players/me")
            let questAward = max(1, before.expToNextLevel - before.exp + 10)
            var roots: [SkillNode] = try await store.request("/skills")
            let root: SkillSummary
            if let existing = roots.first(where: { $0.name == "Progression Proof" })?.summary { root = existing }
            else { root = try await store.request("/skills", method: "POST", body: ProofSkillPayload(name: "Progression Proof", description: "Integration proof", parentId: nil, iconKey: nil)) }
            roots = try await store.request("/skills")
            let child: SkillSummary
            if let existing = roots.flatMap(\.children).first(where: { $0.name == "Daily Practice" })?.summary { child = existing }
            else { child = try await store.request("/skills", method: "POST", body: ProofSkillPayload(name: "Daily Practice", description: nil, parentId: root.id, iconKey: nil)) }

            let proofBytes = Data("saved proof".utf8)
            let practice: PracticeResult = try await store.request("/skills/\(child.id)/practice", method: "POST", body: ProofPracticePayload(minutes: 120, note: "Persistence proof", attachments: [.init(kind: "audio", filename: "proof.m4a", contentType: "audio/mp4", dataBase64: proofBytes.base64EncodedString())]))
            let quest: Quest = try await store.request("/quests", method: "POST", body: ProofQuestPayload(title: "Complete the proof loop", description: nil, schedule: .init(kind: "daily"), difficulty: "E", targetCount: 1, unit: "session", practiceMinutes: questAward, statReward: "strength", statRewardAmount: 1, skillId: child.id))
            let action: QuestAction = try await store.request("/quests/\(quest.id)/complete", method: "POST")

            let after: PlayerStatus = try await store.request("/players/me")
            let afterRoots: [SkillNode] = try await store.request("/skills")
            let today: [Quest] = try await store.request("/quests/today")
            let entries: [PracticeEntry] = try await store.request("/skills/\(child.id)/practice")
            let savedBytes: Data? = if let attachmentID = entries.first?.attachments.first?.id { try await store.request("/practice-attachments/\(attachmentID)") } else { nil }
            let updatedRoot = afterRoots.first(where: { $0.id == root.id })
            let updatedChild = updatedRoot?.children.first(where: { $0.id == child.id })

            checks = [
                ("Player reward applied", after.totalExpEarned == before.totalExpEarned + questAward, "\(before.totalExpEarned) → \(after.totalExpEarned) total EXP"),
                ("Level curve applied", action.leveledUp && after.level > before.level, "Level \(before.level) → \(after.level)"),
                ("Stat reward applied", after.stats.strength == before.stats.strength + 1, "Strength \(before.stats.strength) → \(after.stats.strength)"),
                ("Completed quest left Today", !today.contains(where: { $0.id == quest.id }), "Quest #\(quest.id) is completed"),
                ("Child remains nested", updatedChild?.parentId == root.id && updatedChild?.depth == 2, "\(root.name) › \(child.name)"),
                ("Practice and quest train child", (updatedChild?.totalExpEarned ?? 0) >= child.totalExpEarned + 120 + questAward, "+120 practice, +\(questAward) quest"),
                ("Awards roll up to parent", (updatedRoot?.totalExpEarned ?? 0) >= root.totalExpEarned + 120 + questAward, "Parent received both awards"),
                ("Journal and media persist", entries.first?.attachments.count == 1 && practice.entry.attachments.count == 1 && savedBytes == proofBytes, "Saved note with \(savedBytes?.count ?? 0) bytes")
            ]
        } catch {
            checks = [("Progression proof failed", false, error.localizedDescription)]
        }
        running = false
    }
}

struct DailyResetProofScreen: View {
    @State private var checks: [(String, Bool, String)] = []
    @State private var running = true

    var body: some View {
        NavigationStack {
            List {
                Section("Recurring settlement") {
                    ForEach(Array(checks.enumerated()), id: \.offset) { _, check in
                        HStack(alignment: .top, spacing: 12) {
                            Image(systemName: check.1 ? "checkmark.seal.fill" : "xmark.octagon.fill")
                                .foregroundStyle(check.1 ? .green : .red)
                            VStack(alignment: .leading, spacing: 3) {
                                Text(check.0).font(.headline)
                                Text(check.2).font(.caption.monospaced()).foregroundStyle(.secondary)
                            }
                        }
                    }
                }
            }
            .overlay { if running { ProgressView("Settling a missed period…") } }
            .navigationTitle("Reset Proof")
            .task { await run() }
        }
    }

    @MainActor private func run() async {
        var stage = "load player"
        do {
            let store = LocalDataStore.shared
            let before: PlayerStatus = try await store.request("/players/me")
            stage = "create funding quest"
            let awardQuest: Quest = try await store.request("/quests", method: "POST", body: ProofQuestPayload(title: "Fund reset proof", description: nil, schedule: .init(kind: "once"), difficulty: "E", targetCount: 1, unit: "session", practiceMinutes: 40, statReward: nil, statRewardAmount: 0, skillId: nil))
            stage = "complete funding quest"
            let _: QuestAction = try await store.request("/quests/\(awardQuest.id)/complete", method: "POST")
            stage = "create recurring quest"
            let missed: Quest = try await store.request("/quests", method: "POST", body: ProofQuestPayload(title: "Daily reset proof", description: nil, schedule: .init(kind: "daily"), difficulty: "E", targetCount: 2, unit: "sessions", practiceMinutes: 25, statReward: nil, statRewardAmount: 0, skillId: nil))
            stage = "backdate recurring quest"
            try store.backdateQuestForResetProof(missed.id)
            stage = "first reset"
            let first: DailyReset = try await store.request("/system/daily-reset", method: "POST")
            stage = "idempotence reset"
            let second: DailyReset = try await store.request("/system/daily-reset", method: "POST")
            stage = "reload durable state"
            let after: PlayerStatus = try await store.request("/players/me")
            let today: [Quest] = try await store.request("/quests/today")
            let events: [SystemEvent] = try await store.request("/system/events")
            let reopened = today.first(where: { $0.id == missed.id })
            checks = [
                ("Missed period failed once", first.failedCount == 1 && second.failedCount == 0, "reset counts \(first.failedCount), then \(second.failedCount)"),
                ("Penalty applied once", first.totalExpLost == 25 && second.totalExpLost == 0 && after.exp == before.exp + 15, "funded +40 EXP, then lost 25"),
                ("Fresh period opened", first.spawnedCount == 1 && second.spawnedCount == 0 && reopened?.currentInstance?.progress == 0, "new active instance #\(reopened?.currentInstance?.id ?? 0)"),
                ("Failure is explained", events.contains(where: { $0.eventType == "quest_failed" && $0.message.contains("Daily reset proof") }) && events.contains(where: { $0.eventType == "penalty_applied" && $0.message.contains("-25 EXP") }), "failure and penalty transmissions saved")
            ]
        } catch {
            checks = [("Reset proof failed", false, "\(stage): \(String(reflecting: error))")]
        }
        running = false
    }
}

struct LockScreenWidgetSimulationView: View {
    private let quote = "The work you do today becomes your strength tomorrow."

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 0.08, green: 0.13, blue: 0.22),
                    Color(red: 0.02, green: 0.04, blue: 0.08),
                    Color.black,
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            Circle()
                .fill(SystemTheme.cyan.opacity(0.18))
                .frame(width: 330)
                .blur(radius: 90)
                .offset(x: 160, y: -320)

            VStack(spacing: 0) {
                Text("Monday, 31 August")
                    .font(.system(size: 17, weight: .semibold, design: .rounded))
                    .padding(.top, 72)

                Text("18:42")
                    .font(.system(size: 82, weight: .thin, design: .rounded))
                    .tracking(-3)

                HStack(spacing: 12) {
                    Image(systemName: "flashlight.off.fill")
                        .frame(width: 42, height: 42)
                        .background(.black.opacity(0.32), in: Circle())
                    Spacer()
                    Image(systemName: "camera.fill")
                        .frame(width: 42, height: 42)
                        .background(.black.opacity(0.32), in: Circle())
                }
                .padding(.horizontal, 48)
                .opacity(0)
                .frame(height: 10)

                VStack(alignment: .leading, spacing: 7) {
                    Label("QUICK ACTIONS", systemImage: "bolt.fill")
                        .font(.system(size: 9, weight: .bold))
                        .tracking(1)
                        .foregroundStyle(SystemTheme.cyan)
                    HStack(spacing: 5) {
                        ForEach(["house.fill", "checklist", "figure.run", "point.3.connected.trianglepath.dotted"], id: \.self) { icon in
                            Image(systemName: icon)
                                .font(.system(size: 13, weight: .semibold))
                                .frame(maxWidth: .infinity, maxHeight: .infinity)
                                .background(.white.opacity(0.12), in: RoundedRectangle(cornerRadius: 7))
                        }
                    }
                }
                .padding(8)
                .frame(width: 158, height: 66, alignment: .leading)
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
                .overlay {
                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                        .stroke(.white.opacity(0.12))
                }
                .padding(.top, 12)

                Spacer()

                HStack {
                    Image(systemName: "flashlight.off.fill")
                    Spacer()
                    Image(systemName: "camera.fill")
                }
                .font(.title3)
                .padding(.horizontal, 60)
                .padding(.bottom, 54)
            }
            .foregroundStyle(.white)
        }
        .preferredColorScheme(.dark)
    }
}

#Preview("Lock Screen widget simulation") {
    LockScreenWidgetSimulationView()
}

struct HomeScreenQuoteWidgetSimulationView: View {
    private let quote = "The work you do today becomes your strength tomorrow."

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color(red: 0.05, green: 0.12, blue: 0.22), .black],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 26) {
                HStack {
                    Text("18:42").font(.headline)
                    Spacer()
                    Image(systemName: "wifi")
                    Image(systemName: "battery.100percent")
                }
                .padding(.horizontal, 24)
                .padding(.top, 10)

                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Label("SYSTEM", systemImage: "diamond.fill")
                            .font(.caption.bold())
                            .tracking(1.8)
                            .foregroundStyle(SystemTheme.cyan)
                        Spacer()
                        Text("TODAY")
                            .font(.caption2.bold())
                            .foregroundStyle(.secondary)
                    }
                    Spacer(minLength: 0)
                    Text(quote)
                        .font(.system(.title3, design: .rounded, weight: .bold))
                        .lineLimit(3)
                    Text("— The System")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.secondary)
                }
                .padding(18)
                .frame(maxWidth: .infinity, alignment: .leading)
                .frame(height: 166)
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
                .overlay {
                    RoundedRectangle(cornerRadius: 24, style: .continuous)
                        .stroke(.white.opacity(0.12))
                }
                .padding(.horizontal, 20)

                LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 4), spacing: 28) {
                    ForEach(Array(zip(
                        ["checkmark.circle.fill", "figure.run", "book.closed.fill", "music.note", "camera.fill", "brain.head.profile", "calendar", "ellipsis"],
                        ["Quests", "Train", "Read", "Music", "Camera", "Skills", "Calendar", "More"]
                    )), id: \.1) { icon, label in
                        VStack(spacing: 6) {
                            Image(systemName: icon)
                                .font(.title2)
                                .frame(width: 58, height: 58)
                                .background(SystemTheme.surfaceRaised, in: RoundedRectangle(cornerRadius: 14))
                            Text(label).font(.caption2)
                        }
                    }
                }
                .padding(.horizontal, 24)

                Spacer()
            }
            .foregroundStyle(.white)
        }
        .preferredColorScheme(.dark)
    }
}

#Preview("Home Screen wide widget simulation") {
    HomeScreenQuoteWidgetSimulationView()
}

#Preview("Quest card", traits: .sizeThatFitsLayout) {
    QuestCard(quest: .preview, busy: false) { _ in }
        .padding()
        .background(SystemTheme.background)
        .preferredColorScheme(.dark)
}

#Preview("System header", traits: .sizeThatFitsLayout) {
    SystemHeader(title: "Quest Board", eyebrow: "Active missions")
        .padding()
        .background(SystemTheme.background)
        .preferredColorScheme(.dark)
}

private extension Quest {
    static let preview = Quest(
        id: 12,
        title: "Complete the morning training",
        description: "Build momentum before the day begins.",
        schedule: QuestSchedule(label: "Every day"),
        difficulty: "C",
        targetCount: 100,
        unit: "reps",
        practiceMinutes: 20,
        statReward: "strength",
        statRewardAmount: 1,
        isActive: true,
        currentInstance: QuestInstance(
            id: 34,
            progress: 40,
            targetCount: 100,
            status: "active",
            periodEnd: "Today"
        ),
        nextDueDate: nil
    )
}
