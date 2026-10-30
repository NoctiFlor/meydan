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
- [x] Add a reproducible smoke-test command and failure report.
- [x] Establish low/medium/high quality presets.

Exit: a measured baseline exists and no regression is hidden.

## 1. Visual plaza redesign

- [x] Replace the empty test arena with a readable central plaza.
- [ ] Add central dance stage, fountain landmark, cafe/social zone, shop frontage and upper promenade.
- [ ] Use instancing, baked lighting and mobile-friendly materials.
- [x] Add collision boundaries and navigation-safe walking paths.
- [ ] Keep all activity zones visible or signposted from the spawn route.

Exit: the plaza looks intentional, remains navigable and meets the baseline performance budget.

## 2. Character and camera feel

- [ ] Add walk/run blend, turn smoothing and idle variation.
- [x] Improve follow-camera damping, obstruction handling and distance limits.
- [x] Preserve continuous 360-degree joystick movement and independent second-pointer camera.
- [x] Add character selection foundation without committing unlicensed models.

Exit: movement feels consistent on keyboard, touch and Android lifecycle transitions.

## 3. Dance presentation and animation

- [ ] Create clear enter-stage, ready, dance and exit states.
- [ ] Synchronize animation cues with the existing horizontal sequence and timing confirmation.
- [ ] Add stage camera framing without stealing movement/camera input ownership.
- [ ] Restore exploration cleanly after success, failure or cancellation.

Exit: the avatar visibly performs the rhythm action and all exits return to a stable exploration state.

## 4. Scoring, combo and results

- [x] Add Perfect/Good/Miss judgements with documented timing windows.
- [x] Add combo, score multiplier and per-round feedback.
- [x] Add a readable result screen with score, accuracy, max combo and grade.
- [x] Prevent duplicate pointer/click scoring and delayed-frame multiple misses.

Exit: deterministic unit tests cover timing boundaries and repeated input.

## 5. Multiple songs and beatmaps

- [ ] Define a versioned beatmap schema and validation tool.
- [x] Add at least three original/licensed demo tracks or synthesized arrangements.
- [x] Add difficulty metadata, preview and song selection.
- [x] Handle malformed/missing beatmaps without crashing.

Exit: three distinct playable charts load offline and validate during CI.

## 6. Main menu, saves and progression

- [x] Add new game/continue, settings and profile shell.
- [x] Save settings, scores, unlocks and progression locally with schema versioning.
- [x] Add safe migration and corrupted-save recovery.
- [x] Add reset-save confirmation.

Exit: progress survives reload/app restart and corrupted data cannot block startup.

## 7. NPCs, shops and social activities

- [x] Add lightweight NPC state machines and interaction prompts.
- [x] Add non-monetized prototype currency and cosmetic shop inventory.
- [x] Add cafe/seating/photo/dance-invite activity hooks.
- [x] Keep economy values data-driven and offline-safe.

Exit: the plaza has a short repeatable play loop beyond free walking.

## 8. Online multiplayer foundation

- [x] Write and test the private-room protocol and privacy constraints before transport implementation.
- [x] Prototype room creation/join, player transforms and emotes as an isolated offline module.
- [x] Add interpolation, reconnect and abuse-rate limits.
- [x] Do not enable public accounts, purchases, voice, analytics or production servers without explicit approval.

Exit: a private test room supports stable movement and emotes without weakening the offline game.

## Recommended execution order

Work strictly from milestone 0 through 8. Visual work may use placeholders, but online work must not begin before offline saves and the core loop are stable.
