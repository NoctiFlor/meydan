# MEYDAN project guidance

- Edit `dist/game.js` and `shell.html`; generated HTML files are build outputs.
- Models are in `dist/assets`, beatmaps in `dist/beatmaps`, vendor modules in `dist/vendor`.
- Android source is in `android/src`; use `python build_apk.py` with JDK and SDK installed.
- `python build_standalone.py` needs only Python's standard library.
- After APK generation, run `python test_package.py` to check embedded assets.
- Preserve keyboard/mouse and independent multi-pointer controls. Movement uses input camera yaw, never the rendered camera direction.
- Dance inputs score on pointerdown only; compatibility click must not score.
- Never commit signing keys, generated APK/HTML/ZIP files, build caches or emulator disks.
- Do not claim a physical phone or Android emulator test based only on a desktop mobile viewport.
- Browser tests currently use Windows Chrome paths; adapt the harness before running them on Linux.
