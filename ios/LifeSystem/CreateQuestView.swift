import SwiftUI

private enum QuestScheduleKind: String, CaseIterable, Identifiable {
    case once, daily, weekdays, interval, weekly
    var id: String { rawValue }
    var label: String {
        switch self {
        case .once: "One time"
        case .daily: "Every day"
        case .weekdays: "Selected days"
        case .interval: "Every N days"
        case .weekly: "Weekly target"
        }
    }
    var detail: String {
        switch self {
        case .once: "Stays open until you clear it."
        case .daily: "A fresh period opens each local day."
        case .weekdays: "Opens only on the weekdays you choose."
        case .interval: "You get the full interval to complete it."
        case .weekly: "Complete the target at any time during the week."
        }
    }
}

private enum QuestRank: String, CaseIterable, Identifiable {
    case E, D, C, B, A, S
    var id: String { rawValue }
}

private enum RewardStat: String, CaseIterable, Identifiable {
    case strength, agility, vitality, intelligence, perception
    var id: String { rawValue }
}

private struct QuestSchedulePayload: Codable {
    let kind: String
    let days: [Int]?
    let intervalDays: Int?
    let weekStart: Int?
}

private struct CreateQuestPayload: Codable {
    let title: String
    let description: String?
    let schedule: QuestSchedulePayload
    let difficulty: String
    let targetCount: Int
    let unit: String?
    let practiceMinutes: Int
    let statReward: String?
    let statRewardAmount: Int
    let skillId: Int?
}

struct CreateQuestView: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    let linkedSkill: SkillSummary?
    let onCreated: (Quest) -> Void

    init(
        linkedSkill: SkillSummary? = nil,
        initialSkillRoots: [SkillNode] = [],
        onCreated: @escaping (Quest) -> Void
    ) {
        self.linkedSkill = linkedSkill
        self.onCreated = onCreated
        _kind = State(
            initialValue: ProcessInfo.processInfo.arguments.contains("-createQuestWeekdaysPreview")
                ? .weekdays
                : .daily
        )
        _selectedSkillID = State(initialValue: linkedSkill?.id)
        _skillRoots = State(initialValue: initialSkillRoots)
    }

    @State private var title = ""
    @State private var description = ""
    @State private var kind: QuestScheduleKind = .daily
    @State private var weekdays: Set<Int> = Set(0...6)
    @State private var intervalDays = 2
    @State private var weekStart = 0
    @State private var rank: QuestRank = .E
    @State private var target = 1
    @State private var unit = ""
    @State private var minutes = 10
    @State private var givesStatReward = false
    @State private var rewardStat: RewardStat = .strength
    @State private var rewardAmount = 1
    @State private var selectedSkillID: Int?
    @State private var skillRoots: [SkillNode]
    @State private var isLoadingSkills = false
    @State private var skillLoadError: String?
    @State private var isSaving = false
    @State private var errorMessage: String?

    private let daySymbols = Calendar.current.shortWeekdaySymbols
    private var orderedMondayFirstDays: [(Int, String)] {
        // Backend weekdays are Monday = 0; Calendar symbols begin on Sunday.
        Array(daySymbols.dropFirst() + daySymbols.prefix(1)).enumerated().map { ($0, $1) }
    }
    private var canSave: Bool {
        !title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        target > 0 && minutes > 0 &&
        (linkedSkill == nil || selectedSkillID != nil) &&
        (kind != .weekdays || !weekdays.isEmpty) && !isSaving
    }

    private var usesAccessibilityLayout: Bool { dynamicTypeSize.isAccessibilitySize }

    private var skillOptions: [SkillSummary] {
        func flatten(_ nodes: [SkillNode]) -> [SkillSummary] {
            nodes.flatMap { [$0.summary] + flatten($0.children) }
        }
        let loaded = flatten(skillRoots)
        if loaded.isEmpty, let linkedSkill { return [linkedSkill] }
        return loaded
    }

    private var selectedSkillName: String {
        skillOptions.first(where: { $0.id == selectedSkillID })?.name
            ?? linkedSkill?.name
            ?? "Selected skill"
    }

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    TextField("Quest title", text: $title)
                        .textInputAutocapitalization(.sentences)
                    TextField("Description (optional)", text: $description, axis: .vertical)
                        .lineLimit(2...4)
                } header: { Text("Mission") }

                if linkedSkill != nil {
                    Section {
                        Picker("Skill", selection: $selectedSkillID) {
                            ForEach(skillOptions) { skill in
                                HStack(spacing: 8) {
                                    if skill.depth > 1 {
                                        Text(String(repeating: "› ", count: skill.depth - 1))
                                            .foregroundStyle(.secondary)
                                    }
                                    Text(skill.name)
                                }
                                .tag(Optional(skill.id))
                            }
                        }
                        .disabled(isLoadingSkills)

                        if isLoadingSkills {
                            HStack {
                                ProgressView()
                                Text("Loading skill tree…")
                            }
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        } else if let skillLoadError {
                            Text(skillLoadError)
                                .font(.caption)
                                .foregroundStyle(.red)
                        }

                        Text("Completion credits \(minutes) minutes to \(selectedSkillName) and rolls EXP up through its parent branch.")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    } header: {
                        Text("Trains")
                    }
                }

                Section {
                    Picker("Repeats", selection: $kind) {
                        ForEach(QuestScheduleKind.allCases) { kind in
                            Text(kind.label).tag(kind)
                        }
                    }
                    Text(kind.detail)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                        .fixedSize(horizontal: false, vertical: true)

                    if kind == .weekdays {
                        weekdayPicker
                    }
                    if kind == .interval {
                        Stepper("Every \(intervalDays) days", value: $intervalDays, in: 1...365)
                    }
                    if kind == .weekly {
                        Picker("Week starts", selection: $weekStart) {
                            ForEach(orderedMondayFirstDays, id: \.0) { index, day in
                                Text(day).tag(index)
                            }
                        }
                    }
                } header: { Text("Schedule") }

                Section {
                    Picker("Difficulty", selection: $rank) {
                        ForEach(QuestRank.allCases) { rank in Text(rank.rawValue).tag(rank) }
                    }
                    Stepper("Target: \(target)", value: $target, in: 1...100_000)
                    TextField("Unit (minutes, reps, pages…)", text: $unit)
                        .textInputAutocapitalization(.never)
                    Stepper("Practice: \(minutes) minutes", value: $minutes, in: 1...10_000)
                } header: { Text("Target and reward") }
                  footer: { Text("Completion awards \(minutes) EXP. One practice minute equals one EXP.") }

                Section {
                    Toggle("Grant a stat reward", isOn: $givesStatReward)
                    if givesStatReward {
                        Picker("Attribute", selection: $rewardStat) {
                            ForEach(RewardStat.allCases) { stat in
                                Text(stat.rawValue.capitalized).tag(stat)
                            }
                        }
                        Stepper("Amount: +\(rewardAmount)", value: $rewardAmount, in: 1...100)
                    }
                } header: { Text("Optional bonus") }

                Section {
                    summary
                    if let errorMessage {
                        Text(errorMessage).font(.footnote).foregroundStyle(.red)
                    }
                } header: { Text("Review") }
            }
            .dynamicTypeSize(.large ... .accessibility2)
            .navigationTitle(linkedSkill == nil ? "New Quest" : "New Routine")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button(isSaving ? "Creating…" : "Create") {
                        Task { await create() }
                    }
                    .fontWeight(.semibold)
                    .disabled(!canSave)
                }
            }
            .task {
                if linkedSkill != nil, skillRoots.isEmpty {
                    await loadSkills()
                }
            }
        }
    }

    private var weekdayPicker: some View {
        let columns = Array(
            repeating: GridItem(.flexible(), spacing: 8),
            count: usesAccessibilityLayout ? 2 : 7
        )

        return LazyVGrid(columns: columns, alignment: .leading, spacing: 8) {
            ForEach(orderedMondayFirstDays, id: \.0) { index, day in
                Button {
                    if weekdays.contains(index) { weekdays.remove(index) }
                    else { weekdays.insert(index) }
                } label: {
                    Text(usesAccessibilityLayout ? day : String(day.prefix(1)))
                        .font(.caption.bold())
                        .frame(maxWidth: .infinity)
                        .frame(minHeight: 44)
                        .padding(.horizontal, usesAccessibilityLayout ? 6 : 0)
                        .background(weekdays.contains(index) ? SystemTheme.cyan : Color.secondary.opacity(0.15))
                        .foregroundStyle(weekdays.contains(index) ? SystemTheme.background : .primary)
                        .clipShape(usesAccessibilityLayout ? AnyShape(Capsule()) : AnyShape(Circle()))
                }
                .buttonStyle(.plain)
                .accessibilityLabel(day)
                .accessibilityValue(weekdays.contains(index) ? "Selected" : "Not selected")
            }
        }
        .padding(.vertical, 4)
    }

    private var summary: some View {
        VStack(alignment: .leading, spacing: 8) {
            ViewThatFits(in: .horizontal) {
                HStack(alignment: .firstTextBaseline) {
                    summaryHeading
                }
                VStack(alignment: .leading, spacing: 4) {
                    summaryHeading
                }
            }
            Label(kind.label, systemImage: "calendar")
            Label("\(target) \(unit.isEmpty ? "unit\(target == 1 ? "" : "s")" : unit)", systemImage: "scope")
            Label("\(minutes) EXP on completion", systemImage: "sparkles")
            if linkedSkill != nil {
                Label("Trains \(selectedSkillName)", systemImage: "point.3.connected.trianglepath.dotted")
            }
            if givesStatReward {
                Label("+\(rewardAmount) \(rewardStat.rawValue)", systemImage: "arrow.up.circle")
            }
        }
        .font(.subheadline)
        .foregroundStyle(.secondary)
        .padding(.vertical, 4)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(summaryAccessibilityLabel)
    }

    @ViewBuilder
    private var summaryHeading: some View {
        Text(rank.rawValue)
            .font(.headline.monospaced())
            .foregroundStyle(SystemTheme.cyan)
        Text(title.isEmpty ? "Untitled quest" : title)
            .font(.headline)
            .fixedSize(horizontal: false, vertical: true)
    }

    private var summaryAccessibilityLabel: String {
        var parts = [
            "\(rank.rawValue) rank, \(title.isEmpty ? "Untitled quest" : title)",
            kind.label,
            "Target \(target) \(unit.isEmpty ? "units" : unit)",
            "\(minutes) experience on completion"
        ]
        if linkedSkill != nil { parts.append("Trains \(selectedSkillName)") }
        if givesStatReward { parts.append("Rewards \(rewardAmount) \(rewardStat.rawValue)") }
        return parts.joined(separator: ", ")
    }

    private func create() async {
        isSaving = true
        errorMessage = nil
        defer { isSaving = false }

        let payload = CreateQuestPayload(
            title: title.trimmingCharacters(in: .whitespacesAndNewlines),
            description: description.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty,
            schedule: QuestSchedulePayload(
                kind: kind.rawValue,
                days: kind == .weekdays ? weekdays.sorted() : nil,
                intervalDays: kind == .interval ? intervalDays : nil,
                weekStart: kind == .weekly ? weekStart : nil
            ),
            difficulty: rank.rawValue,
            targetCount: target,
            unit: unit.trimmingCharacters(in: .whitespacesAndNewlines).nilIfEmpty,
            practiceMinutes: minutes,
            statReward: givesStatReward ? rewardStat.rawValue : nil,
            statRewardAmount: givesStatReward ? rewardAmount : 0,
            skillId: linkedSkill == nil ? nil : selectedSkillID
        )

        do {
            let quest: Quest = try await LocalDataStore.shared.request("/quests", method: "POST", body: payload)
            onCreated(quest)
            dismiss()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    private func loadSkills() async {
        isLoadingSkills = true
        skillLoadError = nil
        defer { isLoadingSkills = false }
        do {
            skillRoots = try await LocalDataStore.shared.request("/skills")
            if !skillOptions.contains(where: { $0.id == selectedSkillID }) {
                selectedSkillID = linkedSkill?.id ?? skillOptions.first?.id
            }
        } catch {
            skillLoadError = "Couldn’t load the skill tree. Keeping \(linkedSkill?.name ?? "the current skill")."
        }
    }
}

private extension String {
    var nilIfEmpty: String? { isEmpty ? nil : self }
}

#Preview("Create daily quest") {
    CreateQuestView(onCreated: { _ in })
        .preferredColorScheme(.dark)
}

struct CreateRoutinePreviewScreen: View {
    private let photography = SkillNode(
        id: 901, parentId: nil, name: "Photography",
        description: "Composition, light, and visual storytelling",
        level: 1, exp: 0, expToNextLevel: 100, expProgress: 0,
        totalExpEarned: 0, isActive: true, depth: 1, createdAt: "2026-08-31",
        children: [
            SkillNode(id: 902, parentId: 901, name: "Composition", description: nil, level: 1, exp: 0, expToNextLevel: 100, expProgress: 0, totalExpEarned: 0, isActive: true, depth: 2, createdAt: "2026-08-31", children: []),
            SkillNode(id: 903, parentId: 901, name: "Lighting", description: nil, level: 1, exp: 0, expToNextLevel: 100, expProgress: 0, totalExpEarned: 0, isActive: true, depth: 2, createdAt: "2026-08-31", children: [
                SkillNode(id: 904, parentId: 903, name: "Natural light", description: nil, level: 1, exp: 0, expToNextLevel: 100, expProgress: 0, totalExpEarned: 0, isActive: true, depth: 3, createdAt: "2026-08-31", children: [])
            ]),
            SkillNode(id: 905, parentId: 901, name: "Portraits", description: nil, level: 1, exp: 0, expToNextLevel: 100, expProgress: 0, totalExpEarned: 0, isActive: true, depth: 2, createdAt: "2026-08-31", children: [])
        ]
    )

    var body: some View {
        CreateQuestView(
            linkedSkill: photography.summary,
            initialSkillRoots: [photography],
            onCreated: { _ in }
        )
    }
}

#Preview("Create skill routine") {
    CreateRoutinePreviewScreen()
        .preferredColorScheme(.dark)
}
