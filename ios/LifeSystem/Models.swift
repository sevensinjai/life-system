import Foundation

struct TokenResponse: Decodable { let accessToken: String }

struct QuoteSummary: Codable {
    let id: Int
    let text: String
    let author: String?
}

struct SkillSummary: Decodable, Identifiable {
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

struct SkillNode: Decodable, Identifiable {
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

struct SkillDetail: Decodable, Identifiable {
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

struct SkillAward: Decodable, Identifiable {
    let skillId: Int
    let name: String
    let expGained: Int
    let level: Int
    let levelsGained: Int
    let leveledUp: Bool
    let distance: Int
    var id: Int { skillId }
}

struct PracticeResult: Decodable {
    let skill: SkillSummary
    let awards: [SkillAward]
    let entry: PracticeEntry
}

struct PracticeAttachment: Decodable, Identifiable {
    let id: Int
    let kind: String
    let filename: String
    let contentType: String
    let byteCount: Int
}

struct PracticeEntry: Decodable, Identifiable {
    let id: Int
    let skillId: Int
    let skillName: String
    let minutes: Int
    let note: String?
    let createdAt: String
    let attachments: [PracticeAttachment]
}

struct DailyQuote: Decodable {
    let localDate: String
    let quote: QuoteSummary?
    let poolSize: Int
    let refreshAfter: String
}

struct PlayerStatus: Decodable {
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

struct StatBlock: Decodable {
    let strength, agility, vitality, intelligence, perception: Int

    var rows: [(String, Int, String)] {
        [("Strength", strength, "figure.strengthtraining.traditional"),
         ("Agility", agility, "figure.run"),
         ("Vitality", vitality, "heart.fill"),
         ("Intelligence", intelligence, "brain.head.profile"),
         ("Perception", perception, "eye.fill")]
    }
}

struct Quest: Decodable, Identifiable {
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
    let isActive: Bool
    let currentInstance: QuestInstance?
    let nextDueDate: String?
}

struct QuestSchedule: Decodable { let label: String }

struct QuestInstance: Decodable {
    let id: Int
    let progress: Int
    let targetCount: Int
    let status: String
    let periodEnd: String?
}

struct QuestAction: Decodable {
    let completed: Bool
    let expGained: Int
    let leveledUp: Bool
}

struct DailyReset: Decodable {
    let resetDate: String
    let failedCount, spawnedCount, totalExpLost: Int
}

struct SystemEvent: Decodable, Identifiable {
    let id: Int
    let eventType: String
    let message: String
    let createdAt: String
}

struct APIErrorEnvelope: Decodable {
    struct Detail: Decodable { let message: String }
    let error: Detail
}
