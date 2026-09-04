import Foundation
import SwiftData

@Model final class SyncedSystemState {
    var payload: Data = Data()
    var modifiedAt: Date = Date()
    init(payload: Data) { self.payload = payload }
}

struct LocalSnapshot: Codable {
    var player: PlayerStatus
    var quests: [Quest]
    var skills: [SkillNode]
    var practices: [Int: [PracticeEntry]]
    var events: [SystemEvent]
    var quote: DailyQuote
    var attachmentData: [Int: Data]?
    var penalties: [LocalPenalty]?

    static var initial: Self {
        .init(player: .init(id: 1, name: "Player", level: 1, exp: 0, expToNextLevel: 100, expProgress: 0, totalExpEarned: 0, statPoints: 0, stats: .init(strength: 1, agility: 1, vitality: 1, intelligence: 1, perception: 1), timezone: TimeZone.current.identifier), quests: [], skills: [], practices: [:], events: [], quote: .init(localDate: Date.now.formatted(.iso8601.year().month().day()), quote: .init(id: 1, text: "Small steps, repeated, become a life.", author: "The System"), poolSize: 1, refreshAfter: Calendar.current.date(byAdding: .day, value: 1, to: .now)!.ISO8601Format()), attachmentData: [:], penalties: [])
    }
}

struct LocalPenalty: Codable {
    let questId: Int
    let instanceId: Int
    let reason: String
    let expLost: Int
    let createdAt: String
}

@MainActor final class PersistenceController {
    static let shared = PersistenceController()
    let container: ModelContainer
    private init() {
        do {
            container = try ModelContainer(for: SyncedSystemState.self, configurations: ModelConfiguration(cloudKitDatabase: .automatic))
        } catch {
            container = try! ModelContainer(for: SyncedSystemState.self, configurations: ModelConfiguration(cloudKitDatabase: .none))
        }
    }
}

enum LocalDataError: LocalizedError {
    case unsupported(String), missing(String)
    var errorDescription: String? {
        switch self { case .unsupported(let value): "Unsupported local operation: \(value)"; case .missing(let value): "\(value) could not be found." }
    }
}

@MainActor final class LocalDataStore {
    static let shared = LocalDataStore()
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()
    private init() { encoder.keyEncodingStrategy = .convertToSnakeCase; decoder.keyDecodingStrategy = .convertFromSnakeCase }

    func request<Response: Decodable, Body: Encodable>(_ rawPath: String, method: String = "GET", body: Body? = Optional<String>.none) async throws -> Response {
        let context = PersistenceController.shared.container.mainContext
        let record = try load(context)
        var data = try decoder.decode(LocalSnapshot.self, from: record.payload)
        let path = rawPath.components(separatedBy: "?").first ?? rawPath
        let fields = try body.map(dictionary) ?? [:]
        let result: any Encodable

        switch (method, path) {
        case ("GET", "/players/me"): result = data.player
        case ("GET", "/quests"), ("GET", "/quests/today"):
            result = path.hasSuffix("today")
                ? data.quests.filter { $0.isActive && $0.currentInstance?.status == "active" }
                : data.quests
        case ("POST", "/quests"):
            let id = (data.quests.map(\.id).max() ?? 0) + 1
            let target = fields["target_count"] as? Int ?? 1
            let scheduleFields = fields["schedule"] as? [String: Any] ?? [:]
            let schedule = scheduleFields["kind"] as? String ?? "daily"
            let today = localDay(for: data.player)
            let spec = QuestSchedule(label: scheduleLabel(schedule), kind: schedule, days: scheduleFields["days"] as? [Int], intervalDays: scheduleFields["interval_days"] as? Int, anchor: isoDay(today), weekStart: scheduleFields["week_start"] as? Int)
            let period = currentPeriod(for: spec, on: today)
            let instance = period.map { QuestInstance(id: id, progress: 0, targetCount: target, status: "active", periodEnd: $0.end.map(isoDay), periodStart: isoDay($0.start)) }
            let quest = Quest(id: id, title: fields["title"] as? String ?? "Untitled quest", description: fields["description"] as? String, schedule: spec, difficulty: fields["difficulty"] as? String ?? "E", targetCount: target, unit: fields["unit"] as? String, practiceMinutes: fields["practice_minutes"] as? Int ?? 10, statReward: fields["stat_reward"] as? String, statRewardAmount: fields["stat_reward_amount"] as? Int ?? 0, skillId: fields["skill_id"] as? Int, isActive: true, currentInstance: instance, nextDueDate: nil)
            data.quests.append(quest); result = quest
        case ("POST", let value) where value.hasSuffix("/progress") || value.hasSuffix("/complete"):
            guard let id = Int(value.split(separator: "/")[1]), let index = data.quests.firstIndex(where: { $0.id == id }) else { throw LocalDataError.missing("Quest") }
            let old = data.quests[index], target = old.currentInstance?.targetCount ?? old.targetCount
            guard old.currentInstance?.status == "active" else {
                result = QuestAction(completed: true, expGained: 0, leveledUp: false)
                break
            }
            let progress = value.hasSuffix("/complete") ? target : min((old.currentInstance?.progress ?? 0) + (fields["amount"] as? Int ?? 1), target)
            data.quests[index] = old.replacingProgress(progress)
            let completed = progress >= target
            var leveledUp = false
            if completed {
                let playerAward = awardPlayer(data.player, amount: old.practiceMinutes, statReward: old.statReward, statRewardAmount: old.statRewardAmount)
                data.player = playerAward.player
                leveledUp = playerAward.levelsGained > 0
                if let skillID = old.skillId {
                    let skillAwards = awardSkillTree(&data.skills, skillID: skillID, amount: old.practiceMinutes)
                    appendSkillLevelEvents(skillAwards, events: &data.events)
                }
                data.events.insert(.init(id: nextEventID(data.events), eventType: "quest_completed", message: "Completed \(old.title) and gained \(old.practiceMinutes) EXP.", createdAt: Date.now.ISO8601Format()), at: 0)
                if leveledUp {
                    data.events.insert(.init(id: nextEventID(data.events), eventType: "level_up", message: "Level up! You are now Level \(data.player.level).", createdAt: Date.now.ISO8601Format()), at: 0)
                }
            }
            result = QuestAction(completed: completed, expGained: completed ? old.practiceMinutes : 0, leveledUp: leveledUp)
        case ("GET", "/skills"): result = data.skills
        case ("POST", "/skills"):
            let id = maxSkillID(data.skills) + 1
            let parentID = fields["parent_id"] as? Int
            let depth = parentID.flatMap { findSkill($0, data.skills)?.depth }.map { $0 + 1 } ?? 1
            let skill = SkillSummary(id: id, parentId: parentID, name: fields["name"] as? String ?? "New skill", description: fields["description"] as? String, iconKey: fields["icon_key"] as? String, level: 1, exp: 0, expToNextLevel: 100, expProgress: 0, totalExpEarned: 0, isActive: true, depth: depth, createdAt: Date.now.ISO8601Format())
            if let parentID { insertSkill(skill.node(), under: parentID, in: &data.skills) }
            else { data.skills.append(skill.node()) }
            result = skill
        case ("GET", let value) where value.hasSuffix("/practice"):
            let id = Int(value.split(separator: "/")[1]) ?? 0; result = data.practices[id] ?? []
        case ("POST", let value) where value.hasSuffix("/practice"):
            let id = Int(value.split(separator: "/")[1]) ?? 0
            guard let skill = findSkill(id, data.skills) else { throw LocalDataError.missing("Skill") }
            let minutes = fields["minutes"] as? Int ?? 1
            let rawAttachments = fields["attachments"] as? [[String: Any]] ?? []
            if data.attachmentData == nil { data.attachmentData = [:] }
            var nextAttachmentID = maxAttachmentID(data.practices) + 1
            let attachments = rawAttachments.compactMap { item -> PracticeAttachment? in
                guard let encoded = item["data_base64"] as? String, let bytes = Data(base64Encoded: encoded) else { return nil }
                let attachment = PracticeAttachment(id: nextAttachmentID, kind: item["kind"] as? String ?? "file", filename: item["filename"] as? String ?? "attachment", contentType: item["content_type"] as? String ?? "application/octet-stream", byteCount: bytes.count)
                data.attachmentData?[nextAttachmentID] = bytes
                nextAttachmentID += 1
                return attachment
            }
            let entry = PracticeEntry(id: (data.practices.values.flatMap { $0 }.map(\.id).max() ?? 0) + 1, skillId: id, skillName: skill.name, minutes: minutes, note: fields["note"] as? String, createdAt: Date.now.ISO8601Format(), attachments: attachments)
            data.practices[id, default: []].insert(entry, at: 0)
            let awards = awardSkillTree(&data.skills, skillID: id, amount: minutes)
            appendSkillLevelEvents(awards, events: &data.events)
            guard let updated = findSkill(id, data.skills) else { throw LocalDataError.missing("Skill") }
            result = PracticeResult(skill: updated, awards: awards, entry: entry)
        case ("GET", let value) where value.hasPrefix("/skills/"):
            let id = Int(value.split(separator: "/")[1]) ?? 0
            guard let skill = findSkill(id, data.skills) else { throw LocalDataError.missing("Skill") }
            result = skillDetail(for: skill, in: data.skills)
        case ("PATCH", let value) where value.hasPrefix("/skills/"):
            let id = Int(value.split(separator: "/")[1]) ?? 0
            guard var skill = findSkill(id, data.skills) else { throw LocalDataError.missing("Skill") }
            skill.iconKey = fields["icon_key"] as? String; replaceSkill(skill, in: &data.skills); result = skill
        case ("GET", "/quotes/today"): result = data.quote
        case ("GET", "/system/events"): result = data.events
        case ("GET", let value) where value.hasPrefix("/practice-attachments/"):
            let id = Int(value.split(separator: "/").last ?? "") ?? 0
            guard let bytes = data.attachmentData?[id] else { throw LocalDataError.missing("Practice attachment") }
            result = bytes
        case ("POST", "/system/daily-reset"):
            result = runLocalDailyReset(&data, on: localDay(for: data.player))
        default: throw LocalDataError.unsupported("\(method) \(path)")
        }
        if method != "GET" { record.payload = try encoder.encode(data); record.modifiedAt = .now; try context.save() }
        return try decoder.decode(Response.self, from: try encoder.encode(result))
    }

    func request<Response: Decodable>(_ path: String, method: String = "GET") async throws -> Response { try await request(path, method: method, body: Optional<String>.none) }
#if DEBUG
    func backdateQuestForResetProof(_ questID: Int) throws {
        let context = PersistenceController.shared.container.mainContext
        let record = try load(context)
        var data = try decoder.decode(LocalSnapshot.self, from: record.payload)
        guard let index = data.quests.firstIndex(where: { $0.id == questID }), let instance = data.quests[index].currentInstance else { throw LocalDataError.missing("Quest") }
        let yesterday = Calendar.current.date(byAdding: .day, value: -1, to: localDay(for: data.player))!
        data.quests[index] = data.quests[index].replacingInstance(.init(id: instance.id, progress: instance.progress, targetCount: instance.targetCount, status: "active", periodEnd: isoDay(yesterday), periodStart: isoDay(yesterday)))
        record.payload = try encoder.encode(data); record.modifiedAt = .now; try context.save()
    }
#endif
    private func load(_ context: ModelContext) throws -> SyncedSystemState {
        var descriptor = FetchDescriptor<SyncedSystemState>(sortBy: [SortDescriptor(\.modifiedAt, order: .reverse)]); descriptor.fetchLimit = 1
        if let found = try context.fetch(descriptor).first { return found }
        let value = SyncedSystemState(payload: try encoder.encode(LocalSnapshot.initial)); context.insert(value); try context.save(); return value
    }
    private func dictionary<T: Encodable>(_ value: T) throws -> [String: Any] { try JSONSerialization.jsonObject(with: encoder.encode(value)) as? [String: Any] ?? [:] }
}

private let maximumLevel = 999
private let statPointsPerLevel = 3

private struct LocalPeriod { let start: Date; let end: Date? }
private let dayFormatter: DateFormatter = { let value = DateFormatter(); value.calendar = Calendar(identifier: .gregorian); value.locale = Locale(identifier: "en_US_POSIX"); value.dateFormat = "yyyy-MM-dd"; return value }()
private func isoDay(_ date: Date) -> String { dayFormatter.string(from: date) }
private func parseDay(_ value: String?) -> Date? { value.flatMap(dayFormatter.date) }
private func localDay(for player: PlayerStatus) -> Date { var calendar = Calendar(identifier: .gregorian); calendar.timeZone = TimeZone(identifier: player.timezone) ?? .current; return calendar.startOfDay(for: .now) }

private func currentPeriod(for schedule: QuestSchedule, on day: Date) -> LocalPeriod? {
    var calendar = Calendar(identifier: .gregorian); calendar.timeZone = dayFormatter.timeZone ?? .current
    let legacyKind: String
    switch schedule.label {
    case "One time": legacyKind = "once"
    case "Selected days": legacyKind = "weekdays"
    case "Every N days": legacyKind = "interval"
    case "Weekly target": legacyKind = "weekly"
    default: legacyKind = "daily"
    }
    let kind = schedule.kind ?? legacyKind
    if kind == "once" { return .init(start: parseDay(schedule.anchor) ?? day, end: nil) }
    if kind == "daily" { return .init(start: day, end: day) }
    let weekday = (calendar.component(.weekday, from: day) + 5) % 7
    if kind == "weekdays" { return (schedule.days ?? []).contains(weekday) ? .init(start: day, end: day) : nil }
    if kind == "weekly" {
        let startDay = schedule.weekStart ?? 0, delta = (weekday - startDay + 7) % 7
        let start = calendar.date(byAdding: .day, value: -delta, to: day)!
        return .init(start: start, end: calendar.date(byAdding: .day, value: 6, to: start))
    }
    let anchor = parseDay(schedule.anchor) ?? day, length = max(1, schedule.intervalDays ?? 1)
    let elapsed = max(0, calendar.dateComponents([.day], from: anchor, to: day).day ?? 0)
    let start = calendar.date(byAdding: .day, value: (elapsed / length) * length, to: anchor)!
    return .init(start: start, end: calendar.date(byAdding: .day, value: length - 1, to: start))
}

private func runLocalDailyReset(_ data: inout LocalSnapshot, on today: Date) -> DailyReset {
    var failed = 0, spawned = 0, lost = 0
    if data.penalties == nil { data.penalties = [] }
    for index in data.quests.indices where data.quests[index].isActive {
        let quest = data.quests[index]
        if let instance = quest.currentInstance, instance.status == "active", let end = parseDay(instance.periodEnd), end < today {
            failed += 1
            let expLost = min(data.player.exp, quest.practiceMinutes)
            lost += expLost
            data.player = data.player.replacingExp(data.player.exp - expLost)
            data.penalties?.append(.init(questId: quest.id, instanceId: instance.id, reason: "Failed quest: \(quest.title)", expLost: expLost, createdAt: Date.now.ISO8601Format()))
            data.events.insert(.init(id: nextEventID(data.events), eventType: "penalty_applied", message: "Penalty incurred: Failed quest: \(quest.title) (-\(expLost) EXP)", createdAt: Date.now.ISO8601Format()), at: 0)
            data.events.insert(.init(id: nextEventID(data.events), eventType: "quest_failed", message: "Quest failed: \(quest.title) (\(instance.progress)/\(instance.targetCount))", createdAt: Date.now.ISO8601Format()), at: 0)
        }
        if let period = currentPeriod(for: quest.schedule, on: today), quest.schedule.kind != "once", quest.currentInstance?.periodStart != isoDay(period.start) {
            let nextID = (data.quests.compactMap(\.currentInstance?.id).max() ?? 0) + 1
            data.quests[index] = quest.replacingInstance(.init(id: nextID, progress: 0, targetCount: quest.targetCount, status: "active", periodEnd: period.end.map(isoDay), periodStart: isoDay(period.start)))
            spawned += 1
        }
    }
    if failed > 0 || spawned > 0 {
        data.events.insert(.init(id: nextEventID(data.events), eventType: "daily_reset", message: "Reset: \(failed) quest\(failed == 1 ? "" : "s") failed, \(spawned) quest\(spawned == 1 ? "" : "s") issued\(lost > 0 ? " (-\(lost) EXP)" : "").", createdAt: Date.now.ISO8601Format()), at: 0)
    }
    return .init(resetDate: isoDay(today), failedCount: failed, spawnedCount: spawned, totalExpLost: lost)
}

private func expThreshold(_ level: Int) -> Int {
    guard level < maximumLevel else { return 0 }
    return max(10, Int((100 * pow(Double(level), 1.5) / 10).rounded()) * 10)
}

private func awardProgress(level: Int, exp: Int, amount: Int) -> (level: Int, exp: Int, levelsGained: Int) {
    var level = level, exp = exp + amount, gained = 0
    while level < maximumLevel, exp >= expThreshold(level) {
        exp -= expThreshold(level); level += 1; gained += 1
    }
    return (level, level == maximumLevel ? 0 : exp, gained)
}

private func awardPlayer(_ player: PlayerStatus, amount: Int, statReward: String?, statRewardAmount: Int) -> (player: PlayerStatus, levelsGained: Int) {
    let progress = awardProgress(level: player.level, exp: player.exp, amount: amount)
    var strength = player.stats.strength, agility = player.stats.agility, vitality = player.stats.vitality, intelligence = player.stats.intelligence, perception = player.stats.perception
    switch statReward {
    case "strength": strength += statRewardAmount
    case "agility": agility += statRewardAmount
    case "vitality": vitality += statRewardAmount
    case "intelligence": intelligence += statRewardAmount
    case "perception": perception += statRewardAmount
    default: break
    }
    let threshold = expThreshold(progress.level)
    return (.init(id: player.id, name: player.name, level: progress.level, exp: progress.exp, expToNextLevel: threshold, expProgress: threshold == 0 ? 1 : Double(progress.exp) / Double(threshold), totalExpEarned: player.totalExpEarned + amount, statPoints: player.statPoints + progress.levelsGained * statPointsPerLevel, stats: .init(strength: strength, agility: agility, vitality: vitality, intelligence: intelligence, perception: perception), timezone: player.timezone), progress.levelsGained)
}

private func awardSkill(_ skill: SkillSummary, amount: Int) -> (skill: SkillSummary, levelsGained: Int) {
    let progress = awardProgress(level: skill.level, exp: skill.exp, amount: amount)
    let threshold = expThreshold(progress.level)
    return (.init(id: skill.id, parentId: skill.parentId, name: skill.name, description: skill.description, iconKey: skill.iconKey, level: progress.level, exp: progress.exp, expToNextLevel: threshold, expProgress: threshold == 0 ? 1 : Double(progress.exp) / Double(threshold), totalExpEarned: skill.totalExpEarned + amount, isActive: skill.isActive, depth: skill.depth, createdAt: skill.createdAt), progress.levelsGained)
}

private func awardSkillTree(_ nodes: inout [SkillNode], skillID: Int, amount: Int) -> [SkillAward] {
    guard var current = findSkill(skillID, nodes) else { return [] }
    var awards: [SkillAward] = [], distance = 0
    while true {
        let result = awardSkill(current, amount: amount)
        replaceSkill(result.skill, in: &nodes)
        awards.append(.init(skillId: current.id, name: current.name, expGained: amount, level: result.skill.level, levelsGained: result.levelsGained, leveledUp: result.levelsGained > 0, distance: distance))
        guard let parentID = current.parentId, let parent = findSkill(parentID, nodes) else { break }
        current = parent; distance += 1
    }
    return awards
}

private func appendSkillLevelEvents(_ awards: [SkillAward], events: inout [SystemEvent]) {
    for award in awards where award.leveledUp {
        events.insert(.init(id: nextEventID(events), eventType: "skill_level_up", message: "\(award.name) reached Lv. \(award.level).", createdAt: Date.now.ISO8601Format()), at: 0)
    }
}

private func nextEventID(_ events: [SystemEvent]) -> Int { (events.map(\.id).max() ?? 0) + 1 }
private func maxAttachmentID(_ practices: [Int: [PracticeEntry]]) -> Int { practices.values.flatMap { $0 }.flatMap(\.attachments).map(\.id).max() ?? 0 }
private func scheduleLabel(_ kind: String) -> String { switch kind { case "once": "One time"; case "daily": "Every day"; case "weekdays": "Selected days"; case "interval": "Every N days"; case "weekly": "Weekly target"; default: kind.capitalized } }
private func maxSkillID(_ nodes: [SkillNode]) -> Int { nodes.reduce(0) { max($0, $1.id, maxSkillID($1.children)) } }
private func findSkill(_ id: Int, _ nodes: [SkillNode]) -> SkillSummary? { for node in nodes { if node.id == id { return node.summary }; if let value = findSkill(id, node.children) { return value } }; return nil }
private func replaceSkill(_ skill: SkillSummary, in nodes: inout [SkillNode]) {
    for index in nodes.indices {
        if nodes[index].id == skill.id { nodes[index] = skill.node(children: nodes[index].children); return }
        var children = nodes[index].children
        replaceSkill(skill, in: &children)
        nodes[index] = nodes[index].replacingChildren(children)
    }
}
private func insertSkill(_ skill: SkillNode, under parentID: Int, in nodes: inout [SkillNode]) {
    for index in nodes.indices {
        if nodes[index].id == parentID { nodes[index] = nodes[index].replacingChildren(nodes[index].children + [skill]); return }
        var children = nodes[index].children
        insertSkill(skill, under: parentID, in: &children)
        nodes[index] = nodes[index].replacingChildren(children)
    }
}
private func skillPath(to id: Int, nodes: [SkillNode], path: [SkillSummary] = []) -> [SkillSummary]? {
    for node in nodes {
        if node.id == id { return path }
        if let found = skillPath(to: id, nodes: node.children, path: path + [node.summary]) { return found }
    }
    return nil
}
private func skillDetail(for skill: SkillSummary, in nodes: [SkillNode]) -> SkillDetail {
    let node = findSkillNode(skill.id, nodes)
    return .init(id: skill.id, parentId: skill.parentId, name: skill.name, description: skill.description, iconKey: skill.iconKey, level: skill.level, exp: skill.exp, expToNextLevel: skill.expToNextLevel, expProgress: skill.expProgress, totalExpEarned: skill.totalExpEarned, isActive: skill.isActive, depth: skill.depth, createdAt: skill.createdAt, path: skillPath(to: skill.id, nodes: nodes) ?? [], children: node?.children.map(\.summary) ?? [])
}
private func findSkillNode(_ id: Int, _ nodes: [SkillNode]) -> SkillNode? { for node in nodes { if node.id == id { return node }; if let value = findSkillNode(id, node.children) { return value } }; return nil }
private extension SkillSummary { func node(children: [SkillNode] = []) -> SkillNode { .init(id: id, parentId: parentId, name: name, description: description, iconKey: iconKey, level: level, exp: exp, expToNextLevel: expToNextLevel, expProgress: expProgress, totalExpEarned: totalExpEarned, isActive: isActive, depth: depth, createdAt: createdAt, children: children) } }
private extension SkillNode { func replacingChildren(_ children: [SkillNode]) -> SkillNode { .init(id: id, parentId: parentId, name: name, description: description, iconKey: iconKey, level: level, exp: exp, expToNextLevel: expToNextLevel, expProgress: expProgress, totalExpEarned: totalExpEarned, isActive: isActive, depth: depth, createdAt: createdAt, children: children) } }
private extension PlayerStatus {
    func replacingExp(_ value: Int) -> PlayerStatus {
        .init(id: id, name: name, level: level, exp: value, expToNextLevel: expToNextLevel, expProgress: expToNextLevel == 0 ? 1 : Double(value) / Double(expToNextLevel), totalExpEarned: totalExpEarned, statPoints: statPoints, stats: stats, timezone: timezone)
    }
}
private extension Quest {
    func replacingInstance(_ instance: QuestInstance?) -> Quest {
        .init(id: id, title: title, description: description, schedule: schedule, difficulty: difficulty, targetCount: targetCount, unit: unit, practiceMinutes: practiceMinutes, statReward: statReward, statRewardAmount: statRewardAmount, skillId: skillId, isActive: isActive, currentInstance: instance, nextDueDate: nextDueDate)
    }
    func replacingProgress(_ value: Int) -> Quest {
        replacingInstance(.init(id: currentInstance?.id ?? id, progress: value, targetCount: currentInstance?.targetCount ?? targetCount, status: value >= targetCount ? "completed" : "active", periodEnd: currentInstance?.periodEnd, periodStart: currentInstance?.periodStart))
    }
}
