"""Verify the installed-package payload against every source model and beatmap."""
from pathlib import Path
import base64
import json
import re
import zipfile

root = Path(__file__).resolve().parent
with zipfile.ZipFile(root / 'MEYDAN.apk') as apk:
    html = apk.read('assets/MEYDAN.html')
    assert html == (root / 'MEYDAN.html').read_bytes(), 'APK has stale HTML'
    assert len(apk.read('classes.dex')) > 0
    assert len(apk.read('AndroidManifest.xml')) > 0
text = html.decode('utf-8')
models = json.loads(re.search(r'window.EMBEDDED_ASSETS=(.*?);window.EMBEDDED_BEATMAPS=', text).group(1))
beatmaps = json.loads(re.search(r'window.EMBEDDED_BEATMAPS=(.*?);</script>', text).group(1))
for file in (root / 'dist/assets').glob('*.glb'):
    assert base64.b64decode(models[file.name]) == file.read_bytes(), file.name
    print('PASS: embedded model matches source:', file.name)
for file in (root / 'dist/beatmaps').glob('*.json'):
    assert beatmaps[file.stem] == json.loads(file.read_text(encoding='utf-8')), file.name
    print('PASS: embedded beatmap matches source:', file.name)
manifest = (root / 'android/AndroidManifest.xml').read_text(encoding='utf-8')
assert 'android.permission.INTERNET' not in manifest
assert 'android:debuggable="true"' not in manifest
print('PASS: APK payload, source identity, offline assets and non-debug source manifest')
