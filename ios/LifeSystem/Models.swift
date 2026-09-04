import Foundation

struct QuoteSummary: Codable {
    let id: Int
    let text: String
    let author: String?
}

struct SkillSummary: Codable, Identifiable {
    let id: Int
    let parentId: Int?
    let name: String
    let description: String?
    var iconKey: String? = nil
    let level: Int
    let exp: Int
    let expToNextLevel: Int
    let expProgress: Double
    let totalExpEarned: Int
    let isActive: Bool
    let depth: Int
    let createdAt: String
}

struct SkillNode: Codable, Identifiable {
    let id: Int
    let parentId: Int?
    let name: String
    let description: String?
    var iconKey: String? = nil
    let level: Int
    let exp: Int
    let expToNextLevel: Int
    let expProgress: Double
    let totalExpEarned: Int
    let isActive: Bool
    let depth: Int
    let createdAt: String
    let children: [SkillNode]

    var summary: SkillSummary {
        SkillSummary(id: id, parentId: parentId, name: name, description: description, iconKey: iconKey, level: level, exp: exp, expToNextLevel: expToNextLevel, expProgress: expProgress, totalExpEarned: totalExpEarned, isActive: isActive, depth: depth, createdAt: createdAt)
    }
}

struct SkillDetail: Codable, Identifiable {
    let id: Int
    let parentId: Int?
    let name: String
    let description: String?
    var iconKey: String? = nil
    let level: Int
    let exp: Int
    let expToNextLevel: Int
    let expProgress: Double
    let totalExpEarned: Int
    let isActive: Bool
    let depth: Int
    let createdAt: String
    let path: [SkillSummary]
    let children: [SkillSummary]

    var summary: SkillSummary {
        SkillSummary(id: id, parentId: parentId, name: name, description: description, iconKey: iconKey, level: level, exp: exp, expToNextLevel: expToNextLevel, expProgress: expProgress, totalExpEarned: totalExpEarned, isActive: isActive, depth: depth, createdAt: createdAt)
    }
}

struct SkillAward: Codable, Identifiable {
    let skillId: Int
    let name: String
    let expGained: Int
    let level: Int
    let levelsGained: Int
    let leveledUp: Bool
    let distance: Int
    var id: Int { skillId }
}

struct PracticeResult: Codable {
    let skill: SkillSummary
    let awards: [SkillAward]
    let entry: PracticeEntry
}

struct PracticeAttachment: Codable, Identifiable {
    let id: Int
    let kind: String
    let filename: String
    let contentType: String
    let byteCount: Int
}

struct PracticeEntry: Codable, Identifiable {
    let id: Int
    let skillId: Int
    let skillName: String
    let minutes: Int
    let note: String?
    let createdAt: String
    let attachments: [PracticeAttachment]
}

struct DailyQuote: Codable {
    let localDate: String
    let quote: QuoteSummary?
    let poolSize: Int
    let refreshAfter: String
}

struct PlayerStatus: Codable {
    let id: Int
    let name: String
    let level: Int
    let exp: Int
    let expToNextLevel: Int
    let expProgress: Double
    let totalExpEarned: Int
    let statPoints: Int
    let stats: StatBlock
    let timezone: String
}

struct StatBlock: Codable {
    let strength, agility, vitality, intelligence, perception: Int

    var rows: [(String, Int, String)] {
        [("Strength", strength, "figure.strengthtraining.traditional"),
         ("Agility", agility, "figure.run"),
         ("Vitality", vitality, "heart.fill"),
         ("Intelligence", intelligence, "brain.head.profile"),
         ("Perception", perception, "eye.fill")]
    }
}

struct Quest: Codable, Identifiable {
    let id: Int
    let title: String
    let description: String?
    let schedule: QuestSchedule
    let difficulty: String
    let targetCount: Int
    let unit: String?
    let practiceMinutes: Int
    let statReward: String?
    let statRewardAmount: Int
    let skillId: Int?
    let isActive: Bool
    let currentInstance: QuestInstance?
    let nextDueDate: String?

    init(id: Int, title: String, description: String?, schedule: QuestSchedule, difficulty: String, targetCount: Int, unit: String?, practiceMinutes: Int, statReward: String?, statRewardAmount: Int, skillId: Int? = nil, isActive: Bool, currentInstance: QuestInstance?, nextDueDate: String?) {
        self.id = id
        self.title = title
        self.description = description
        self.schedule = schedule
        self.difficulty = difficulty
        self.targetCount = targetCount
        self.unit = unit
        self.practiceMinutes = practiceMinutes
        self.statReward = statReward
        self.statRewardAmount = statRewardAmount
        self.skillId = skillId
        self.isActive = isActive
        self.currentInstance = currentInstance
        self.nextDueDate = nextDueDate
    }
}

struct QuestSchedule: Codable {
    let label: String
    let kind: String?
    let days: [Int]?
    let intervalDays: Int?
    let anchor: String?
    let weekStart: Int?

    init(label: String, kind: String? = nil, days: [Int]? = nil, intervalDays: Int? = nil, anchor: String? = nil, weekStart: Int? = nil) {
        self.label = label
        self.kind = kind
        self.days = days
        self.intervalDays = intervalDays
        self.anchor = anchor
        self.weekStart = weekStart
    }
}

struct QuestInstance: Codable {
    let id: Int
    let progress: Int
    let targetCount: Int
    let status: String
    let periodEnd: String?
    let periodStart: String?

    init(id: Int, progress: Int, targetCount: Int, status: String, periodEnd: String?, periodStart: String? = nil) {
        self.id = id
        self.progress = progress
        self.targetCount = targetCount
        self.status = status
        self.periodEnd = periodEnd
        self.periodStart = periodStart
    }
}

struct QuestAction: Codable {
    let completed: Bool
    let expGained: Int
    let leveledUp: Bool
}

struct DailyReset: Codable {
    let resetDate: String
    let failedCount, spawnedCount, totalExpLost: Int
}

struct SystemEvent: Codable, Identifiable {
    let id: Int
    let eventType: String
    let message: String
    let createdAt: String
}
