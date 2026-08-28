PRAGMA foreign_keys = ON;

CREATE TABLE constellations (
  id INTEGER NOT NULL PRIMARY KEY,
  code VARCHAR(64) NOT NULL,
  name VARCHAR(120) NOT NULL,
  epithet VARCHAR(200), description TEXT, domain VARCHAR(16),
  voice JSON NOT NULL, is_active BOOLEAN NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE UNIQUE INDEX ix_constellations_code ON constellations (code);

CREATE TABLE users (
  id INTEGER NOT NULL PRIMARY KEY,
  email VARCHAR(320) NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE TABLE players (
  id INTEGER NOT NULL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  name VARCHAR(80) NOT NULL,
  level INTEGER NOT NULL, exp INTEGER NOT NULL,
  total_exp_earned INTEGER NOT NULL, stat_points INTEGER NOT NULL,
  strength INTEGER NOT NULL, agility INTEGER NOT NULL,
  vitality INTEGER NOT NULL, intelligence INTEGER NOT NULL,
  perception INTEGER NOT NULL, timezone VARCHAR(64) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX ix_players_user_id ON players (user_id);

CREATE TABLE side_quests (
  id INTEGER NOT NULL PRIMARY KEY,
  title VARCHAR(200) NOT NULL, description TEXT,
  constellation_id INTEGER, catalog_code VARCHAR(64), lines JSON NOT NULL,
  is_challenge BOOLEAN NOT NULL, difficulty VARCHAR(2) NOT NULL,
  target_count INTEGER NOT NULL, unit VARCHAR(32), exp_reward INTEGER NOT NULL,
  stat_reward VARCHAR(16), stat_reward_amount INTEGER NOT NULL,
  penalty_exp INTEGER NOT NULL, status VARCHAR(16) NOT NULL,
  broadcast_at DATETIME NOT NULL, expires_at DATETIME,
  min_level INTEGER NOT NULL, max_level INTEGER, min_standing VARCHAR(16),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  FOREIGN KEY(constellation_id) REFERENCES constellations (id) ON DELETE SET NULL
);
CREATE INDEX ix_side_quests_constellation_id ON side_quests (constellation_id);
CREATE INDEX ix_side_quests_status ON side_quests (status);
CREATE INDEX ix_side_quests_is_challenge ON side_quests (is_challenge);
CREATE INDEX ix_side_quests_broadcast_at ON side_quests (broadcast_at);
CREATE INDEX ix_side_quests_catalog_code ON side_quests (catalog_code);
CREATE INDEX ix_side_quests_expires_at ON side_quests (expires_at);

CREATE TABLE constellation_favor (
  id INTEGER NOT NULL PRIMARY KEY,
  constellation_id INTEGER NOT NULL, player_id INTEGER NOT NULL,
  favor INTEGER NOT NULL, is_friend BOOLEAN NOT NULL,
  befriended_at DATETIME, unfriended_at DATETIME, may_ask_after DATETIME,
  offers_received INTEGER NOT NULL, completed INTEGER NOT NULL,
  declined INTEGER NOT NULL, expired INTEGER NOT NULL, failed INTEGER NOT NULL,
  first_seen_at DATETIME, last_seen_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  CONSTRAINT uq_favor_per_player UNIQUE (constellation_id, player_id),
  FOREIGN KEY(constellation_id) REFERENCES constellations (id) ON DELETE CASCADE,
  FOREIGN KEY(player_id) REFERENCES players (id) ON DELETE CASCADE
);
CREATE INDEX ix_constellation_favor_player_id ON constellation_favor (player_id);
CREATE INDEX ix_constellation_favor_constellation_id ON constellation_favor (constellation_id);

CREATE TABLE system_events (
  id INTEGER NOT NULL PRIMARY KEY, player_id INTEGER NOT NULL,
  event_type VARCHAR(32) NOT NULL, message VARCHAR(500) NOT NULL,
  payload JSON NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  FOREIGN KEY(player_id) REFERENCES players (id) ON DELETE CASCADE
);
CREATE INDEX ix_system_events_player_id ON system_events (player_id);
CREATE INDEX ix_system_events_created_at ON system_events (created_at);

CREATE TABLE quests (
  id INTEGER NOT NULL PRIMARY KEY, player_id INTEGER NOT NULL,
  title VARCHAR(200) NOT NULL, description TEXT, schedule VARCHAR(16) NOT NULL,
  schedule_days JSON, schedule_interval_days INTEGER, schedule_anchor DATE,
  week_start INTEGER NOT NULL, difficulty VARCHAR(2) NOT NULL,
  target_count INTEGER NOT NULL, unit VARCHAR(32), exp_reward INTEGER NOT NULL,
  stat_reward VARCHAR(16), stat_reward_amount INTEGER NOT NULL,
  is_active BOOLEAN NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  FOREIGN KEY(player_id) REFERENCES players (id) ON DELETE CASCADE
);
CREATE INDEX ix_quests_player_id ON quests (player_id);

CREATE TABLE quotes (
  id INTEGER NOT NULL PRIMARY KEY, player_id INTEGER NOT NULL,
  text TEXT NOT NULL, author VARCHAR(120), is_active BOOLEAN NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  FOREIGN KEY(player_id) REFERENCES players (id) ON DELETE CASCADE
);
CREATE INDEX ix_quotes_player_id ON quotes (player_id);

CREATE TABLE side_quest_offers (
  id INTEGER NOT NULL PRIMARY KEY, side_quest_id INTEGER NOT NULL,
  player_id INTEGER NOT NULL, status VARCHAR(16) NOT NULL,
  progress INTEGER NOT NULL, target_count INTEGER NOT NULL,
  expires_at DATETIME, offered_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  responded_at DATETIME, completed_at DATETIME,
  CONSTRAINT uq_side_quest_offer_per_player UNIQUE (side_quest_id, player_id),
  FOREIGN KEY(side_quest_id) REFERENCES side_quests (id) ON DELETE CASCADE,
  FOREIGN KEY(player_id) REFERENCES players (id) ON DELETE CASCADE
);
CREATE INDEX ix_side_quest_offers_offered_at ON side_quest_offers (offered_at);
CREATE INDEX ix_side_quest_offers_player_id ON side_quest_offers (player_id);
CREATE INDEX ix_side_quest_offers_status ON side_quest_offers (status);
CREATE INDEX ix_side_quest_offers_side_quest_id ON side_quest_offers (side_quest_id);
CREATE INDEX ix_side_quest_offers_expires_at ON side_quest_offers (expires_at);

CREATE TABLE side_quest_preferences (
  id INTEGER NOT NULL PRIMARY KEY, player_id INTEGER NOT NULL,
  is_opted_in BOOLEAN NOT NULL, frequency VARCHAR(16) NOT NULL,
  max_difficulty VARCHAR(2), auto_accept BOOLEAN NOT NULL,
  opted_in_at DATETIME, opted_out_at DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL, updated_at DATETIME,
  FOREIGN KEY(player_id) REFERENCES players (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX ix_side_quest_preferences_player_id ON side_quest_preferences (player_id);

CREATE TABLE friendship_requests (
  id INTEGER NOT NULL PRIMARY KEY, constellation_id INTEGER NOT NULL,
  player_id INTEGER NOT NULL, status VARCHAR(16) NOT NULL,
  message TEXT, verdict_reason TEXT, challenge_offer_id INTEGER,
  requested_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  decided_at DATETIME, resolved_at DATETIME,
  FOREIGN KEY(constellation_id) REFERENCES constellations (id) ON DELETE CASCADE,
  FOREIGN KEY(player_id) REFERENCES players (id) ON DELETE CASCADE,
  FOREIGN KEY(challenge_offer_id) REFERENCES side_quest_offers (id) ON DELETE SET NULL
);
CREATE INDEX ix_friendship_requests_requested_at ON friendship_requests (requested_at);
CREATE INDEX ix_friendship_requests_player_id ON friendship_requests (player_id);
CREATE INDEX ix_friendship_requests_status ON friendship_requests (status);
CREATE INDEX ix_friendship_requests_constellation_id ON friendship_requests (constellation_id);

CREATE TABLE quest_instances (
  id INTEGER NOT NULL PRIMARY KEY, quest_id INTEGER NOT NULL, player_id INTEGER NOT NULL,
  period_start DATE NOT NULL, period_end DATE, progress INTEGER NOT NULL,
  target_count INTEGER NOT NULL, status VARCHAR(16) NOT NULL,
  completed_at DATETIME, created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  CONSTRAINT uq_quest_instance_per_period UNIQUE (quest_id, period_start),
  FOREIGN KEY(quest_id) REFERENCES quests (id) ON DELETE CASCADE,
  FOREIGN KEY(player_id) REFERENCES players (id) ON DELETE CASCADE
);
CREATE INDEX ix_quest_instances_player_id ON quest_instances (player_id);
CREATE INDEX ix_quest_instances_quest_id ON quest_instances (quest_id);
CREATE INDEX ix_quest_instances_period_end ON quest_instances (period_end);
CREATE INDEX ix_quest_instances_period_start ON quest_instances (period_start);

CREATE TABLE penalties (
  id INTEGER NOT NULL PRIMARY KEY, player_id INTEGER NOT NULL,
  quest_instance_id INTEGER, side_quest_offer_id INTEGER,
  reason VARCHAR(255) NOT NULL, exp_lost INTEGER NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  FOREIGN KEY(player_id) REFERENCES players (id) ON DELETE CASCADE,
  FOREIGN KEY(quest_instance_id) REFERENCES quest_instances (id) ON DELETE SET NULL,
  FOREIGN KEY(side_quest_offer_id) REFERENCES side_quest_offers (id) ON DELETE SET NULL
);
CREATE INDEX ix_penalties_player_id ON penalties (player_id);
