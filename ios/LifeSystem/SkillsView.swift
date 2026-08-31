import AVFoundation
import PhotosUI
import SwiftUI
import UniformTypeIdentifiers

private struct CreateSkillPayload: Codable {
    let name: String
    let description: String?
    let parentId: Int?
    let iconKey: String?
}

private struct SkillIconPayload: Codable { let iconKey: String? }

private struct PracticeAttachmentPayload: Codable {
    let kind: String
    let filename: String
    let contentType: String
    let dataBase64: String
}

private struct PracticePayload: Codable {
    let minutes: Int
    let note: String?
    let attachments: [PracticeAttachmentPayload]
}

private struct PracticeDraftAttachment: Identifiable {
    let id = UUID()
    let kind: String
    let filename: String
    let contentType: String
    let data: Data
    let thumbnail: Image?
}

struct SkillsView: View {
    @State private var roots: [SkillNode] = []
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var showingCreate = false

    var body: some View {
        NavigationStack {
            Group {
                if isLoading {
                    ProgressView("Loading skill tree…").tint(SystemTheme.cyan)
                } else if roots.isEmpty {
                    ContentUnavailableView {
                        Label("Choose your first skill", systemImage: "point.3.connected.trianglepath.dotted")
                    } description: {
                        Text("Start broad. You can add focused sub-skills as your practice becomes clearer.")
                    } actions: {
                        Button("Create a skill") { showingCreate = true }.buttonStyle(.borderedProminent)
                    }
                } else {
                    SkillTreeContent(roots: roots)
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(SystemBackdrop())
            .navigationTitle("Skill Tree")
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button { showingCreate = true } label: { Label("New skill", systemImage: "plus") }
                }
            }
            .task { await load() }
            .refreshable { await load() }
            .sheet(isPresented: $showingCreate) {
                CreateSkillView(parent: nil) { Task { await load() } }
            }
            .overlay(alignment: .bottom) {
                if let errorMessage {
                    Text(errorMessage).font(.footnote).padding(10).background(.red.opacity(0.9)).clipShape(Capsule()).padding()
                }
            }
        }
    }

    private func load() async {
        isLoading = roots.isEmpty
        defer { isLoading = false }
        do {
            roots = try await LocalDataStore.shared.request("/skills")
            errorMessage = nil
        } catch { errorMessage = error.localizedDescription }
    }
}

private struct SkillTreeContent: View {
    let roots: [SkillNode]

    private var flattened: [SkillNode] {
        func walk(_ nodes: [SkillNode]) -> [SkillNode] {
            nodes.flatMap { [$0] + walk($0.children) }
        }
        return walk(roots)
    }

    var body: some View {
        ScrollView {
            LazyVStack(spacing: 10) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("YOUR GROWTH MAP").font(.caption2.bold()).tracking(2).foregroundStyle(SystemTheme.cyan)
                    Text("Practice a focused skill and the work rolls up through its branch.")
                        .font(.subheadline).foregroundStyle(SystemTheme.muted)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.bottom, 6)

                ForEach(flattened) { skill in
                    NavigationLink { SkillDetailView(skillID: skill.id, initial: skill.summary) } label: {
                        SkillTreeRow(skill: skill)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding()
        }
    }
}

private struct SkillTreeRow: View {
    let skill: SkillNode

    var body: some View {
        HStack(spacing: 10) {
            if skill.depth > 1 {
                HStack(spacing: 6) {
                    ForEach(1..<skill.depth, id: \.self) { _ in
                        Rectangle().fill(SystemTheme.cyan.opacity(0.22)).frame(width: 2)
                    }
                }
                .frame(width: CGFloat(skill.depth - 1) * 13)
            }
            SkillIcon(key: skill.iconKey, fallback: SkillIconCatalog.fallback(for: skill.name))
                .foregroundStyle(SystemTheme.cyan)
                .frame(width: 20, height: 20)
                .padding(7)
                .background(SystemTheme.surfaceRaised)
                .clipShape(Circle())
            VStack(alignment: .leading, spacing: 5) {
                HStack {
                    Text(skill.name).font(.headline).lineLimit(1)
                    Spacer()
                    Text("LV \(skill.level)").font(.caption.bold().monospaced()).foregroundStyle(SystemTheme.cyan)
                }
                ProgressView(value: skill.expProgress).tint(SystemTheme.cyan)
                HStack {
                    Text("\(skill.exp) / \(skill.expToNextLevel) EXP")
                    Spacer()
                    if !skill.children.isEmpty { Text("\(skill.children.count) branches") }
                }
                .font(.caption2.monospaced()).foregroundStyle(SystemTheme.muted)
            }
            Image(systemName: "chevron.right").font(.caption).foregroundStyle(SystemTheme.muted)
        }
        .padding(13)
        .background(Color.black.opacity(0.4))
        .overlay { Rectangle().stroke(SystemTheme.gold.opacity(0.24)) }
    }
}

struct SkillDetailView: View {
    let skillID: Int
    let initial: SkillSummary

    @State private var detail: SkillDetail?
    @State private var showingPractice = false
    @State private var showingRoutine = false
    @State private var showingChild = false
    @State private var showingIconPicker = false
    @State private var practiceEntries: [PracticeEntry] = []

    private var skill: SkillSummary { detail?.summary ?? initial }

    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                SystemCard {
                    VStack(spacing: 14) {
                        HStack(alignment: .top) {
                            Button { showingIconPicker = true } label: {
                                SkillIcon(key: skill.iconKey, fallback: SkillIconCatalog.fallback(for: skill.name))
                                    .foregroundStyle(SystemTheme.gold)
                                    .frame(width: 36, height: 36)
                                    .padding(10)
                                    .background(Color.black.opacity(0.35))
                                    .overlay { Rectangle().stroke(SystemTheme.gold.opacity(0.35)) }
                            }
                            .buttonStyle(.plain)
                            VStack(alignment: .leading, spacing: 4) {
                                Text("SKILL STATUS").font(.caption2.bold()).tracking(1.6).foregroundStyle(SystemTheme.cyan)
                                Text(skill.name).font(.title.bold())
                                if let description = skill.description { Text(description).font(.subheadline).foregroundStyle(SystemTheme.muted) }
                            }
                            Spacer(); Text("LV \(skill.level)").font(.headline.monospaced()).foregroundStyle(SystemTheme.cyan)
                        }
                        ProgressView(value: skill.expProgress).tint(SystemTheme.cyan)
                        HStack {
                            Text("\(skill.exp) / \(skill.expToNextLevel) EXP")
                            Spacer(); Text("\(skill.totalExpEarned) min practised")
                        }.font(.caption.monospaced()).foregroundStyle(SystemTheme.muted)
                    }
                }

                HStack(spacing: 10) {
                    action("Log practice", "timer", primary: true) { showingPractice = true }
                    action("Create routine", "calendar.badge.plus", primary: false) { showingRoutine = true }
                }

                if let path = detail?.path, !path.isEmpty {
                    SystemCard {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("BRANCH").font(.caption2.bold()).tracking(1.5).foregroundStyle(SystemTheme.cyan)
                            Text((path.map(\.name) + [skill.name]).joined(separator: "  ›  "))
                                .font(.subheadline).foregroundStyle(SystemTheme.muted)
                        }.frame(maxWidth: .infinity, alignment: .leading)
                    }
                }

                SystemCard {
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Text("SUB-SKILLS").font(.caption2.bold()).tracking(1.5).foregroundStyle(SystemTheme.cyan)
                            Spacer(); Button { showingChild = true } label: { Label("Add", systemImage: "plus") }.font(.caption.bold())
                        }
                        if let children = detail?.children, !children.isEmpty {
                            ForEach(children) { child in
                                NavigationLink { SkillDetailView(skillID: child.id, initial: child) } label: {
                                    HStack { Image(systemName: "arrow.turn.down.right").foregroundStyle(SystemTheme.cyan); Text(child.name); Spacer(); Text("LV \(child.level)").font(.caption.monospaced()).foregroundStyle(SystemTheme.muted); Image(systemName: "chevron.right").font(.caption).foregroundStyle(SystemTheme.muted) }
                                }.buttonStyle(.plain)
                            }
                        } else {
                            Text("Add a focused skill when this area becomes too broad to practise directly.")
                                .font(.subheadline).foregroundStyle(SystemTheme.muted)
                        }
                    }.frame(maxWidth: .infinity, alignment: .leading)
                }

                SystemCard {
                    VStack(alignment: .leading, spacing: 6) {
                        Text("PRACTICE RECORD").font(.caption2.bold()).tracking(1.5).foregroundStyle(SystemTheme.cyan)
                        Text("\(skill.totalExpEarned) total minutes credited")
                            .font(.title3.bold().monospaced())
                        if practiceEntries.isEmpty {
                            Text("Your saved notes, photos, and recordings will appear here after you log practice.")
                                .font(.caption).foregroundStyle(SystemTheme.muted)
                        } else {
                            ForEach(practiceEntries) { entry in
                                Divider().overlay(Color.white.opacity(0.08))
                                VStack(alignment: .leading, spacing: 6) {
                                    HStack {
                                        Text("\(entry.minutes) min").font(.headline.monospaced())
                                        Spacer()
                                        Text(entry.createdAt.prefix(10)).font(.caption.monospaced()).foregroundStyle(SystemTheme.muted)
                                    }
                                    if let note = entry.note, !note.isEmpty {
                                        Text(note).font(.subheadline).lineLimit(4)
                                    }
                                    if !entry.attachments.isEmpty {
                                        HStack(spacing: 12) {
                                            let images = entry.attachments.filter { $0.kind == "image" }.count
                                            let audio = entry.attachments.filter { $0.kind == "audio" }.count
                                            if images > 0 { Label("\(images)", systemImage: "photo").accessibilityLabel("\(images) photos") }
                                            if audio > 0 { Label("\(audio)", systemImage: "waveform").accessibilityLabel("\(audio) recordings") }
                                        }
                                        .font(.caption.bold()).foregroundStyle(SystemTheme.cyan)
                                    }
                                }
                                .padding(.vertical, 4)
                            }
                        }
                    }.frame(maxWidth: .infinity, alignment: .leading)
                }
            }.padding()
        }
        .background(SystemTheme.background)
        .navigationTitle(skill.name)
        .navigationBarTitleDisplayMode(.inline)
        .task { await load() }
        .sheet(isPresented: $showingPractice) { LogPracticeView(skill: skill) { Task { await load() } } }
        .sheet(isPresented: $showingRoutine) { CreateQuestView(linkedSkill: skill) { _ in } }
        .sheet(isPresented: $showingChild) { CreateSkillView(parent: skill) { Task { await load() } } }
        .sheet(isPresented: $showingIconPicker) {
            SkillIconPicker(selectedKey: skill.iconKey) { key in
                Task { await setIcon(key) }
            }
        }
    }

    @ViewBuilder
    private func action(_ title: String, _ icon: String, primary: Bool, perform: @escaping () -> Void) -> some View {
        if primary {
            Button(action: perform) { Label(title, systemImage: icon).frame(maxWidth: .infinity).padding(.vertical, 7) }
                .buttonStyle(.borderedProminent)
        } else {
            Button(action: perform) { Label(title, systemImage: icon).frame(maxWidth: .infinity).padding(.vertical, 7) }
                .buttonStyle(.bordered)
        }
    }
    private func load() async {
        async let loadedDetail: SkillDetail? = try? LocalDataStore.shared.request("/skills/\(skillID)")
        async let loadedEntries: [PracticeEntry]? = try? LocalDataStore.shared.request("/skills/\(skillID)/practice")
        detail = await loadedDetail
        practiceEntries = await loadedEntries ?? []
    }
    private func setIcon(_ key: String?) async {
        let _: SkillSummary? = try? await LocalDataStore.shared.request("/skills/\(skillID)", method: "PATCH", body: SkillIconPayload(iconKey: key))
        showingIconPicker = false
        await load()
    }
}

struct CreateSkillView: View {
    @Environment(\.dismiss) private var dismiss
    let parent: SkillSummary?
    let onCreated: () -> Void
    @State private var name = ""
    @State private var description = ""
    @State private var selectedIconKey: String?
    @State private var showingIconPicker = false
    @State private var saving = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            Form {
                if let parent { Section("Parent skill") { Label(parent.name, systemImage: "arrow.turn.down.right") } }
                Section("What do you want to improve?") {
                    TextField(parent == nil ? "e.g. Singing" : "e.g. Pitch accuracy", text: $name)
                    TextField("Description (optional)", text: $description, axis: .vertical).lineLimit(2...4)
                }
                Section("Skill icon") {
                    Button { showingIconPicker = true } label: {
                        HStack(spacing: 14) {
                            SkillIcon(key: selectedIconKey, fallback: SkillIconCatalog.fallback(for: name))
                                .foregroundStyle(SystemTheme.gold).frame(width: 30, height: 30)
                            VStack(alignment: .leading) {
                                Text(selectedIconKey.flatMap { SkillIconCatalog.option(for: $0)?.title } ?? "Automatic")
                                Text("Choose from 150 fantasy icons").font(.caption).foregroundStyle(.secondary)
                            }
                            Spacer(); Image(systemName: "chevron.right").foregroundStyle(.secondary)
                        }
                    }.buttonStyle(.plain)
                }
                Section { Text(parent == nil ? "Start broad. Add sub-skills later when your practice becomes more specific." : "Practice logged here also advances every skill above it in the branch.").font(.footnote).foregroundStyle(.secondary) }
                if let errorMessage { Section { Text(errorMessage).foregroundStyle(.red) } }
            }
            .navigationTitle(parent == nil ? "New Skill" : "New Sub-skill")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Cancel") { dismiss() } }
                ToolbarItem(placement: .confirmationAction) { Button(saving ? "Creating…" : "Create") { Task { await create() } }.disabled(name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || saving) }
            }
        }
        .sheet(isPresented: $showingIconPicker) {
            SkillIconPicker(selectedKey: selectedIconKey) { key in selectedIconKey = key; showingIconPicker = false }
        }
    }
    private func create() async {
        saving = true; defer { saving = false }
        do {
            let _: SkillSummary = try await LocalDataStore.shared.request("/skills", method: "POST", body: CreateSkillPayload(name: name.trimmingCharacters(in: .whitespacesAndNewlines), description: description.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? nil : description, parentId: parent?.id, iconKey: selectedIconKey))
            onCreated(); dismiss()
        } catch { errorMessage = error.localizedDescription }
    }
}

struct LogPracticeView: View {
    @Environment(\.dismiss) private var dismiss
    let skill: SkillSummary
    let onSaved: () -> Void
    @State private var minutes = 20
    @State private var note = ""
    @State private var photoItems: [PhotosPickerItem] = []
    @State private var attachments: [PracticeDraftAttachment] = []
    @State private var recorder: AVAudioRecorder?
    @State private var isRecording = false
    @State private var saving = false
    @State private var result: PracticeResult?
    @State private var errorMessage: String?

    fileprivate init(
        skill: SkillSummary,
        initialNote: String = "",
        initialAttachments: [PracticeDraftAttachment] = [],
        initialIsRecording: Bool = false,
        onSaved: @escaping () -> Void
    ) {
        self.skill = skill
        self.onSaved = onSaved
        _note = State(initialValue: initialNote)
        _attachments = State(initialValue: initialAttachments)
        _isRecording = State(initialValue: initialIsRecording)
    }

    var body: some View {
        NavigationStack {
            Form {
                Section("Skill") { LabeledContent(skill.name, value: "Level \(skill.level)") }
                Section("Practice") {
                    Stepper("\(minutes) minutes", value: $minutes, in: 1...1_440, step: 5)
                    Text("One minute equals one skill EXP. Parent skills receive their configured share automatically.").font(.footnote).foregroundStyle(.secondary)
                }
                Section("Notes") {
                    TextEditor(text: $note)
                        .frame(minHeight: 110)
                        .overlay(alignment: .topLeading) {
                            if note.isEmpty {
                                Text("What did you practise? What improved or needs attention?")
                                    .foregroundStyle(.tertiary)
                                    .padding(.horizontal, 5)
                                    .padding(.vertical, 8)
                                    .allowsHitTesting(false)
                            }
                        }
                    HStack(spacing: 10) {
                        PhotosPicker(selection: $photoItems, maxSelectionCount: 6, matching: .images) {
                            Label("Photo", systemImage: "photo.on.rectangle.angled")
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.bordered)

                        Button {
                            Task { await toggleRecording() }
                        } label: {
                            Label(isRecording ? "Stop" : "Record", systemImage: isRecording ? "stop.circle.fill" : "waveform")
                                .frame(maxWidth: .infinity)
                                .foregroundStyle(isRecording ? .red : SystemTheme.cyan)
                        }
                        .buttonStyle(.bordered)
                    }
                    if isRecording {
                        Label("Recording in progress — tap Stop to attach", systemImage: "record.circle.fill")
                            .font(.caption.bold())
                            .foregroundStyle(.red)
                            .accessibilityAddTraits(.updatesFrequently)
                    }
                    if !attachments.isEmpty {
                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 10) {
                                ForEach(attachments) { attachment in
                                    attachmentTile(attachment)
                                }
                            }
                        }
                    }
                    Text("Add photos or a short audio reflection. Up to 8 attachments.")
                        .font(.caption).foregroundStyle(.secondary)
                }
                if let result {
                    Section("EXP awarded") {
                        ForEach(result.awards) { award in
                            HStack { Image(systemName: award.leveledUp ? "sparkles" : "arrow.up.right").foregroundStyle(award.leveledUp ? SystemTheme.gold : SystemTheme.cyan); VStack(alignment: .leading) { Text(award.name); if award.distance > 0 { Text("Parent roll-up").font(.caption).foregroundStyle(.secondary) } }; Spacer(); Text("+\(award.expGained)").font(.headline.monospaced()) }
                        }
                    }
                }
                if let errorMessage { Section { Text(errorMessage).foregroundStyle(.red) } }
            }
            .navigationTitle(result == nil ? "Log Practice" : "Practice Logged")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button(result == nil ? "Cancel" : "Done") { if result != nil { onSaved() }; dismiss() } }
                if result == nil { ToolbarItem(placement: .confirmationAction) { Button(saving ? "Saving…" : "Save") { Task { await save() } }.disabled(saving) } }
            }
            .onChange(of: photoItems) { _, items in
                Task { await importPhotos(items) }
            }
            .onDisappear {
                recorder?.stop()
                recorder = nil
                isRecording = false
            }
        }
    }
    @ViewBuilder
    private func attachmentTile(_ attachment: PracticeDraftAttachment) -> some View {
        ZStack(alignment: .topTrailing) {
            Group {
                if let thumbnail = attachment.thumbnail {
                    thumbnail.resizable().scaledToFill()
                } else {
                    VStack(spacing: 6) {
                        Image(systemName: "waveform")
                        Text("Audio").font(.caption2)
                    }
                }
            }
            .frame(width: 82, height: 72)
            .background(SystemTheme.surfaceRaised)
            .clipShape(RoundedRectangle(cornerRadius: 10))
            Button {
                attachments.removeAll { $0.id == attachment.id }
            } label: {
                Image(systemName: "xmark.circle.fill")
                    .symbolRenderingMode(.palette)
                    .foregroundStyle(.white, .black.opacity(0.65))
            }
            .offset(x: 5, y: -5)
        }
        .padding(.top, 5)
    }

    private func importPhotos(_ items: [PhotosPickerItem]) async {
        for (index, item) in items.enumerated() {
            guard attachments.count < 8,
                  let data = try? await item.loadTransferable(type: Data.self),
                  data.count <= 10 * 1024 * 1024,
                  !attachments.contains(where: { $0.data == data }) else { continue }
            let type = item.supportedContentTypes.first ?? .jpeg
            let thumbnail = UIImage(data: data).map { Image(uiImage: $0) }
            attachments.append(
                PracticeDraftAttachment(
                    kind: "image",
                    filename: "practice-photo-\(index + 1).\(type.preferredFilenameExtension ?? "jpg")",
                    contentType: type.preferredMIMEType ?? "image/jpeg",
                    data: data,
                    thumbnail: thumbnail
                )
            )
        }
    }

    private func toggleRecording() async {
        if isRecording {
            finishRecording()
            return
        }
        let allowed = await withCheckedContinuation { continuation in
            AVAudioApplication.requestRecordPermission { continuation.resume(returning: $0) }
        }
        guard allowed else {
            errorMessage = "Microphone access is required to attach a recording."
            return
        }
        do {
            let session = AVAudioSession.sharedInstance()
            try session.setCategory(.playAndRecord, mode: .spokenAudio, options: [.defaultToSpeaker])
            try session.setActive(true)
            let url = FileManager.default.temporaryDirectory.appendingPathComponent("practice-\(UUID().uuidString).m4a")
            let settings: [String: Any] = [
                AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
                AVSampleRateKey: 44_100,
                AVNumberOfChannelsKey: 1,
                AVEncoderAudioQualityKey: AVAudioQuality.medium.rawValue,
            ]
            let newRecorder = try AVAudioRecorder(url: url, settings: settings)
            newRecorder.record()
            recorder = newRecorder
            isRecording = true
        } catch {
            errorMessage = "Couldn’t start recording: \(error.localizedDescription)"
        }
    }

    private func finishRecording() {
        guard let recorder else { return }
        recorder.stop()
        if let data = try? Data(contentsOf: recorder.url), data.count <= 10 * 1024 * 1024 {
            attachments.append(
                PracticeDraftAttachment(
                    kind: "audio",
                    filename: recorder.url.lastPathComponent,
                    contentType: "audio/mp4",
                    data: data,
                    thumbnail: nil
                )
            )
        } else {
            errorMessage = "The recording is too large to attach."
        }
        self.recorder = nil
        isRecording = false
        try? AVAudioSession.sharedInstance().setActive(false)
    }

    private func save() async {
        saving = true; defer { saving = false }
        if isRecording { finishRecording() }
        let payload = PracticePayload(
            minutes: minutes,
            note: note.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? nil : note.trimmingCharacters(in: .whitespacesAndNewlines),
            attachments: attachments.map {
                PracticeAttachmentPayload(kind: $0.kind, filename: $0.filename, contentType: $0.contentType, dataBase64: $0.data.base64EncodedString())
            }
        )
        do { result = try await LocalDataStore.shared.request("/skills/\(skill.id)/practice", method: "POST", body: payload) }
        catch { errorMessage = error.localizedDescription }
    }
}

struct SkillsPreviewScreen: View {
    var body: some View { NavigationStack { SkillTreeContent(roots: SkillFixtures.roots).navigationTitle("Skill Tree") }.preferredColorScheme(.dark) }
}

struct PracticeJournalPreviewScreen: View {
    var body: some View {
        LogPracticeView(
            skill: SkillFixtures.roots[0].children[0].summary,
            onSaved: {}
        )
        .preferredColorScheme(.dark)
    }
}

struct PracticeJournalProofScreen: View {
    let includesAudio: Bool

    private static let samplePhoto: PracticeDraftAttachment = {
        let renderer = UIGraphicsImageRenderer(size: CGSize(width: 320, height: 220))
        let image = renderer.image { context in
            UIColor.systemIndigo.setFill()
            context.fill(CGRect(x: 0, y: 0, width: 320, height: 220))
            UIColor.systemTeal.setFill()
            context.cgContext.fillEllipse(in: CGRect(x: 85, y: 35, width: 150, height: 150))
            UIColor.white.withAlphaComponent(0.85).setFill()
            context.cgContext.fill(CGRect(x: 35, y: 178, width: 250, height: 8))
        }
        return PracticeDraftAttachment(
            kind: "image",
            filename: "practice-reference.png",
            contentType: "image/png",
            data: image.pngData() ?? Data(),
            thumbnail: Image(uiImage: image)
        )
    }()

    private static let sampleAudio = PracticeDraftAttachment(
        kind: "audio",
        filename: "practice-reflection.m4a",
        contentType: "audio/mp4",
        data: Data("deterministic audio preview".utf8),
        thumbnail: nil
    )

    var body: some View {
        LogPracticeView(
            skill: SkillFixtures.roots[0].children[0].summary,
            initialNote: "Focused on holding the interval cleanly. The second attempt felt more stable.",
            initialAttachments: includesAudio
                ? [Self.samplePhoto, Self.sampleAudio]
                : [Self.samplePhoto],
            onSaved: {}
        )
        .preferredColorScheme(.dark)
    }
}

struct PracticeRecordingProofScreen: View {
    var body: some View {
        LogPracticeView(
            skill: SkillFixtures.roots[0].children[0].summary,
            initialNote: "Speaking a quick reflection while the exercise is still fresh.",
            initialIsRecording: true,
            onSaved: {}
        )
        .preferredColorScheme(.dark)
    }
}

private enum SkillFixtures {
    static let roots = [
        SkillNode(id: 1, parentId: nil, name: "Singing", description: "Voice and performance", level: 4, exp: 72, expToNextLevel: 300, expProgress: 0.24, totalExpEarned: 540, isActive: true, depth: 1, createdAt: "2026-01-01", children: [
            SkillNode(id: 2, parentId: 1, name: "Pitch accuracy", description: nil, level: 3, exp: 160, expToNextLevel: 220, expProgress: 0.73, totalExpEarned: 360, isActive: true, depth: 2, createdAt: "2026-01-02", children: [
                SkillNode(id: 3, parentId: 2, name: "Interval jumps", description: nil, level: 2, exp: 65, expToNextLevel: 140, expProgress: 0.46, totalExpEarned: 165, isActive: true, depth: 3, createdAt: "2026-01-03", children: [])
            ]),
            SkillNode(id: 4, parentId: 1, name: "Breath control", description: nil, level: 2, exp: 90, expToNextLevel: 140, expProgress: 0.64, totalExpEarned: 190, isActive: true, depth: 2, createdAt: "2026-01-04", children: [])
        ]),
        SkillNode(id: 5, parentId: nil, name: "Programming", description: nil, level: 6, exp: 210, expToNextLevel: 500, expProgress: 0.42, totalExpEarned: 1_840, isActive: true, depth: 1, createdAt: "2026-01-05", children: [])
    ]
}

#Preview("Skill tree") { SkillsPreviewScreen() }
#Preview("Log practice") { LogPracticeView(skill: SkillFixtures.roots[0].children[0].summary, onSaved: {}).preferredColorScheme(.dark) }
