---
name: evolve-product
description: Evolve the Life System product by turning its maintained new-user and daily-use UX feedback into prioritized, implemented, and verified product improvements. Use when asked to improve, upgrade, refine, or continue evolving the Life System experience from the product review.
---

# Evolve Product

Upgrade Life System from observed user friction, not from feature novelty alone.

Before choosing work, read [the complete product feedback and development history](../../../docs/daily-use-ux-review.md). Treat it as the cumulative source of truth for the product's new-user and daily-use problems, priorities, roadmap, acceptance scenarios, decisions, and completed improvements. Check the current implementation before assuming a recorded issue is still present.

## Preserve product-development history

The feedback document is an append-only product-development record. Every invocation must preserve all feedback and history already present in it.

- Read the entire existing document before updating it.
- Never replace, truncate, regenerate, or broadly rewrite the document.
- Never delete an old finding because it was fixed, superseded, duplicated, or is no longer reproducible. Preserve the original account and append its later status.
- Record new review findings, implementation decisions, verification evidence, changed priorities, and corrections as a new dated history entry. Clearly distinguish newly observed feedback from carried-forward findings.
- When work resolves or changes an existing finding, append a dated resolution update that identifies the original finding, describes what changed, and records verification. Do not edit the original finding into a description of the new state.
- If an earlier entry was wrong, append a correction that explains the error; retain the earlier entry for traceability.
- Before finishing, inspect the diff of the feedback document. Existing history may move or change only when the user explicitly requests a history migration or correction; otherwise restore it and keep only additive edits.

Use stable finding identifiers when adding new feedback so future entries can refer to it without rewriting earlier text. If an older finding has no identifier, refer to its existing heading verbatim in the appended update rather than retroactively restructuring the historical document.

## Choose the next improvement

Use the user's requested area when one is given. Otherwise select the highest-priority unfinished item in the feedback, ordered by:

1. Progression correctness and data durability
2. Accessibility blockers
3. First-session activation
4. Speed and clarity of the daily loop
5. Long-term history, organization, and reflection
6. Additional game-layer richness

Prefer a coherent vertical improvement that a player can experience end to end. Do not add new systems while a dependency in the core quest → action → reward → persisted progress loop remains unreliable.

## Upgrade the product

- Translate the relevant feedback into concrete behavior and acceptance criteria before editing.
- Inspect the current UI, models, persistence behavior, feature maps, and tests that own that behavior.
- Preserve the app's Souls/manhwa identity while making consequences and controls understandable in plain language.
- Keep player EXP, skill EXP, quest state, journal data, events, widgets, and sync-visible state consistent whenever an action affects more than one of them.
- Design frequent daily actions for minimal navigation and reversible recovery where accidental input is plausible.
- Handle empty, populated, loading, failure, completion, and relaunch states as part of the feature rather than as follow-up polish.
- Maintain accessibility at the same time as the primary layout, including Dynamic Type, VoiceOver labels and order, contrast, touch targets, Reduce Motion, and non-color state cues where relevant.
- Update the relevant feature map and append to the product-development history when behavior, contracts, priorities, or finding status changes. Mark findings resolved only in a new dated entry and only after runtime verification.

For changes under `ios/`, read [the harness skill](../harness/SKILL.md) completely and follow it. Build and exercise the real app in Simulator; a compile alone is not sufficient for navigation, persistence, or visual work.

## Verify the player outcome

Verify the smallest realistic journey that proves the improvement, including relaunch persistence when state changes. Use the acceptance scenarios in the feedback as the regression baseline and add focused XCTest or XCUITest coverage when the behavior is repeatable or high risk.

For UI work, inspect screenshots at the normal text size and at a relevant accessibility size. For progression work, confirm every affected surface shows the same durable result after relaunch. For sync or widget work, state clearly which behavior was exercised in Simulator and which still requires a physical device or multi-device validation.

Finish by reporting:

- The player-facing outcome
- Which feedback finding or acceptance scenario was addressed
- What was verified and on which device/runtime
- Evidence paths and any remaining limitations
- The dated history entry appended to the feedback document
