import SwiftUI

struct SkillIconOption: Identifiable, Hashable {
    let key: String
    let title: String
    let category: String
    let author: String
    var id: String { key }
}

enum SkillIconCatalog {
    static let options: [SkillIconOption] = [
        SkillIconOption(key: "game-lorc-run", title: "Run", category: "Fitness", author: "lorc"),
        SkillIconOption(key: "game-badges-body", title: "Body", category: "Fitness", author: "badges"),
        SkillIconOption(key: "game-badges-heart", title: "Heart", category: "Fitness", author: "badges"),
        SkillIconOption(key: "game-skoll-hearts", title: "Hearts", category: "Fitness", author: "skoll"),
        SkillIconOption(key: "game-lorc-sprint", title: "Sprint", category: "Fitness", author: "lorc"),
        SkillIconOption(key: "game-delapouite-weight", title: "Weight", category: "Fitness", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-cycling", title: "Cycling", category: "Fitness", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-gym-bag", title: "Gym Bag", category: "Fitness", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-antibody", title: "Antibody", category: "Fitness", author: "delapouite"),
        SkillIconOption(key: "game-lorc-barefoot", title: "Barefoot", category: "Fitness", author: "lorc"),
        SkillIconOption(key: "game-delapouite-passport", title: "Passport", category: "Fitness", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-swimfins", title: "Swimfins", category: "Fitness", author: "delapouite"),
        SkillIconOption(key: "game-lorc-wingfoot", title: "Wingfoot", category: "Fitness", author: "lorc"),
        SkillIconOption(key: "game-lorc-foot-trip", title: "Foot Trip", category: "Fitness", author: "lorc"),
        SkillIconOption(key: "game-lorc-footprint", title: "Footprint", category: "Fitness", author: "lorc"),
        SkillIconOption(key: "game-delapouite-drum", title: "Drum", category: "Music", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-harp", title: "Harp", category: "Music", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-pear", title: "Pear", category: "Music", author: "delapouite"),
        SkillIconOption(key: "game-lorc-sing", title: "Sing", category: "Music", author: "lorc"),
        SkillIconOption(key: "game-lorc-beard", title: "Beard", category: "Music", author: "lorc"),
        SkillIconOption(key: "game-delapouite-flute", title: "Flute", category: "Music", author: "delapouite"),
        SkillIconOption(key: "game-lorc-gears", title: "Gears", category: "Music", author: "lorc"),
        SkillIconOption(key: "game-lorc-harpy", title: "Harpy", category: "Music", author: "lorc"),
        SkillIconOption(key: "game-badges-music", title: "Music", category: "Music", author: "badges"),
        SkillIconOption(key: "game-lorc-earwig", title: "Earwig", category: "Music", author: "lorc"),
        SkillIconOption(key: "game-lorc-guitar", title: "Guitar", category: "Music", author: "lorc"),
        SkillIconOption(key: "game-delapouite-shears", title: "Shears", category: "Music", author: "delapouite"),
        SkillIconOption(key: "game-lorc-spears", title: "Spears", category: "Music", author: "lorc"),
        SkillIconOption(key: "game-zajkonur-violin", title: "Violin", category: "Music", author: "zajkonur"),
        SkillIconOption(key: "game-caro-asercion-earbuds", title: "Earbuds", category: "Music", author: "caro-asercion"),
        SkillIconOption(key: "game-delapouite-idea", title: "Idea", category: "Knowledge", author: "delapouite"),
        SkillIconOption(key: "game-skoll-read", title: "Read", category: "Knowledge", author: "skoll"),
        SkillIconOption(key: "game-lorc-brain", title: "Brain", category: "Knowledge", author: "lorc"),
        SkillIconOption(key: "game-delapouite-bread", title: "Bread", category: "Knowledge", author: "delapouite"),
        SkillIconOption(key: "game-cathelineau-dread", title: "Dread", category: "Knowledge", author: "cathelineau"),
        SkillIconOption(key: "game-lorc-quill", title: "Quill", category: "Knowledge", author: "lorc"),
        SkillIconOption(key: "game-delapouite-think", title: "Think", category: "Knowledge", author: "delapouite"),
        SkillIconOption(key: "game-lorc-tread", title: "Tread", category: "Knowledge", author: "lorc"),
        SkillIconOption(key: "game-delapouite-wisdom", title: "Wisdom", category: "Knowledge", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-diploma", title: "Diploma", category: "Knowledge", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-teacher", title: "Teacher", category: "Knowledge", author: "delapouite"),
        SkillIconOption(key: "game-lorc-bookmark", title: "Bookmark", category: "Knowledge", author: "lorc"),
        SkillIconOption(key: "game-delapouite-notebook", title: "Notebook", category: "Knowledge", author: "delapouite"),
        SkillIconOption(key: "game-lorc-book-aura", title: "Book Aura", category: "Knowledge", author: "lorc"),
        SkillIconOption(key: "game-delapouite-book-pile", title: "Book Pile", category: "Knowledge", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-phone", title: "Phone", category: "Technology", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-laptop", title: "Laptop", category: "Technology", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-database", title: "Database", category: "Technology", author: "delapouite"),
        SkillIconOption(key: "game-sbed-electric", title: "Electric", category: "Technology", author: "sbed"),
        SkillIconOption(key: "game-delapouite-keyboard", title: "Keyboard", category: "Technology", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-chips-bag", title: "Chips Bag", category: "Technology", author: "delapouite"),
        SkillIconOption(key: "game-lorc-circuitry", title: "Circuitry", category: "Technology", author: "lorc"),
        SkillIconOption(key: "game-delapouite-megaphone", title: "Megaphone", category: "Technology", author: "delapouite"),
        SkillIconOption(key: "game-lorc-microchip", title: "Microchip", category: "Technology", author: "lorc"),
        SkillIconOption(key: "game-lorc-processor", title: "Processor", category: "Technology", author: "lorc"),
        SkillIconOption(key: "game-delapouite-robot-leg", title: "Robot Leg", category: "Technology", author: "delapouite"),
        SkillIconOption(key: "game-lorc-satellite", title: "Satellite", category: "Technology", author: "lorc"),
        SkillIconOption(key: "game-delapouite-saxophone", title: "Saxophone", category: "Technology", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-xylophone", title: "Xylophone", category: "Technology", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-headphones", title: "Headphones", category: "Technology", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-dart", title: "Dart", category: "Art", author: "delapouite"),
        SkillIconOption(key: "game-caro-asercion-sink", title: "Sink", category: "Art", author: "caro-asercion"),
        SkillIconOption(key: "game-delapouite-chart", title: "Chart", category: "Art", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-smart", title: "Smart", category: "Art", author: "delapouite"),
        SkillIconOption(key: "game-badges-pencil", title: "Pencil", category: "Art", author: "badges"),
        SkillIconOption(key: "game-delapouite-pencil", title: "Pencil", category: "Art", author: "delapouite"),
        SkillIconOption(key: "game-lorc-tinker", title: "Tinker", category: "Art", author: "lorc"),
        SkillIconOption(key: "game-lorc-martini", title: "Martini", category: "Art", author: "lorc"),
        SkillIconOption(key: "game-delapouite-palette", title: "Palette", category: "Art", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-rempart", title: "Rempart", category: "Art", author: "delapouite"),
        SkillIconOption(key: "game-lorc-spartan", title: "Spartan", category: "Art", author: "lorc"),
        SkillIconOption(key: "game-delapouite-theater", title: "Theater", category: "Art", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-bat-mask", title: "Bat Mask", category: "Art", author: "delapouite"),
        SkillIconOption(key: "game-lorc-drink-me", title: "Drink Me", category: "Art", author: "lorc"),
        SkillIconOption(key: "game-delapouite-drinking", title: "Drinking", category: "Art", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-cook", title: "Cook", category: "Cooking", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-meal", title: "Meal", category: "Cooking", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-japan", title: "Japan", category: "Cooking", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-panda", title: "Panda", category: "Cooking", author: "delapouite"),
        SkillIconOption(key: "game-lorc-spoon", title: "Spoon", category: "Cooking", author: "lorc"),
        SkillIconOption(key: "game-delapouite-steak", title: "Steak", category: "Cooking", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-steam", title: "Steam", category: "Cooking", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-cookie", title: "Cookie", category: "Cooking", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-expand", title: "Expand", category: "Cooking", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-potato", title: "Potato", category: "Cooking", author: "delapouite"),
        SkillIconOption(key: "game-lorc-teapot", title: "Teapot", category: "Cooking", author: "lorc"),
        SkillIconOption(key: "game-delapouite-cupcake", title: "Cupcake", category: "Cooking", author: "delapouite"),
        SkillIconOption(key: "game-lorc-spanner", title: "Spanner", category: "Cooking", author: "lorc"),
        SkillIconOption(key: "game-lorc-tearing", title: "Tearing", category: "Cooking", author: "lorc"),
        SkillIconOption(key: "game-caro-asercion-anteater", title: "Anteater", category: "Cooking", author: "caro-asercion"),
        SkillIconOption(key: "game-skoll-talk", title: "Talk", category: "Communication", author: "skoll"),
        SkillIconOption(key: "game-delapouite-present", title: "Present", category: "Communication", author: "delapouite"),
        SkillIconOption(key: "game-lorc-eyestalk", title: "Eyestalk", category: "Communication", author: "lorc"),
        SkillIconOption(key: "game-lorc-beanstalk", title: "Beanstalk", category: "Communication", author: "lorc"),
        SkillIconOption(key: "game-delapouite-lead-pipe", title: "Lead Pipe", category: "Communication", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-team-idea", title: "Team Idea", category: "Communication", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-chat-bubble", title: "Chat Bubble", category: "Communication", author: "delapouite"),
        SkillIconOption(key: "game-lorc-letter-bomb", title: "Letter Bomb", category: "Communication", author: "lorc"),
        SkillIconOption(key: "game-delapouite-love-letter", title: "Love Letter", category: "Communication", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-steam-blast", title: "Steam Blast", category: "Communication", author: "delapouite"),
        SkillIconOption(key: "game-caro-asercion-steamroller", title: "Steamroller", category: "Communication", author: "caro-asercion"),
        SkillIconOption(key: "game-delapouite-meeple-group", title: "Meeple Group", category: "Communication", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-team-upgrade", title: "Team Upgrade", category: "Communication", author: "delapouite"),
        SkillIconOption(key: "game-lorc-grouped-drops", title: "Grouped Drops", category: "Communication", author: "lorc"),
        SkillIconOption(key: "game-delapouite-walkie-talkie", title: "Walkie Talkie", category: "Communication", author: "delapouite"),
        SkillIconOption(key: "game-badges-sun", title: "Sun", category: "Outdoors", author: "badges"),
        SkillIconOption(key: "game-lorc-sun", title: "Sun", category: "Outdoors", author: "lorc"),
        SkillIconOption(key: "game-badges-moon", title: "Moon", category: "Outdoors", author: "badges"),
        SkillIconOption(key: "game-lorc-moon", title: "Moon", category: "Outdoors", author: "lorc"),
        SkillIconOption(key: "game-delapouite-trail", title: "Trail", category: "Outdoors", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-forest", title: "Forest", category: "Outdoors", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-sunset", title: "Sunset", category: "Outdoors", author: "delapouite"),
        SkillIconOption(key: "game-lorc-compass", title: "Compass", category: "Outdoors", author: "lorc"),
        SkillIconOption(key: "game-delapouite-fishing", title: "Fishing", category: "Outdoors", author: "delapouite"),
        SkillIconOption(key: "game-lorc-flowers", title: "Flowers", category: "Outdoors", author: "lorc"),
        SkillIconOption(key: "game-lorc-sundial", title: "Sundial", category: "Outdoors", author: "lorc"),
        SkillIconOption(key: "game-delapouite-sunrise", title: "Sunrise", category: "Outdoors", author: "delapouite"),
        SkillIconOption(key: "game-lorc-sunrise", title: "Sunrise", category: "Outdoors", author: "lorc"),
        SkillIconOption(key: "game-lorc-campfire", title: "Campfire", category: "Outdoors", author: "lorc"),
        SkillIconOption(key: "game-lorc-fishbone", title: "Fishbone", category: "Outdoors", author: "lorc"),
        SkillIconOption(key: "game-badges-anvil", title: "Anvil", category: "Craft", author: "badges"),
        SkillIconOption(key: "game-lorc-anvil", title: "Anvil", category: "Craft", author: "lorc"),
        SkillIconOption(key: "game-sbed-wrench", title: "Wrench", category: "Craft", author: "sbed"),
        SkillIconOption(key: "game-delapouite-i-brick", title: "I Brick", category: "Craft", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-j-brick", title: "J Brick", category: "Craft", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-l-brick", title: "L Brick", category: "Craft", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-o-brick", title: "O Brick", category: "Craft", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-ropeway", title: "Ropeway", category: "Craft", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-s-brick", title: "S Brick", category: "Craft", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-t-brick", title: "T Brick", category: "Craft", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-toolbox", title: "Toolbox", category: "Craft", author: "delapouite"),
        SkillIconOption(key: "game-delapouite-z-brick", title: "Z Brick", category: "Craft", author: "delapouite"),
        SkillIconOption(key: "game-darkzaitzev-big-gear", title: "Big Gear", category: "Craft", author: "darkzaitzev"),
        SkillIconOption(key: "game-lorc-bolt-saw", title: "Bolt Saw", category: "Craft", author: "lorc"),
        SkillIconOption(key: "game-badges-building", title: "Building", category: "Craft", author: "badges"),
        SkillIconOption(key: "game-badges-eye", title: "Eye", category: "Mind & Spirit", author: "badges"),
        SkillIconOption(key: "game-lorc-aura", title: "Aura", category: "Mind & Spirit", author: "lorc"),
        SkillIconOption(key: "game-delapouite-soul", title: "Soul", category: "Mind & Spirit", author: "delapouite"),
        SkillIconOption(key: "game-badges-star", title: "Star", category: "Mind & Spirit", author: "badges"),
        SkillIconOption(key: "game-carl-olsen-flame", title: "Flame", category: "Mind & Spirit", author: "carl-olsen"),
        SkillIconOption(key: "game-lorc-lotus", title: "Lotus", category: "Mind & Spirit", author: "lorc"),
        SkillIconOption(key: "game-sbed-flamer", title: "Flamer", category: "Mind & Spirit", author: "sbed"),
        SkillIconOption(key: "game-lorc-prayer", title: "Prayer", category: "Mind & Spirit", author: "lorc"),
        SkillIconOption(key: "game-lorc-staryu", title: "Staryu", category: "Mind & Spirit", author: "lorc"),
        SkillIconOption(key: "game-delapouite-egg-eye", title: "Egg Eye", category: "Mind & Spirit", author: "delapouite"),
        SkillIconOption(key: "game-lorc-eyeball", title: "Eyeball", category: "Mind & Spirit", author: "lorc"),
        SkillIconOption(key: "game-lorc-bolt-eye", title: "Bolt Eye", category: "Mind & Spirit", author: "lorc"),
        SkillIconOption(key: "game-skoll-bullseye", title: "Bullseye", category: "Mind & Spirit", author: "skoll"),
        SkillIconOption(key: "game-lorc-dead-eye", title: "Dead Eye", category: "Mind & Spirit", author: "lorc"),
        SkillIconOption(key: "game-delapouite-eyepatch", title: "Eyepatch", category: "Mind & Spirit", author: "delapouite"),
    ]
    static let categories = ["All"] + Array(Set(options.map(\.category))).sorted()

    static func option(for key: String?) -> SkillIconOption? { options.first { $0.key == key }
    }

    static func fallback(for name: String) -> String {
        let value = name.lowercased()
        if value.contains("music") || value.contains("sing") || value.contains("piano") || value.contains("guitar") { return "music.note" }
        if value.contains("run") || value.contains("fit") || value.contains("strength") || value.contains("sport") { return "figure.run" }
        if value.contains("code") || value.contains("program") || value.contains("swift") { return "chevron.left.forwardslash.chevron.right" }
        if value.contains("read") || value.contains("learn") || value.contains("study") { return "book.closed.fill" }
        if value.contains("cook") || value.contains("food") { return "fork.knife" }
        if value.contains("photo") || value.contains("art") || value.contains("draw") { return "paintbrush.fill" }
        return "sparkle"
    }
}

struct SkillIcon: View {
    let key: String?
    var fallback: String = "sparkle"
    var body: some View {
        if let key, SkillIconCatalog.option(for: key) != nil { Image(key).resizable().renderingMode(.template).scaledToFit() }
        else { Image(systemName: fallback).resizable().scaledToFit() }
    }
}
