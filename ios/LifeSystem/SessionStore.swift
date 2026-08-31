import Foundation

@MainActor
final class SessionStore: ObservableObject {
    @Published private(set) var isAuthenticated = KeychainToken.load() != nil
    @Published var isBusy = false
    @Published var errorMessage: String?

    func login(email: String, password: String) async {
        await authenticate(path: "/auth/login", payload: LoginPayload(email: email, password: password))
    }

    func register(email: String, password: String, name: String) async {
        let zone = TimeZone.current.identifier
        await authenticate(path: "/auth/register", payload: RegisterPayload(email: email, password: password, name: name, timezone: zone))
    }

    private func authenticate<T: Encodable>(path: String, payload: T) async {
        isBusy = true
        errorMessage = nil
        defer { isBusy = false }
        do {
            let token: TokenResponse = try await APIClient.shared.request(path, method: "POST", body: payload)
            KeychainToken.save(token.accessToken)
            isAuthenticated = true
        } catch { errorMessage = error.localizedDescription }
    }

    func signOut() {
        KeychainToken.delete()
        isAuthenticated = false
    }
}

private struct LoginPayload: Encodable { let email, password: String }
private struct RegisterPayload: Encodable { let email, password, name, timezone: String }
