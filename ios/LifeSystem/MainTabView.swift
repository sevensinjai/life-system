import SwiftUI

struct MainTabView: View {
    private enum Tab: Hashable { case dashboard, board, skills, system, more }
    @State private var selection: Tab = .dashboard

    var body: some View {
        TabView(selection: $selection) {
            DashboardView(
                openBoard: { selection = .board },
                openSystem: { selection = .system }
            )
            .tabItem { Label("Home", systemImage: "diamond") }
            .tag(Tab.dashboard)
            BoardView().tabItem { Label("Board", systemImage: "checklist") }.tag(Tab.board)
            SkillsView().tabItem { Label("Skills", systemImage: "point.3.connected.trianglepath.dotted") }.tag(Tab.skills)
            SystemLogView().tabItem { Label("System", systemImage: "terminal") }.tag(Tab.system)
            SettingsView().tabItem { Label("More", systemImage: "ellipsis") }.tag(Tab.more)
        }
        .toolbarBackground(Color.black.opacity(0.94), for: .tabBar)
        .toolbarBackground(.visible, for: .tabBar)
        .task { await QuoteWidgetSync.refresh() }
        .onOpenURL { url in
            guard url.scheme == "lifesystem" else { return }
            switch url.host {
            case "home": selection = .dashboard
            case "board": selection = .board
            case "skills": selection = .skills
            case "system": selection = .system
            default: break
            }
        }
    }
}

struct SettingsView: View {
    @EnvironmentObject private var session: SessionStore
    var body: some View {
        NavigationStack {
            List {
                Section("Library") {
                    NavigationLink { QuestLibraryView() } label: { Label("All quests", systemImage: "scroll") }
                    NavigationLink { SkillIconCreditsView() } label: { Label("Icon credits", systemImage: "seal") }
                }
                Section("Connection") { LabeledContent("API", value: "127.0.0.1:8000") }
                Section("Lock Screen quote") {
                    VStack(alignment: .leading, spacing: 8) {
                        Label("Add the Daily System Quote widget", systemImage: "lock.rectangle")
                            .font(.headline)
                        Text("Touch and hold your Lock Screen, choose Customize, tap the widget area, then select System Quote.")
                            .font(.footnote)
                            .foregroundStyle(.secondary)
                    }
                    .padding(.vertical, 4)
                }
                Section {
                    Button("Refresh Lock Screen quote") {
                        Task { await QuoteWidgetSync.refresh() }
                    }
                    Button("Sign out", role: .destructive) {
                        QuoteWidgetSync.clear()
                        session.signOut()
                    }
                }
            }.navigationTitle("More")
        }
    }
}
