"""Create a portable source archive; never include emulator disks or build caches."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parent
output = root / 'MEYDAN-kaynak.zip'
exclude_dirs = {'.git', '.openai', '.agents', '.codex', '__pycache__', 'test-avd', 'build', '.venv', 'tools-local'}
with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for file in sorted(root.rglob('*')):
        relative = file.relative_to(root)
        if not file.is_file() or any(part in exclude_dirs for part in relative.parts): continue
        if file.suffix in {'.zip', '.apk', '.idsig', '.log', '.pyc'}: continue
        archive.write(file, Path('MEYDAN') / relative)
with zipfile.ZipFile(output) as archive:
    assert archive.testzip() is None
    for required in ('build_apk.py', 'build_standalone.py', 'shell.html', 'dist/game.js', 'dist/gameplay.js', 'tests/gameplay.cjs',
                     'dist/assets/Michelle.glb', 'dist/assets/Xbot.glb', 'dist/beatmaps/meydan_demo.json',
                     'android/src/com/bahri/meydan/MainActivity.java', 'YENIDEN_DERLEME.md'):
        assert 'MEYDAN/' + required in archive.namelist(), required
print(f'Source ZIP ready: {output} ({output.stat().st_size:,} bytes)')
