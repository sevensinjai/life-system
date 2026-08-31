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

    static var initial: Self {
        .init(player: .init(id: 1, name: "Player", level: 1, exp: 0, expToNextLevel: 100, expProgress: 0, totalExpEarned: 0, statPoints: 0, stats: .init(strength: 1, agility: 1, vitality: 1, intelligence: 1, perception: 1), timezone: TimeZone.current.identifier), quests: [], skills: [], practices: [:], events: [], quote: .init(localDate: Date.now.formatted(.iso8601.year().month().day()), quote: .init(id: 1, text: "Small steps, repeated, become a life.", author: "The System"), poolSize: 1, refreshAfter: Calendar.current.date(byAdding: .day, value: 1, to: .now)!.ISO8601Format()))
    }
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
        case ("GET", "/quests"), ("GET", "/quests/today"): result = path.hasSuffix("today") ? data.quests.filter(\.isActive) : data.quests
        case ("POST", "/quests"):
            let id = (data.quests.map(\.id).max() ?? 0) + 1
            let target = fields["target_count"] as? Int ?? 1
            let schedule = (fields["schedule"] as? [String: Any])?["kind"] as? String ?? "daily"
            let quest = Quest(id: id, title: fields["title"] as? String ?? "Untitled quest", description: fields["description"] as? String, schedule: .init(label: schedule.capitalized), difficulty: fields["difficulty"] as? String ?? "E", targetCount: target, unit: fields["unit"] as? String, practiceMinutes: fields["practice_minutes"] as? Int ?? 10, statReward: fields["stat_reward"] as? String, statRewardAmount: fields["stat_reward_amount"] as? Int ?? 0, isActive: true, currentInstance: .init(id: id, progress: 0, targetCount: target, status: "active", periodEnd: "Today"), nextDueDate: nil)
            data.quests.append(quest); result = quest
        case ("POST", let value) where value.hasSuffix("/progress") || value.hasSuffix("/complete"):
            guard let id = Int(value.split(separator: "/")[1]), let index = data.quests.firstIndex(where: { $0.id == id }) else { throw LocalDataError.missing("Quest") }
            let old = data.quests[index], target = old.currentInstance?.targetCount ?? old.targetCount
            let progress = value.hasSuffix("/complete") ? target : min((old.currentInstance?.progress ?? 0) + (fields["amount"] as? Int ?? 1), target)
            data.quests[index] = old.replacingProgress(progress)
            let completed = progress >= target
            result = QuestAction(completed: completed, expGained: completed ? old.practiceMinutes : 0, leveledUp: false)
            if completed { data.events.insert(.init(id: (data.events.map(\.id).max() ?? 0) + 1, eventType: "quest_completed", message: "Completed \(old.title).", createdAt: Date.now.ISO8601Format()), at: 0) }
        case ("GET", "/skills"): result = data.skills
        case ("POST", "/skills"):
            let id = maxSkillID(data.skills) + 1
            let skill = SkillSummary(id: id, parentId: fields["parent_id"] as? Int, name: fields["name"] as? String ?? "New skill", description: fields["description"] as? String, iconKey: fields["icon_key"] as? String, level: 1, exp: 0, expToNextLevel: 100, expProgress: 0, totalExpEarned: 0, isActive: true, depth: 0, createdAt: Date.now.ISO8601Format())
            data.skills.append(skill.node); result = skill
        case ("GET", let value) where value.hasSuffix("/practice"):
            let id = Int(value.split(separator: "/")[1]) ?? 0; result = data.practices[id] ?? []
        case ("POST", let value) where value.hasSuffix("/practice"):
            let id = Int(value.split(separator: "/")[1]) ?? 0
            guard let skill = findSkill(id, data.skills) else { throw LocalDataError.missing("Skill") }
            let minutes = fields["minutes"] as? Int ?? 1
            let entry = PracticeEntry(id: (data.practices.values.flatMap { $0 }.map(\.id).max() ?? 0) + 1, skillId: id, skillName: skill.name, minutes: minutes, note: fields["note"] as? String, createdAt: Date.now.ISO8601Format(), attachments: [])
            data.practices[id, default: []].insert(entry, at: 0)
            result = PracticeResult(skill: skill, awards: [.init(skillId: id, name: skill.name, expGained: minutes, level: skill.level, levelsGained: 0, leveledUp: false, distance: 0)], entry: entry)
        case ("GET", let value) where value.hasPrefix("/skills/"):
            let id = Int(value.split(separator: "/")[1]) ?? 0
            guard let skill = findSkill(id, data.skills) else { throw LocalDataError.missing("Skill") }; result = SkillDetail(from: skill)
        case ("PATCH", let value) where value.hasPrefix("/skills/"):
            let id = Int(value.split(separator: "/")[1]) ?? 0
            guard var skill = findSkill(id, data.skills) else { throw LocalDataError.missing("Skill") }
            skill.iconKey = fields["icon_key"] as? String; replaceSkill(skill, in: &data.skills); result = skill
        case ("GET", "/quotes/today"): result = data.quote
        case ("GET", "/system/events"): result = data.events
        case ("POST", "/system/daily-reset"): result = DailyReset(resetDate: Date.now.formatted(.iso8601.year().month().day()), failedCount: 0, spawnedCount: 0, totalExpLost: 0)
        default: throw LocalDataError.unsupported("\(method) \(path)")
        }
        if method != "GET" { record.payload = try encoder.encode(data); record.modifiedAt = .now; try context.save() }
        return try decoder.decode(Response.self, from: try encoder.encode(result))
    }

    func request<Response: Decodable>(_ path: String, method: String = "GET") async throws -> Response { try await request(path, method: method, body: Optional<String>.none) }
    private func load(_ context: ModelContext) throws -> SyncedSystemState {
        var descriptor = FetchDescriptor<SyncedSystemState>(sortBy: [SortDescriptor(\.modifiedAt, order: .reverse)]); descriptor.fetchLimit = 1
        if let found = try context.fetch(descriptor).first { return found }
        let value = SyncedSystemState(payload: try encoder.encode(LocalSnapshot.initial)); context.insert(value); try context.save(); return value
    }
    private func dictionary<T: Encodable>(_ value: T) throws -> [String: Any] { try JSONSerialization.jsonObject(with: encoder.encode(value)) as? [String: Any] ?? [:] }
}

private func maxSkillID(_ nodes: [SkillNode]) -> Int { nodes.reduce(0) { max($0, $1.id, maxSkillID($1.children)) } }
private func findSkill(_ id: Int, _ nodes: [SkillNode]) -> SkillSummary? { for node in nodes { if node.id == id { return node.summary }; if let value = findSkill(id, node.children) { return value } }; return nil }
private func replaceSkill(_ skill: SkillSummary, in nodes: inout [SkillNode]) { for index in nodes.indices { if nodes[index].id == skill.id { nodes[index] = skill.node; return }; var children = nodes[index].children; replaceSkill(skill, in: &children) } }
private extension SkillSummary { var node: SkillNode { .init(id: id, parentId: parentId, name: name, description: description, iconKey: iconKey, level: level, exp: exp, expToNextLevel: expToNextLevel, expProgress: expProgress, totalExpEarned: totalExpEarned, isActive: isActive, depth: depth, createdAt: createdAt, children: []) } }
private extension SkillDetail { init(from value: SkillSummary) { self.init(id: value.id, parentId: value.parentId, name: value.name, description: value.description, iconKey: value.iconKey, level: value.level, exp: value.exp, expToNextLevel: value.expToNextLevel, expProgress: value.expProgress, totalExpEarned: value.totalExpEarned, isActive: value.isActive, depth: value.depth, createdAt: value.createdAt, path: [], children: []) } }
private extension Quest { func replacingProgress(_ value: Int) -> Quest { .init(id: id, title: title, description: description, schedule: schedule, difficulty: difficulty, targetCount: targetCount, unit: unit, practiceMinutes: practiceMinutes, statReward: statReward, statRewardAmount: statRewardAmount, isActive: isActive, currentInstance: .init(id: currentInstance?.id ?? id, progress: value, targetCount: currentInstance?.targetCount ?? targetCount, status: value >= targetCount ? "completed" : "active", periodEnd: currentInstance?.periodEnd), nextDueDate: nextDueDate) } }
