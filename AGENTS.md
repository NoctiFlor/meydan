# MEYDAN project guidance

## Autonomous operating mode

- Work autonomously inside the requested milestone: inspect, reproduce, fix, test, and iterate without asking for approval for ordinary reversible code changes.
- Never hide a failing test or weaken an assertion to make a build green. Fix the cause or document the blocker.
- Keep changes small and milestone-scoped. Do not attempt multiple major roadmap milestones in one commit.
- Before editing, read `docs/ROADMAP.md` and select the first incomplete milestone whose prerequisites pass.
- Preserve the last known working build. Use a feature branch and do not push directly to `main`.
- After every change, run the narrowest relevant test, then the full available regression set before declaring completion.
- If a change fails, diagnose and retry with a different evidence-based fix. Stop only for missing credentials/assets, destructive migrations, legal/licensing uncertainty, paid services, or a product choice that materially changes the game.
- Commit only when tests pass. Commit messages should name the milestone and user-visible result.
- Update the milestone checklist and test evidence in `docs/ROADMAP.md`.
- Do not claim a physical-phone test unless a real device was connected and tested.

## Safety boundaries

- Never commit signing keys, tokens, generated APK/HTML/ZIP files, build caches, emulator disks, or copyrighted Jadde music/art.
- Do not delete working features, saves, or assets without explicit approval.
- New third-party assets must have a documented compatible licence.
- Online accounts, purchases, analytics, moderation, and public deployment require explicit approval before activation.

## Technical invariants

- Edit `dist/game.js` and `shell.html`; generated HTML files are build outputs.
- Shared analog input and sequence/timing rules live in `dist/gameplay.js`; run `node tests/gameplay.cjs` after changing them.
- Dance uses horizontal sequence entry followed by a single timing confirmation. Direction entry never awards points; wrong directions reset the sequence.
- Joystick input is a continuous vector with radial deadzone, not four/eight direction snapping. Keep second-pointer camera ownership independent.
- Models are in `dist/assets`, beatmaps in `dist/beatmaps`, vendor modules in `dist/vendor`.
- Android source is in `android/src`; use `python build_apk.py` with JDK and SDK installed.
- `python build_standalone.py` needs only Python's standard library.
- After APK generation, run `python test_package.py` to check embedded assets.
- Preserve keyboard/mouse and independent multi-pointer controls. Movement uses input camera yaw, never the rendered camera direction.
- Dance inputs score on pointerdown only; compatibility click must not score.
- Browser tests currently use Windows Chrome paths; adapt the harness before running them on Linux.
