from pathlib import Path


game = (Path(__file__).parent / "dist" / "game.js").read_text(encoding="utf-8")


def require(label: str, condition: bool) -> None:
    assert condition, label
    print(f"PASS: {label}")


require("plaza uses one shared ground mesh", "const plazaGround=new THREE.Mesh" in game)
require("legacy 441-mesh floor loop is removed", "for(let x=-20;x<=20;x+=2)for(let z=-20;z<=20;z+=2)block" not in game)
require("mobile profile caps pixel density", "compactDevice?1.35:1.7" in game)
require("mobile profile caps shadow resolution", "compactDevice?1024:2048" in game)
require("decorative lamps can omit real point lights", "castsLight=false" in game)
require("dance stage has a circular surface", "new THREE.CircleGeometry(2.48,48)" in game)
require("dance stage keeps the interaction landmark", "stageDisc.position.set(1.5,.09,-1.5)" in game)

print("ALL SCENE FOUNDATION CHECKS PASSED")
