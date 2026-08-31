import SwiftUI

enum SystemTheme {
    static let background = Color(red: 0.025, green: 0.023, blue: 0.022)
    static let surface = Color(red: 0.055, green: 0.050, blue: 0.044)
    static let surfaceRaised = Color(red: 0.09, green: 0.078, blue: 0.063)
    static let cyan = Color(red: 0.72, green: 0.58, blue: 0.30)
    static let blue = Color(red: 0.78, green: 0.23, blue: 0.10)
    static let gold = Color(red: 0.82, green: 0.66, blue: 0.34)
    static let muted = Color(red: 0.88, green: 0.85, blue: 0.75).opacity(0.58)
    static let parchment = Color(red: 0.88, green: 0.85, blue: 0.75)
    static let ember = Color(red: 0.78, green: 0.23, blue: 0.10)
}

struct SystemCard<Content: View>: View {
    @ViewBuilder var content: Content

    var body: some View {
        content
            .padding(16)
            .background(Color.black.opacity(0.42))
            .overlay {
                Rectangle().stroke(SystemTheme.gold.opacity(0.27), lineWidth: 1)
            }
            .overlay(alignment: .topLeading) {
                LCorner().stroke(SystemTheme.gold.opacity(0.7), lineWidth: 1).frame(width: 22, height: 22)
            }
            .overlay(alignment: .bottomTrailing) {
                LCorner().stroke(SystemTheme.gold.opacity(0.7), lineWidth: 1).frame(width: 22, height: 22).rotationEffect(.degrees(180))
            }
    }
}

struct SystemHeader: View {
    let title: String
    let eyebrow: String

    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(eyebrow.uppercased())
                .font(.system(size: 10, weight: .bold, design: .serif))
                .tracking(2)
                .foregroundStyle(SystemTheme.cyan)
            Text(title)
                .font(.system(.largeTitle, design: .serif, weight: .semibold))
                .foregroundStyle(SystemTheme.parchment)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

struct SystemBackdrop: View {
    var body: some View {
        ZStack {
            LinearGradient(colors: [Color(red: 0.075, green: 0.055, blue: 0.045), SystemTheme.background], startPoint: .top, endPoint: .bottom)
            RadialGradient(colors: [SystemTheme.ember.opacity(0.11), .clear], center: .top, startRadius: 0, endRadius: 360)
        }.ignoresSafeArea()
    }
}

private struct LCorner: Shape {
    func path(in rect: CGRect) -> Path {
        Path { path in
            path.move(to: CGPoint(x: rect.minX, y: rect.maxY)); path.addLine(to: CGPoint(x: rect.minX, y: rect.minY)); path.addLine(to: CGPoint(x: rect.maxX, y: rect.minY))
            path.move(to: CGPoint(x: rect.minX + 5, y: rect.minY + 12)); path.addLine(to: CGPoint(x: rect.minX + 5, y: rect.minY + 5)); path.addLine(to: CGPoint(x: rect.minX + 12, y: rect.minY + 5))
        }
    }
}
