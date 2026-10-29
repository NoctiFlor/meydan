# MEYDAN development roadmap

This document is the execution contract for the autonomous agent. Each milestone must preserve earlier tests and add its own acceptance checks.

## Definition of done for every milestone

- [ ] Feature works in standalone HTML.
- [ ] Android package still builds.
- [ ] Existing movement, camera, lifecycle and rhythm tests pass.
- [ ] New behavior has an automated test where technically practical.
- [ ] Real-device-only claims remain marked unverified until tested.
- [ ] Documentation and screenshots are updated.

## 0. Foundation and real-device baseline

- [ ] Record FPS, load time, memory and input feel on the Xiaomi 13T Pro.
- [ ] Test common 16:9, 19.5:9 and tablet aspect ratios.
- [ ] Add a reproducible smoke-test command and failure report.
- [ ] Establish low/medium/high quality presets.

Exit: a measured baseline exists and no regression is hidden.

## 1. Visual plaza redesign

- [ ] Replace the empty test arena with a readable central plaza.
- [ ] Add central dance stage, fountain landmark, cafe/social zone, shop frontage and upper promenade.
- [ ] Use instancing, baked lighting and mobile-friendly materials.
- [ ] Add collision boundaries and navigation-safe walking paths.
- [ ] Keep all activity zones visible or signposted from the spawn route.

Exit: the plaza looks intentional, remains navigable and meets the baseline performance budget.

## 2. Character and camera feel

- [ ] Add walk/run blend, turn smoothing and idle variation.
- [ ] Improve follow-camera damping, obstruction handling and distance limits.
- [ ] Preserve continuous 360-degree joystick movement and independent second-pointer camera.
- [ ] Add character selection foundation without committing unlicensed models.

Exit: movement feels consistent on keyboard, touch and Android lifecycle transitions.

## 3. Dance presentation and animation

- [ ] Create clear enter-stage, ready, dance and exit states.
- [ ] Synchronize animation cues with the existing horizontal sequence and timing confirmation.
- [ ] Add stage camera framing without stealing movement/camera input ownership.
- [ ] Restore exploration cleanly after success, failure or cancellation.

Exit: the avatar visibly performs the rhythm action and all exits return to a stable exploration state.

## 4. Scoring, combo and results

- [ ] Add Perfect/Good/Miss judgements with documented timing windows.
- [ ] Add combo, score multiplier and per-round feedback.
- [ ] Add a readable result screen with score, accuracy, max combo and grade.
- [ ] Prevent duplicate pointer/click scoring and delayed-frame multiple misses.

Exit: deterministic unit tests cover timing boundaries and repeated input.

## 5. Multiple songs and beatmaps

- [ ] Define a versioned beatmap schema and validation tool.
- [ ] Add at least three original/licensed demo tracks or synthesized arrangements.
- [ ] Add difficulty metadata, preview and song selection.
- [ ] Handle malformed/missing beatmaps without crashing.

Exit: three distinct playable charts load offline and validate during CI.

## 6. Main menu, saves and progression

- [ ] Add new game/continue, settings and profile shell.
- [ ] Save settings, scores, unlocks and progression locally with schema versioning.
- [ ] Add safe migration and corrupted-save recovery.
- [ ] Add reset-save confirmation.

Exit: progress survives reload/app restart and corrupted data cannot block startup.

## 7. NPCs, shops and social activities

- [ ] Add lightweight NPC state machines and interaction prompts.
- [ ] Add non-monetized prototype currency and cosmetic shop inventory.
- [ ] Add cafe/seating/photo/dance-invite activity hooks.
- [ ] Keep economy values data-driven and offline-safe.

Exit: the plaza has a short repeatable play loop beyond free walking.

## 8. Online multiplayer foundation

- [ ] Write the authoritative networking and privacy design before implementation.
- [ ] Prototype room creation/join, player transforms and emotes in an isolated branch.
- [ ] Add interpolation, reconnect and abuse-rate limits.
- [ ] Do not enable public accounts, purchases, voice, analytics or production servers without explicit approval.

Exit: a private test room supports stable movement and emotes without weakening the offline game.

## Recommended execution order

Work strictly from milestone 0 through 8. Visual work may use placeholders, but online work must not begin before offline saves and the core loop are stable.
