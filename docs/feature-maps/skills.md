# Skills and practice

## Purpose

Each player owns a tree of skills. A node has its own level and EXP and at most one parent. Direct practice or completing a linked quest credits the selected skill and rolls a configured share upward through its ancestors.

## Public API

- `POST /skills` — create a root or child skill, optionally with an `icon_key`.
- `GET /skills` — nested forest, optionally including archived nodes.
- `GET /skills/{id}` — node with root-first path and immediate children.
- `PATCH /skills/{id}` — rename, describe, change `icon_key`, reparent, archive, or restore.
- `DELETE /skills/{id}` — archive the entire subtree.
- `POST /skills/{id}/practice` — credit practice minutes and return all awards.
- `GET /skills/{id}/practice` — newest-first practice journal for one skill.
- `GET /practice-attachments/{id}` — ownership-protected media download.

Contracts: `app/schemas/skill.py`; routes: `app/routers/skills.py`; model: `app/models/skill.py`; rules: `app/services/skills.py`.

## Invariants

- This is a tree, not a general graph: one parent gives one unambiguous award path.
- Reparenting must not create a cycle or exceed `max_skill_depth` (default 5).
- Names are normalized and unique among siblings.
- Archiving a node archives its subtree; no active child may hang below an archived parent.
- Archived nodes cannot receive direct or rolled-up practice.
- EXP uses a separately tunable curve (`skill_exp_curve_*`).
- `skill_exp_rollup` compounds once per ancestor; default 1.0 gives every ancestor full credit.
- Practice minutes are the canonical reward unit and match quest-linked skill credit.
- `icon_key` is optional visual metadata. The API validates its safe key shape; unknown keys remain valid so clients may evolve their catalogs independently.
- A practice entry and all attachment metadata/data are committed atomically with the EXP awards.

## Clients and gaps

- iOS exposes Skills as a primary tab in `SkillsView.swift`. It renders the nested tree, progression, breadcrumbs, children, root/sub-skill creation, and direct practice with visible ancestor roll-up awards. “Create routine” opens a quest preselected to the originating skill and exposes the full hierarchical skill tree so the player can switch the routine to a root skill or sub-skill before creation.
- Direct practice persists a timestamped journal entry atomically with its EXP awards. An entry can contain up to 10,000 characters of notes and eight image/audio attachments (10 MB each, 25 MB total); attachment downloads are ownership-protected. iOS provides a lightweight composer with duration, freeform notes, photo selection, audio recording, and journal history on the skill detail. Editing, reparenting, archive/restore, entry editing/deletion, attachment playback, and full-screen media viewing remain missing.
- Skills may use one of 150 curated, tintable Game-icons.net SVG sigils across ten searchable categories. The create form and skill detail expose `SkillIconPicker`; tree rows and Player State render the chosen icon. Missing selections use name-aware SF Symbol fallbacks. `SkillIconCreditsView` and `SkillIconAttribution.md` satisfy CC BY 3.0 attribution. Persistence is covered by Alembic revision `d2148c9f31aa` and D1 migration `0004_skill_icons.sql`.
- No web UI currently exposes skill management or direct practice. Quests can reference `skill_id` through backend authoring contracts.

## Verification

- Primary tests: `tests/test_skill_graph.py`, `tests/test_skill_leveling.py`; quest tests cover linked awards. Practice tests cover atomic journal persistence, attachment metadata/download, and EXP roll-up.
- Cover cycle/depth rejection, sibling uniqueness, subtree archive/restore, roll-up rounding/shares, multi-level gain, ownership, and quest/practice parity.
