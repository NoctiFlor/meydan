"""Run MEYDAN's deterministic offline smoke suite without browser or Android SDK."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def run(*command):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run([str(part) for part in command], cwd=ROOT, check=True)


def main():
    for test in sorted((ROOT / "tests").glob("*.cjs")):
        run("node", test)
    run(sys.executable, ROOT / "test_scene_foundation.py")
    run("node", "--check", ROOT / "dist/game.js")
    run(sys.executable, ROOT / "build_standalone.py")
    print("ALL OFFLINE SMOKE TESTS PASSED")


if __name__ == "__main__":
    main()
