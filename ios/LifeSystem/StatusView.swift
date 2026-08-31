import SwiftUI

struct StatusView: View {
    @State private var player: PlayerStatus?
    @State private var skills: [SkillNode] = []
    @State private var errorMessage: String?

    var body: some View {
        Group {
            if let player { PlayerStateContent(player: player, roots: skills) }
            else if let errorMessage { ContentUnavailableView("Status unavailable", systemImage: "wifi.exclamationmark", description: Text(errorMessage)) }
            else { ZStack { PlayerStateBackdrop(); ProgressView("Reading the runes…").tint(.orange) } }
        }
        .navigationTitle("Player State")
        .navigationBarTitleDisplayMode(.inline)
        .task { await load() }
    }

    private func load() async {
        do {
            async let playerRequest: PlayerStatus = LocalDataStore.shared.request("/players/me")
            async let skillsRequest: [SkillNode] = LocalDataStore.shared.request("/skills")
            player = try await playerRequest
            skills = try await skillsRequest
            errorMessage = nil
        } catch { errorMessage = error.localizedDescription }
    }
}

private struct PlayerStateContent: View {
    let player: PlayerStatus
    let roots: [SkillNode]
    @State private var showingAllAttributes = false

    private var skills: [SkillNode] {
        func flatten(_ nodes: [SkillNode]) -> [SkillNode] { nodes.flatMap { [$0] + flatten($0.children) } }
        return flatten(roots).sorted { $0.totalExpEarned > $1.totalExpEarned }
    }

    var body: some View {
        ZStack {
            PlayerStateBackdrop()
            ScrollView {
                VStack(spacing: 18) { title; identity; attributes; mastery }
                    .padding(.horizontal, 18).padding(.top, 14).padding(.bottom, 36)
            }
        }
        .sheet(isPresented: $showingAllAttributes) {
            ExpandedAttributesView(player: player)
        }
    }

    private var title: some View {
        VStack(spacing: 8) {
            HStack(spacing: 12) { OrnamentalRule(); Image(systemName: "flame.fill").foregroundStyle(SoulPalette.ember).shadow(color: SoulPalette.ember.opacity(0.8), radius: 9); OrnamentalRule() }
            Text("PLAYER STATE").font(.system(size: 13, weight: .semibold, design: .serif)).tracking(4).foregroundStyle(SoulPalette.parchment.opacity(0.82))
        }
    }

    private var identity: some View {
        SoulPanel {
            VStack(spacing: 17) {
                HStack(spacing: 16) {
                    ZStack {
                        Circle().stroke(SoulPalette.gold.opacity(0.35), lineWidth: 1)
                        Circle().stroke(SoulPalette.ember.opacity(0.25), lineWidth: 7).padding(6)
                        Image(systemName: "figure.martial.arts").font(.system(size: 35, weight: .light)).foregroundStyle(SoulPalette.parchment)
                    }.frame(width: 82, height: 82)
                    VStack(alignment: .leading, spacing: 5) {
                        Text(player.name.uppercased()).font(.system(size: 23, weight: .semibold, design: .serif)).tracking(1.5).foregroundStyle(SoulPalette.parchment)
                        Text("BEARER OF THE SYSTEM").font(.system(size: 9, weight: .bold, design: .serif)).tracking(2).foregroundStyle(SoulPalette.gold)
                        Text(player.timezone).font(.caption2.monospaced()).foregroundStyle(.white.opacity(0.42))
                    }
                    Spacer()
                    VStack(spacing: 0) {
                        Text("LEVEL").font(.system(size: 9, weight: .bold, design: .serif)).tracking(1.5).foregroundStyle(SoulPalette.gold)
                        Text("\(player.level)").font(.system(size: 34, weight: .light, design: .serif)).foregroundStyle(SoulPalette.parchment)
                    }
                }
                VStack(spacing: 7) {
                    HStack { Text("SOUL EXPERIENCE"); Spacer(); Text("\(player.exp) / \(player.expToNextLevel)") }
                        .font(.system(size: 10, weight: .semibold, design: .serif)).tracking(1).foregroundStyle(SoulPalette.parchment.opacity(0.7))
                    SoulProgress(value: player.expProgress, color: SoulPalette.ember)
                }
                HStack {
                    soulMetric("TOTAL EXP", player.totalExpEarned); Divider().overlay(SoulPalette.gold.opacity(0.25))
                    soulMetric("UNSPENT", player.statPoints); Divider().overlay(SoulPalette.gold.opacity(0.25))
                    soulMetric("SKILLS", skills.count)
                }.frame(height: 42)
            }
        }
    }

    private var attributes: some View {
        SoulPanel(title: "ATTRIBUTES") {
            VStack(spacing: 0) {
                ForEach(Array(player.stats.rows.enumerated()), id: \.element.0) { index, stat in
                    HStack(spacing: 12) {
                        Image(systemName: stat.2).font(.caption).foregroundStyle(SoulPalette.gold).frame(width: 24)
                        Text(stat.0.uppercased()).font(.system(size: 12, weight: .medium, design: .serif)).tracking(1.2)
                        Spacer()
                        Text("\(stat.1)").font(.system(size: 18, weight: .medium, design: .serif).monospacedDigit()).foregroundStyle(SoulPalette.parchment)
                    }.padding(.vertical, 10)
                    if index < player.stats.rows.count - 1 { Rectangle().fill(SoulPalette.gold.opacity(0.13)).frame(height: 1) }
                }
                Button { showingAllAttributes = true } label: {
                    HStack {
                        Text("SEE ALL 100 ATTRIBUTES")
                        Spacer()
                        Image(systemName: "chevron.right")
                    }
                    .font(.system(size: 10, weight: .bold, design: .serif))
                    .tracking(1.4)
                    .foregroundStyle(SoulPalette.gold)
                    .padding(.top, 15)
                }
                .buttonStyle(.plain)
            }
        }
    }

    private var mastery: some View {
        SoulPanel(title: "SKILL MASTERY") {
            VStack(spacing: 14) {
                if skills.isEmpty {
                    Text("No disciplines have yet been awakened.").font(.system(.subheadline, design: .serif)).foregroundStyle(.white.opacity(0.5)).frame(maxWidth: .infinity, alignment: .leading)
                } else {
                    ForEach(skills) { skill in
                        NavigationLink { SkillDetailView(skillID: skill.id, initial: skill.summary) } label: { SkillMasteryRow(skill: skill) }.buttonStyle(.plain)
                    }
                }
            }
        }
    }

    private func soulMetric(_ label: String, _ value: Int) -> some View {
        VStack(spacing: 3) {
            Text("\(value)").font(.system(size: 17, weight: .medium, design: .serif).monospacedDigit()).foregroundStyle(SoulPalette.parchment)
            Text(label).font(.system(size: 8, weight: .bold, design: .serif)).tracking(1).foregroundStyle(.white.opacity(0.42))
        }.frame(maxWidth: .infinity)
    }
}

private struct HumanAttribute: Identifiable {
    let id: Int
    let domain: String
    let name: String
    let icon: String
}

private let humanAttributeCatalog: [HumanAttribute] = {
    let domains: [(String, String, [String])] = [
        ("PHYSICAL", "figure.run", ["Power", "Speed", "Endurance", "Mobility", "Balance", "Coordination", "Dexterity", "Recovery", "Stamina", "Body Awareness"]),
        ("COGNITIVE", "brain.head.profile", ["Reasoning", "Memory", "Focus", "Learning", "Numeracy", "Language", "Planning", "Problem Solving", "Mental Agility", "Wisdom"]),
        ("EMOTIONAL", "heart.fill", ["Self Awareness", "Self Control", "Empathy", "Optimism", "Patience", "Composure", "Emotional Range", "Compassion", "Gratitude", "Inner Calm"]),
        ("SOCIAL", "person.2.fill", ["Communication", "Listening", "Leadership", "Cooperation", "Persuasion", "Humour", "Warmth", "Trust Building", "Conflict Resolution", "Presence"]),
        ("CREATIVE", "paintbrush.fill", ["Imagination", "Originality", "Curiosity", "Storytelling", "Visual Sense", "Musicality", "Improvisation", "Experimentation", "Expression", "Taste"]),
        ("PRACTICAL", "hammer.fill", ["Organisation", "Time Management", "Resourcefulness", "Financial Sense", "Technical Skill", "Craftsmanship", "Decision Making", "Risk Assessment", "Navigation", "Preparedness"]),
        ("DISCIPLINE", "shield.fill", ["Consistency", "Willpower", "Habit Strength", "Punctuality", "Attention to Detail", "Follow Through", "Restraint", "Work Ethic", "Accountability", "Purpose"]),
        ("PERCEPTION", "eye.fill", ["Observation", "Spatial Sense", "Pattern Recognition", "Situational Awareness", "Intuition", "Aesthetic Sensitivity", "Reading People", "Foresight", "Sound Awareness", "Precision"]),
        ("RESILIENCE", "flame.fill", ["Courage", "Adaptability", "Stress Tolerance", "Persistence", "Pain Tolerance", "Recovery Mindset", "Independence", "Decisiveness", "Confidence", "Fortitude"]),
        ("CHARACTER", "crown.fill", ["Integrity", "Kindness", "Humility", "Loyalty", "Fairness", "Generosity", "Responsibility", "Authenticity", "Respect", "Honor"]),
    ]
    return domains.enumerated().flatMap { domainIndex, domain in
        domain.2.enumerated().map { traitIndex, name in
            HumanAttribute(id: domainIndex * 10 + traitIndex, domain: domain.0, name: name, icon: domain.1)
        }
    }
}()

private struct ExpandedAttributesView: View {
    @Environment(\.dismiss) private var dismiss
    let player: PlayerStatus
    var initialIndex: Int? = nil

    var body: some View {
        NavigationStack {
            ZStack {
                PlayerStateBackdrop()
                ScrollViewReader { proxy in
                    ScrollView {
                        VStack(spacing: 18) {
                            summary
                            ForEach(groupedCatalog, id: \.domain) { group in
                                attributeDomain(group.domain, attributes: group.attributes)
                            }
                        }
                        .padding(18)
                    }
                    .onAppear {
                        if let initialIndex {
                            DispatchQueue.main.async { proxy.scrollTo(initialIndex, anchor: .top) }
                        }
                    }
                }
            }
            .navigationTitle("Attributes")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }.foregroundStyle(SoulPalette.gold)
                }
            }
        }
        .preferredColorScheme(.dark)
    }

    private var groupedCatalog: [(domain: String, attributes: [HumanAttribute])] {
        var result: [(String, [HumanAttribute])] = []
        for attribute in humanAttributeCatalog {
            if result.last?.0 == attribute.domain { result[result.count - 1].1.append(attribute) }
            else { result.append((attribute.domain, [attribute])) }
        }
        return result
    }

    private var summary: some View {
        VStack(spacing: 8) {
            Image(systemName: "crown.fill").font(.title2).foregroundStyle(SoulPalette.gold)
            Text("THE HUNDRED FACETS").font(.system(size: 18, weight: .semibold, design: .serif)).tracking(2).foregroundStyle(SoulPalette.parchment)
            Text("A broad reflection of personality, character, and human ability.")
                .font(.system(.caption, design: .serif)).foregroundStyle(.white.opacity(0.5)).multilineTextAlignment(.center)
        }.frame(maxWidth: .infinity).padding(.vertical, 8)
    }

    private func attributeDomain(_ domain: String, attributes: [HumanAttribute]) -> some View {
        SoulPanel(title: domain) {
            VStack(spacing: 0) {
                ForEach(attributes) { attribute in
                    HStack(spacing: 11) {
                        Image(systemName: attribute.icon).font(.caption2).foregroundStyle(SoulPalette.gold).frame(width: 20)
                        Text(attribute.name.uppercased()).font(.system(size: 11, weight: .medium, design: .serif)).tracking(0.8)
                        Spacer()
                        Text("\(score(for: attribute))").font(.system(size: 16, weight: .medium, design: .serif).monospacedDigit()).foregroundStyle(SoulPalette.parchment)
                    }
                    .padding(.vertical, 9)
                    .id(attribute.id)
                    if attribute.id != attributes.last?.id { Rectangle().fill(SoulPalette.gold.opacity(0.11)).frame(height: 1) }
                }
            }
        }
    }

    private func score(for attribute: HumanAttribute) -> Int {
        let foundations = [player.stats.strength, player.stats.agility, player.stats.vitality, player.stats.intelligence, player.stats.perception]
        let primary = foundations[attribute.id % foundations.count]
        let secondary = foundations[(attribute.id * 3 + 1) % foundations.count]
        return min(99, max(1, primary * 2 + secondary + (attribute.id * 7 % 13)))
    }
}

private struct SkillMasteryRow: View {
    let skill: SkillNode
    var body: some View {
        HStack(spacing: 12) {
            ZStack {
                Diamond().stroke(SoulPalette.gold.opacity(0.45), lineWidth: 1)
                SkillIcon(key: skill.iconKey, fallback: SkillIconCatalog.fallback(for: skill.name)).foregroundStyle(skill.children.isEmpty ? SoulPalette.parchment : SoulPalette.ember).padding(9)
            }.frame(width: 34, height: 34)
            VStack(alignment: .leading, spacing: 7) {
                HStack {
                    Text(skill.name.uppercased()).font(.system(size: 12, weight: .semibold, design: .serif)).tracking(0.8).lineLimit(1)
                    Spacer(); Text("LV \(skill.level)").font(.caption2.bold().monospaced()).foregroundStyle(SoulPalette.gold)
                }
                SoulProgress(value: skill.expProgress, color: SoulPalette.gold)
                HStack { Text("\(skill.exp) / \(skill.expToNextLevel) EXP"); Spacer(); Text("\(skill.totalExpEarned) MASTERED") }
                    .font(.system(size: 8, weight: .medium).monospaced()).foregroundStyle(.white.opacity(0.4))
            }
            Image(systemName: "chevron.right").font(.caption2).foregroundStyle(SoulPalette.gold.opacity(0.55))
        }
    }
}

private struct SoulPanel<Content: View>: View {
    var title: String?
    let content: Content
    init(title: String? = nil, @ViewBuilder content: () -> Content) { self.title = title; self.content = content() }
    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            if let title { HStack(spacing: 10) { Text(title).font(.system(size: 11, weight: .bold, design: .serif)).tracking(2.4).foregroundStyle(SoulPalette.gold); Rectangle().fill(SoulPalette.gold.opacity(0.25)).frame(height: 1) } }
            content
        }
        .padding(17).background(Color.black.opacity(0.38))
        .overlay { Rectangle().stroke(SoulPalette.gold.opacity(0.27), lineWidth: 1) }
        .overlay(alignment: .topLeading) { CornerRune().stroke(SoulPalette.gold.opacity(0.65), lineWidth: 1).frame(width: 24, height: 24) }
        .overlay(alignment: .bottomTrailing) { CornerRune().stroke(SoulPalette.gold.opacity(0.65), lineWidth: 1).frame(width: 24, height: 24).rotationEffect(.degrees(180)) }
    }
}

private struct SoulProgress: View {
    let value: Double; let color: Color
    var body: some View {
        GeometryReader { geometry in
            ZStack(alignment: .leading) {
                Rectangle().fill(Color.black.opacity(0.65))
                Rectangle().fill(LinearGradient(colors: [color.opacity(0.55), color], startPoint: .leading, endPoint: .trailing)).frame(width: geometry.size.width * min(max(value, 0), 1))
                Rectangle().stroke(SoulPalette.parchment.opacity(0.18), lineWidth: 1)
            }
        }.frame(height: 6)
    }
}

private struct PlayerStateBackdrop: View {
    var body: some View {
        ZStack {
            LinearGradient(colors: [Color(red: 0.08, green: 0.075, blue: 0.065), Color(red: 0.018, green: 0.018, blue: 0.02)], startPoint: .top, endPoint: .bottom)
            RadialGradient(colors: [SoulPalette.ember.opacity(0.12), .clear], center: .top, startRadius: 0, endRadius: 330)
        }.ignoresSafeArea()
    }
}

private struct OrnamentalRule: View {
    var body: some View { HStack(spacing: 0) { Rectangle().fill(SoulPalette.gold.opacity(0.08)).frame(height: 1); Diamond().fill(SoulPalette.gold.opacity(0.55)).frame(width: 7, height: 7); Rectangle().fill(SoulPalette.gold.opacity(0.35)).frame(height: 1) } }
}

private struct Diamond: Shape {
    func path(in rect: CGRect) -> Path { Path { p in p.move(to: CGPoint(x: rect.midX, y: rect.minY)); p.addLine(to: CGPoint(x: rect.maxX, y: rect.midY)); p.addLine(to: CGPoint(x: rect.midX, y: rect.maxY)); p.addLine(to: CGPoint(x: rect.minX, y: rect.midY)); p.closeSubpath() } }
}

private struct CornerRune: Shape {
    func path(in rect: CGRect) -> Path { Path { p in p.move(to: CGPoint(x: rect.minX, y: rect.maxY)); p.addLine(to: CGPoint(x: rect.minX, y: rect.minY)); p.addLine(to: CGPoint(x: rect.maxX, y: rect.minY)); p.move(to: CGPoint(x: rect.minX + 5, y: rect.minY + 12)); p.addLine(to: CGPoint(x: rect.minX + 5, y: rect.minY + 5)); p.addLine(to: CGPoint(x: rect.minX + 12, y: rect.minY + 5)) } }
}

private enum SoulPalette {
    static let parchment = Color(red: 0.88, green: 0.85, blue: 0.75)
    static let gold = Color(red: 0.72, green: 0.58, blue: 0.30)
    static let ember = Color(red: 0.78, green: 0.23, blue: 0.10)
}

struct PlayerStatePreviewScreen: View {
    private let player = PlayerStatus(id: 1, name: "Ashen Wanderer", level: 27, exp: 1840, expToNextLevel: 2500, expProgress: 0.736, totalExpEarned: 18_640, statPoints: 3, stats: StatBlock(strength: 24, agility: 19, vitality: 22, intelligence: 16, perception: 18), timezone: "Europe/London")
    private let skills: [SkillNode] = [
        SkillNode(id: 1, parentId: nil, name: "Strength Training", description: nil, level: 12, exp: 680, expToNextLevel: 1000, expProgress: 0.68, totalExpEarned: 5820, isActive: true, depth: 1, createdAt: "", children: []),
        SkillNode(id: 2, parentId: nil, name: "Swift Programming", description: nil, level: 9, exp: 410, expToNextLevel: 800, expProgress: 0.5125, totalExpEarned: 3940, isActive: true, depth: 1, createdAt: "", children: []),
        SkillNode(id: 3, parentId: nil, name: "Piano", description: nil, level: 7, exp: 190, expToNextLevel: 600, expProgress: 0.316, totalExpEarned: 2610, isActive: true, depth: 1, createdAt: "", children: [])
    ]
    var body: some View { NavigationStack { PlayerStateContent(player: player, roots: skills).toolbar(.hidden, for: .navigationBar) }.preferredColorScheme(.dark) }
}

struct PlayerAttributesPreviewScreen: View {
    private let player = PlayerStatus(id: 1, name: "Ashen Wanderer", level: 27, exp: 1840, expToNextLevel: 2500, expProgress: 0.736, totalExpEarned: 18_640, statPoints: 3, stats: StatBlock(strength: 24, agility: 19, vitality: 22, intelligence: 16, perception: 18), timezone: "Europe/London")
    var body: some View { ExpandedAttributesView(player: player, initialIndex: 70) }
}

#Preview("Player State") { PlayerStatePreviewScreen() }
#Preview("Player Attributes — scrolled") { PlayerAttributesPreviewScreen() }
