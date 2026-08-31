import SwiftUI

struct SystemLogView: View {
    @State private var events: [SystemEvent] = []
    var body: some View {
        NavigationStack {
            List(events) { event in
                VStack(alignment: .leading, spacing: 5) {
                    Text(event.eventType.replacingOccurrences(of: "_", with: " ").uppercased()).font(.caption2.bold()).tracking(1).foregroundStyle(SystemTheme.cyan)
                    Text(event.message)
                    Text(event.createdAt).font(.caption2.monospaced()).foregroundStyle(.secondary)
                }.padding(.vertical, 7)
                 .listRowBackground(Color.black.opacity(0.38))
                 .listRowSeparatorTint(SystemTheme.gold.opacity(0.2))
            }.navigationTitle("System Log")
             .scrollContentBackground(.hidden)
             .background(SystemBackdrop())
             .overlay { if events.isEmpty { ContentUnavailableView("No transmissions", systemImage: "terminal", description: Text("System events will appear here.")) } }
             .task { await load() }.refreshable { await load() }
        }
    }
    private func load() async { events = (try? await APIClient.shared.request("/system/events?limit=50")) ?? [] }
}
