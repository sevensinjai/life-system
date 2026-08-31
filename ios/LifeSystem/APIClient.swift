import Foundation
import Security

enum APIError: LocalizedError {
    case invalidResponse
    case server(String)

    var errorDescription: String? {
        switch self {
        case .invalidResponse: "The System returned an invalid response."
        case .server(let message): message
        }
    }
}

final class APIClient {
    static let shared = APIClient()
    private let decoder: JSONDecoder
    private let encoder: JSONEncoder

    private init() {
        decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
    }

    private var baseURL: URL {
        let configured = Bundle.main.object(forInfoDictionaryKey: "SYSTEM_API_URL") as? String
        return URL(string: configured ?? "http://127.0.0.1:8000")!
    }

    func request<Response: Decodable, Body: Encodable>(
        _ path: String,
        method: String = "GET",
        body: Body? = Optional<String>.none
    ) async throws -> Response {
        var request = URLRequest(url: baseURL.appending(path: path))
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if let token = KeychainToken.load() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        if let body { request.httpBody = try encoder.encode(body) }

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse else { throw APIError.invalidResponse }
        guard (200..<300).contains(http.statusCode) else {
            let message = (try? decoder.decode(APIErrorEnvelope.self, from: data).error.message)
                ?? "Request failed (\(http.statusCode))."
            throw APIError.server(message)
        }
        return try decoder.decode(Response.self, from: data)
    }

    func request<Response: Decodable>(_ path: String, method: String = "GET") async throws -> Response {
        try await request(path, method: method, body: Optional<String>.none)
    }
}

enum KeychainToken {
    private static let service = "uk.tomchan.LifeSystem"
    private static let account = "access-token"

    static func save(_ token: String) {
        delete()
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecValueData as String: Data(token.utf8)
        ]
        SecItemAdd(query as CFDictionary, nil)
    }

    static func load() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        var result: AnyObject?
        guard SecItemCopyMatching(query as CFDictionary, &result) == errSecSuccess,
              let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }

    static func delete() {
        SecItemDelete([kSecClass as String: kSecClassGenericPassword,
                       kSecAttrService as String: service,
                       kSecAttrAccount as String: account] as CFDictionary)
    }
}
