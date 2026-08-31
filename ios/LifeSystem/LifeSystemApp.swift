import SwiftUI
import SwiftData

@main
struct LifeSystemApp: App {
    private let persistence = PersistenceController.shared

    var body: some Scene {
        WindowGroup {
            RootView()
                .preferredColorScheme(.dark)
                .modelContainer(persistence.container)
        }
    }
}

struct RootView: View {
    var body: some View {
        Group {
#if DEBUG
            if ProcessInfo.processInfo.arguments.contains("-skillsPreview") {
                SkillsPreviewScreen()
            } else if ProcessInfo.processInfo.arguments.contains("-skillIconPickerPreview") {
                SkillIconPickerPreviewScreen()
            } else if ProcessInfo.processInfo.arguments.contains("-playerStatePreview") {
                PlayerStatePreviewScreen()
            } else if ProcessInfo.processInfo.arguments.contains("-playerAttributesPreview") {
                PlayerAttributesPreviewScreen()
            } else if ProcessInfo.processInfo.arguments.contains("-lockScreenWidgetPreview") {
                LockScreenWidgetSimulationView()
            } else if ProcessInfo.processInfo.arguments.contains("-homeScreenWidgetPreview") {
                HomeScreenQuoteWidgetSimulationView()
            } else if ProcessInfo.processInfo.arguments.contains("-practiceJournalPreview") {
                PracticeJournalPreviewScreen()
            } else if ProcessInfo.processInfo.arguments.contains("-practicePhotoProof") {
                PracticeJournalProofScreen(includesAudio: false)
            } else if ProcessInfo.processInfo.arguments.contains("-practiceMediaProof") {
                PracticeJournalProofScreen(includesAudio: true)
            } else if ProcessInfo.processInfo.arguments.contains("-practiceRecordingProof") {
                PracticeRecordingProofScreen()
            } else if ProcessInfo.processInfo.arguments.contains("-createRoutinePreview") {
                CreateRoutinePreviewScreen()
            } else if ProcessInfo.processInfo.arguments.contains("-createQuestPreview") {
                CreateQuestView(onCreated: { _ in })
            } else if ProcessInfo.processInfo.arguments.contains("-dashboardPreview") {
                DashboardPreviewScreen()
            } else {
                MainTabView()
            }
#else
            MainTabView()
#endif
        }
        .tint(SystemTheme.cyan)
        .background(SystemTheme.background.ignoresSafeArea())
        .font(.system(.body, design: .serif))
    }
}
