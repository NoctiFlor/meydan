"""Native Android smoke test of the delivered, non-debug APK on our test emulator."""
from pathlib import Path
import os
import re
import subprocess
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
SDK = Path(os.environ.get('ANDROID_SDK_ROOT', str(Path.home() / 'AppData/Local/Android/Sdk')))
ADB = SDK / 'platform-tools/adb.exe'
SERIAL = 'emulator-5554'

def adb(*args):
    return subprocess.check_output([str(ADB), '-s', SERIAL, *args], text=True, encoding='utf-8').strip()

def tree():
    adb('shell', 'uiautomator', 'dump', '/sdcard/meydan-release-ui.xml')
    return ET.fromstring(adb('shell', 'cat', '/sdcard/meydan-release-ui.xml'))

def find(ui, text):
    return next((n for n in ui.iter('node') if text in n.get('text', '')), None)

def tap(node):
    assert node is not None
    x1, y1, x2, y2 = map(int, re.findall(r'\d+', node.get('bounds')))
    adb('shell', 'input', 'tap', str((x1+x2)//2), str((y1+y2)//2))

print(adb('install', '-r', str(ROOT / 'MEYDAN.apk')))
assert adb('shell', 'pm', 'clear', 'com.bahri.meydan') == 'Success'
adb('shell', 'cmd', 'connectivity', 'airplane-mode', 'enable')
adb('shell', 'logcat', '-c')
print(adb('shell', 'am', 'start', '-W', '-n', 'com.bahri.meydan/.MainActivity'))
for _ in range(15):
    ui = tree()
    prompt = next((n for n in ui.iter('node') if n.get('resource-id') == 'com.android.systemui:id/ok'), None)
    if prompt is not None: tap(prompt); continue
    assert find(ui, 'Başlatma sorunu') is None
    if find(ui, 'Bekliyor') is not None: break
    time.sleep(1)
else: raise AssertionError('Game did not become ready in release APK')
assert adb('shell', 'settings', 'get', 'global', 'airplane_mode_on') == '1'
print('PASS: delivered APK installs, clears data and cold-loads offline on Android', flush=True)
time.sleep(1);tap(find(ui, 'Kontroller')); time.sleep(.8)
ui = tree(); assert find(ui, 'Oyuna dön') is not None
adb('shell', 'input', 'keyevent', '4'); time.sleep(.3)
ui = tree(); assert find(ui, 'Oyuna dön') is None
print('PASS: native Back dismisses controls in non-debug APK', flush=True)
tap(find(ui, 'Dans et')); time.sleep(.4)
ui = tree(); assert find(ui, 'Dansı Başlat') is not None
adb('shell', 'input', 'keyevent', '4'); time.sleep(.3)
ui = tree(); assert find(ui, 'Dansı Başlat') is None and find(ui, 'Oyuna dön') is None
print('PASS: native Back dismisses song selection before pause in non-debug APK', flush=True)
logs = adb('shell', 'logcat', '-d', '-s', 'AndroidRuntime:E', 'chromium:I')
assert 'FATAL EXCEPTION' not in logs and 'Uncaught ' not in logs
(ROOT / 'android/emulator-release.png').write_bytes(subprocess.check_output([str(ADB), '-s', SERIAL, 'exec-out', 'screencap', '-p']))
print('ALL DELIVERED APK SMOKE TESTS PASSED', flush=True)
