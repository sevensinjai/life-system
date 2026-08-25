-- Skill tree plus the one-minute-per-EXP quest reward model.
-- Existing quest EXP values become estimated practice minutes.

CREATE TABLE skills (
  id INTEGER NOT NULL PRIMARY KEY,
  player_id INTEGER NOT NULL,
  parent_id INTEGER,
  name VARCHAR(80) NOT NULL,
  description TEXT,
  level INTEGER NOT NULL DEFAULT 1,
  exp INTEGER NOT NULL DEFAULT 0,
  total_exp_earned INTEGER NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  FOREIGN KEY(player_id) REFERENCES players (id) ON DELETE CASCADE,
  FOREIGN KEY(parent_id) REFERENCES skills (id) ON DELETE CASCADE
);
CREATE INDEX ix_skills_player_id ON skills (player_id);
CREATE INDEX ix_skills_parent_id ON skills (parent_id);

ALTER TABLE quests ADD COLUMN skill_id INTEGER REFERENCES skills (id) ON DELETE SET NULL;
ALTER TABLE quests ADD COLUMN skill_exp_reward INTEGER NOT NULL DEFAULT 0;
ALTER TABLE quests ADD COLUMN units_per_minute REAL;
ALTER TABLE quests ADD COLUMN practice_minutes INTEGER NOT NULL DEFAULT 1;
CREATE INDEX ix_quests_skill_id ON quests (skill_id);

UPDATE quests
SET practice_minutes = CASE WHEN exp_reward > 0 THEN exp_reward ELSE 1 END;

ALTER TABLE quest_instances ADD COLUMN practice_minutes INTEGER NOT NULL DEFAULT 1;
UPDATE quest_instances
SET practice_minutes = COALESCE(
  (SELECT practice_minutes FROM quests WHERE quests.id = quest_instances.quest_id),
  1
);
