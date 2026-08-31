import SwiftUI

struct LockScreenWidgetSimulationView: View {
    private let quote = "The work you do today becomes your strength tomorrow."

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 0.08, green: 0.13, blue: 0.22),
                    Color(red: 0.02, green: 0.04, blue: 0.08),
                    Color.black,
                ],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            Circle()
                .fill(SystemTheme.cyan.opacity(0.18))
                .frame(width: 330)
                .blur(radius: 90)
                .offset(x: 160, y: -320)

            VStack(spacing: 0) {
                Text("Monday, 31 August")
                    .font(.system(size: 17, weight: .semibold, design: .rounded))
                    .padding(.top, 72)

                Text("18:42")
                    .font(.system(size: 82, weight: .thin, design: .rounded))
                    .tracking(-3)

                HStack(spacing: 12) {
                    Image(systemName: "flashlight.off.fill")
                        .frame(width: 42, height: 42)
                        .background(.black.opacity(0.32), in: Circle())
                    Spacer()
                    Image(systemName: "camera.fill")
                        .frame(width: 42, height: 42)
                        .background(.black.opacity(0.32), in: Circle())
                }
                .padding(.horizontal, 48)
                .opacity(0)
                .frame(height: 10)

                VStack(alignment: .leading, spacing: 7) {
                    Label("QUICK ACTIONS", systemImage: "bolt.fill")
                        .font(.system(size: 9, weight: .bold))
                        .tracking(1)
                        .foregroundStyle(SystemTheme.cyan)
                    HStack(spacing: 5) {
                        ForEach(["house.fill", "checklist", "figure.run", "point.3.connected.trianglepath.dotted"], id: \.self) { icon in
                            Image(systemName: icon)
                                .font(.system(size: 13, weight: .semibold))
                                .frame(maxWidth: .infinity, maxHeight: .infinity)
                                .background(.white.opacity(0.12), in: RoundedRectangle(cornerRadius: 7))
                        }
                    }
                }
                .padding(8)
                .frame(width: 158, height: 66, alignment: .leading)
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 14, style: .continuous))
                .overlay {
                    RoundedRectangle(cornerRadius: 14, style: .continuous)
                        .stroke(.white.opacity(0.12))
                }
                .padding(.top, 12)

                Spacer()

                HStack {
                    Image(systemName: "flashlight.off.fill")
                    Spacer()
                    Image(systemName: "camera.fill")
                }
                .font(.title3)
                .padding(.horizontal, 60)
                .padding(.bottom, 54)
            }
            .foregroundStyle(.white)
        }
        .preferredColorScheme(.dark)
    }
}

#Preview("Lock Screen widget simulation") {
    LockScreenWidgetSimulationView()
}

struct HomeScreenQuoteWidgetSimulationView: View {
    private let quote = "The work you do today becomes your strength tomorrow."

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color(red: 0.05, green: 0.12, blue: 0.22), .black],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 26) {
                HStack {
                    Text("18:42").font(.headline)
                    Spacer()
                    Image(systemName: "wifi")
                    Image(systemName: "battery.100percent")
                }
                .padding(.horizontal, 24)
                .padding(.top, 10)

                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Label("SYSTEM", systemImage: "diamond.fill")
                            .font(.caption.bold())
                            .tracking(1.8)
                            .foregroundStyle(SystemTheme.cyan)
                        Spacer()
                        Text("TODAY")
                            .font(.caption2.bold())
                            .foregroundStyle(.secondary)
                    }
                    Spacer(minLength: 0)
                    Text(quote)
                        .font(.system(.title3, design: .rounded, weight: .bold))
                        .lineLimit(3)
                    Text("— The System")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(.secondary)
                }
                .padding(18)
                .frame(maxWidth: .infinity, alignment: .leading)
                .frame(height: 166)
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
                .overlay {
                    RoundedRectangle(cornerRadius: 24, style: .continuous)
                        .stroke(.white.opacity(0.12))
                }
                .padding(.horizontal, 20)

                LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 4), spacing: 28) {
                    ForEach(Array(zip(
                        ["checkmark.circle.fill", "figure.run", "book.closed.fill", "music.note", "camera.fill", "brain.head.profile", "calendar", "ellipsis"],
                        ["Quests", "Train", "Read", "Music", "Camera", "Skills", "Calendar", "More"]
                    )), id: \.1) { icon, label in
                        VStack(spacing: 6) {
                            Image(systemName: icon)
                                .font(.title2)
                                .frame(width: 58, height: 58)
                                .background(SystemTheme.surfaceRaised, in: RoundedRectangle(cornerRadius: 14))
                            Text(label).font(.caption2)
                        }
                    }
                }
                .padding(.horizontal, 24)

                Spacer()
            }
            .foregroundStyle(.white)
        }
        .preferredColorScheme(.dark)
    }
}

#Preview("Home Screen wide widget simulation") {
    HomeScreenQuoteWidgetSimulationView()
}

#Preview("Authentication", traits: .portrait) {
    AuthView()
        .environmentObject(SessionStore())
        .preferredColorScheme(.dark)
}

#Preview("Quest card", traits: .sizeThatFitsLayout) {
    QuestCard(quest: .preview, busy: false) { _ in }
        .padding()
        .background(SystemTheme.background)
        .preferredColorScheme(.dark)
}

#Preview("System header", traits: .sizeThatFitsLayout) {
    SystemHeader(title: "Quest Board", eyebrow: "Active missions")
        .padding()
        .background(SystemTheme.background)
        .preferredColorScheme(.dark)
}

private extension Quest {
    static let preview = Quest(
        id: 12,
        title: "Complete the morning training",
        description: "Build momentum before the day begins.",
        schedule: QuestSchedule(label: "Every day"),
        difficulty: "C",
        targetCount: 100,
        unit: "reps",
        practiceMinutes: 20,
        statReward: "strength",
        statRewardAmount: 1,
        isActive: true,
        currentInstance: QuestInstance(
            id: 34,
            progress: 40,
            targetCount: 100,
            status: "active",
            periodEnd: "Today"
        ),
        nextDueDate: nil
    )
}
