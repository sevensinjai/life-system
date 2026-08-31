CREATE TABLE practice_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    minutes INTEGER NOT NULL,
    note TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_practice_entries_player_id ON practice_entries(player_id);
CREATE INDEX ix_practice_entries_skill_id ON practice_entries(skill_id);
CREATE INDEX ix_practice_entries_created_at ON practice_entries(created_at);

CREATE TABLE practice_attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id INTEGER NOT NULL REFERENCES practice_entries(id) ON DELETE CASCADE,
    kind VARCHAR(12) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    byte_count INTEGER NOT NULL,
    data BLOB NOT NULL
);

CREATE INDEX ix_practice_attachments_entry_id ON practice_attachments(entry_id);
