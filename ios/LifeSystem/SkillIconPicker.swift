import SwiftUI

struct SkillIconPicker: View {
    @Environment(\.dismiss) private var dismiss
    let selectedKey: String?
    let onSelect: (String?) -> Void
    @State private var search = ""
    @State private var category = "All"

    private let columns = Array(repeating: GridItem(.flexible(), spacing: 10), count: 4)

    private var options: [SkillIconOption] {
        SkillIconCatalog.options.filter { icon in
            (category == "All" || icon.category == category) &&
            (search.isEmpty || icon.title.localizedCaseInsensitiveContains(search) || icon.category.localizedCaseInsensitiveContains(search))
        }
    }

    var body: some View {
        NavigationStack {
            ZStack {
                SystemBackdrop()
                ScrollView {
                    VStack(spacing: 14) {
                        HStack(spacing: 10) {
                            Image(systemName: "magnifyingglass")
                                .foregroundStyle(SystemTheme.gold)
                            TextField("Search icons or categories", text: $search)
                                .textInputAutocapitalization(.never)
                                .autocorrectionDisabled()
                            if !search.isEmpty {
                                Button { search = "" } label: {
                                    Image(systemName: "xmark.circle.fill")
                                        .foregroundStyle(SystemTheme.muted)
                                }
                                .buttonStyle(.plain)
                                .accessibilityLabel("Clear search")
                            }
                        }
                        .padding(.horizontal, 13)
                        .frame(height: 46)
                        .background(Color.black.opacity(0.48))
                        .overlay { Rectangle().stroke(SystemTheme.gold.opacity(0.38)) }
                        .padding(.horizontal, 18)

                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack {
                                ForEach(SkillIconCatalog.categories, id: \.self) { item in
                                    Button(item) { category = item }
                                        .buttonStyle(.bordered)
                                        .tint(category == item ? SystemTheme.gold : SystemTheme.muted)
                                }
                            }.padding(.horizontal, 18)
                        }

                        LazyVGrid(columns: columns, spacing: 12) {
                            automaticTile
                            ForEach(options) { option in iconTile(option) }
                        }
                        .padding(.horizontal, 18)
                        .padding(.bottom, 30)

                        if options.isEmpty {
                            ContentUnavailableView.search(text: search)
                                .foregroundStyle(SystemTheme.parchment)
                                .padding(.top, 36)
                        }
                    }.padding(.top, 12)
                }
            }
            .navigationTitle("Choose Sigil")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .cancellationAction) { Button("Cancel") { dismiss() } } }
        }
        .preferredColorScheme(.dark)
    }

    private var automaticTile: some View {
        Button { onSelect(nil) } label: {
            VStack(spacing: 7) {
                Image(systemName: "wand.and.stars").font(.title2).frame(height: 34)
                Text("Automatic").font(.caption2).lineLimit(1)
            }
            .foregroundStyle(SystemTheme.parchment)
            .frame(maxWidth: .infinity).padding(.vertical, 11)
            .background(Color.black.opacity(0.4))
            .overlay { Rectangle().stroke(selectedKey == nil ? SystemTheme.gold : SystemTheme.gold.opacity(0.22), lineWidth: selectedKey == nil ? 2 : 1) }
        }.buttonStyle(.plain)
    }

    private func iconTile(_ option: SkillIconOption) -> some View {
        Button { onSelect(option.key) } label: {
            VStack(spacing: 7) {
                SkillIcon(key: option.key).foregroundStyle(SystemTheme.gold).frame(width: 34, height: 34)
                Text(option.title).font(.caption2).lineLimit(1).minimumScaleFactor(0.7)
            }
            .foregroundStyle(SystemTheme.parchment)
            .frame(maxWidth: .infinity).padding(.vertical, 11)
            .background(Color.black.opacity(0.4))
            .overlay { Rectangle().stroke(selectedKey == option.key ? SystemTheme.gold : SystemTheme.gold.opacity(0.22), lineWidth: selectedKey == option.key ? 2 : 1) }
        }
        .buttonStyle(.plain)
        .accessibilityLabel("\(option.title), \(option.category)")
    }
}

struct SkillIconCreditsView: View {
    private var authors: [(String, Int)] {
        Dictionary(grouping: SkillIconCatalog.options, by: \.author)
            .map { ($0.key, $0.value.count) }.sorted { $0.0 < $1.0 }
    }

    var body: some View {
        List {
            Section {
                Text("The 150 skill sigils are adapted from Game-icons.net under the Creative Commons Attribution 3.0 license.")
                Link("Visit Game-icons.net", destination: URL(string: "https://game-icons.net/")!)
            }
            Section("Artists") {
                ForEach(authors, id: \.0) { author, count in
                    LabeledContent(author, value: "\(count) icons")
                }
            }
        }
        .navigationTitle("Icon Credits")
        .scrollContentBackground(.hidden)
        .background(SystemBackdrop())
    }
}

struct SkillIconPickerPreviewScreen: View {
    var body: some View { SkillIconPicker(selectedKey: SkillIconCatalog.options.first?.key) { _ in } }
}

#Preview("Skill Icon Picker") { SkillIconPickerPreviewScreen() }
