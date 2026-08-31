import SwiftUI

struct AuthView: View {
    @EnvironmentObject private var session: SessionStore
    @State private var registering = false
    @State private var name = ""
    @State private var email = ""
    @State private var password = ""

    var body: some View {
        ZStack {
            SystemBackdrop()
            Circle().fill(SystemTheme.ember.opacity(0.18)).frame(width: 360).blur(radius: 80).offset(y: -300)
            ScrollView {
                VStack(spacing: 28) {
                    Spacer(minLength: 72)
                    VStack(spacing: 12) {
                        Image(systemName: "flame.fill")
                            .font(.system(size: 44)).foregroundStyle(SystemTheme.ember)
                            .shadow(color: SystemTheme.ember, radius: 18)
                        Text("SYSTEM").font(.system(size: 35, weight: .semibold, design: .serif)).tracking(7).foregroundStyle(SystemTheme.parchment)
                        Text("Your life. Your progression.").font(.system(.body, design: .serif)).foregroundStyle(SystemTheme.muted)
                    }

                    SystemCard {
                        VStack(spacing: 16) {
                            Picker("Mode", selection: $registering) {
                                Text("Log in").tag(false)
                                Text("Register").tag(true)
                            }.pickerStyle(.segmented)
                            if registering {
                                TextField("Hunter name", text: $name).textContentType(.name)
                            }
                            TextField("Email", text: $email)
                                .textContentType(.emailAddress).keyboardType(.emailAddress).textInputAutocapitalization(.never)
                            SecureField("Password", text: $password).textContentType(registering ? .newPassword : .password)
                            if let message = session.errorMessage {
                                Text(message).font(.footnote).foregroundStyle(.red).frame(maxWidth: .infinity, alignment: .leading)
                            }
                            Button {
                                Task {
                                    if registering { await session.register(email: email, password: password, name: name) }
                                    else { await session.login(email: email, password: password) }
                                }
                            } label: {
                                HStack { if session.isBusy { ProgressView() }; Text(registering ? "Awaken" : "Enter the System").bold() }
                                    .frame(maxWidth: .infinity).padding(.vertical, 9)
                            }
                            .buttonStyle(.borderedProminent)
                            .disabled(email.isEmpty || password.count < 8 || (registering && name.isEmpty) || session.isBusy)
                        }
                        .textFieldStyle(.roundedBorder)
                    }
                    Text("Connects to the System API running on your Mac.")
                        .font(.caption).foregroundStyle(SystemTheme.muted)
                }.padding(24)
            }
        }
    }
}
