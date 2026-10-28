"""Build an offline, locally signed APK with installed Android SDK tools.

No Gradle download or external Android dependencies are required.
"""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
SDK = Path(os.environ.get('ANDROID_SDK_ROOT') or os.environ.get('ANDROID_HOME') or
           Path.home() / ('AppData/Local/Android/Sdk' if os.name == 'nt' else 'Android/Sdk'))
java_home = os.environ.get('JAVA_HOME')
if not java_home:
    compiler = shutil.which('javac')
    java_home = str(Path(compiler).resolve().parent.parent) if compiler else ''
JAVA = Path(java_home)
TOOLS = SDK / 'build-tools' / os.environ.get('ANDROID_BUILD_TOOLS', '36.0.0')
PLATFORM = SDK / 'platforms/android-36/android.jar'
OUT = ROOT / 'android/build'

def executable(directory, name):
    return directory / (name + '.exe' if os.name == 'nt' else name)

def run(*args):
    subprocess.run([str(a) for a in args], check=True, cwd=ROOT)

def main():
    java = executable(JAVA / 'bin', 'java')
    for tool in (executable(TOOLS, 'aapt'), PLATFORM, executable(JAVA / 'bin', 'javac'), TOOLS / 'lib/d8.jar'):
        if not tool.exists():
            raise SystemExit(f'Required Android build tool missing: {tool}')
    OUT.mkdir(parents=True, exist_ok=True)
    assets = OUT / 'assets'
    classes = OUT / 'classes'
    dex = OUT / 'dex'
    for directory in (assets, classes, dex): directory.mkdir(exist_ok=True)
    # Remove stale bytecode when an anonymous class is removed or renamed.
    for old in classes.rglob('*.class'): old.unlink()
    for old in dex.glob('*.dex'): old.unlink()
    run(sys.executable, ROOT / 'build_standalone.py')
    shutil.copy2(ROOT / 'MEYDAN.html', assets / 'MEYDAN.html')
    unsigned = OUT / 'unsigned.apk'
    manifest = ROOT / 'android/AndroidManifest.xml'
    if '--debug' in sys.argv:
        debug_manifest = OUT / 'AndroidManifest.xml'
        debug_manifest.write_text(manifest.read_text(encoding='utf-8').replace('<application ', '<application android:debuggable="true" '), encoding='utf-8')
        manifest = debug_manifest
    run(executable(TOOLS, 'aapt'), 'package', '-f', '-M', manifest,
        '-S', ROOT / 'android/res', '-A', assets, '-I', PLATFORM, '-F', unsigned)
    run(executable(JAVA / 'bin', 'javac'), '--release', '8', '-encoding', 'UTF-8', '-classpath', PLATFORM,
        '-d', classes, ROOT / 'android/src/com/bahri/meydan/MainActivity.java')
    run(java, '-cp', TOOLS / 'lib/d8.jar', 'com.android.tools.r8.D8',
        '--lib', PLATFORM, '--min-api', '26', '--output', dex, *sorted(classes.rglob('*.class')))
    with zipfile.ZipFile(unsigned, 'a', compression=zipfile.ZIP_DEFLATED) as apk:
        apk.write(dex / 'classes.dex', 'classes.dex')
    aligned = OUT / 'aligned.apk'
    run(executable(TOOLS, 'zipalign'), '-f', '4', unsigned, aligned)
    key = Path(os.environ.get('MEYDAN_KEYSTORE', str(ROOT / 'android/local-signing.p12')))
    if not key.exists():
        if os.environ.get('CI'):
            raise SystemExit('CI signing key missing. Set the MEYDAN_KEYSTORE_BASE64 repository secret.')
        run(executable(JAVA / 'bin', 'keytool'), '-genkeypair', '-keystore', key, '-storetype', 'PKCS12',
            '-storepass', 'android', '-keypass', 'android', '-alias', 'meydan-local',
            '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000',
            '-dname', 'CN=MEYDAN Local Build, O=MEYDAN, C=TR')
    output = ROOT / ('MEYDAN-test.apk' if '--debug' in sys.argv else 'MEYDAN.apk')
    signer = TOOLS / 'lib/apksigner.jar'
    run(java, '-jar', signer, 'sign', '--ks', key, '--ks-key-alias', 'meydan-local',
        '--ks-pass', 'pass:android', '--key-pass', 'pass:android', '--out', output, aligned)
    run(java, '-jar', signer, 'verify', '--verbose', output)
    run(executable(TOOLS, 'zipalign'), '-c', '4', output)
    print(f'APK ready: {output} ({output.stat().st_size:,} bytes)')

if __name__ == '__main__': main()
