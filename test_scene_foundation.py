from pathlib import Path


game = (Path(__file__).parent / "dist" / "game.js").read_text(encoding="utf-8")
shell = (Path(__file__).parent / "shell.html").read_text(encoding="utf-8")


def require(label: str, condition: bool) -> None:
    assert condition, label
    print(f"PASS: {label}")


require("plaza uses one shared ground mesh", "const plazaGround=new THREE.Mesh" in game)
require("legacy 441-mesh floor loop is removed", "for(let x=-20;x<=20;x+=2)for(let z=-20;z<=20;z+=2)block" not in game)
require("quality budget caps pixel density", "worldBudget.pixelRatio" in game)
require("quality budget caps shadow resolution", "worldBudget.shadowMap" in game)
require("decorative lamps can omit real point lights", "castsLight=false" in game)
require("dance stage has a circular surface", "new THREE.CircleGeometry(2.48,48)" in game)
require("dance stage keeps the interaction landmark", "stageDisc.position.set(1.5,.09,-1.5)" in game)
require("social NPC simulation is integrated", "updateSocialActors(dt)" in game)
require("offline progression records dance results", "progressionStore.recordScore" in game)
require("activity rewards feed the offline economy", "cosmeticEconomy.grantCoins(reward.coins)" in game)
require("shop supports purchase and equip", "cosmeticEconomy.purchase(item.id)" in game and "cosmeticEconomy.equip(item.id)" in game)
require("reset clears progression and cosmetic economy", "localStorage.removeItem('meydan.economy')" in game)
require("camera checks plaza occluders", "cameraRay.intersectObjects(cameraOccluders" in game)
require("all three original songs are registered", all(song in game for song in ("meydan_demo", "gece_isiklari", "sahil_ritmi")))
require("dance HUD has left control, center beatmap and right confirm zones", all(name in shell for name in ('class="dance-left"', 'class="dance-center"', 'class="dance-confirm-wrap"')))
require("dance direction buttons use an analog disc layout", ".keys{position:absolute;inset:1%;display:grid" in shell and ".key:nth-child(4){grid-column:3;grid-row:2" in shell)
require("normal movement joystick is hidden during dance", 'body[data-dancing="true"] #joystick{display:none!important}' in shell)
require("dance judgements have visible animated feedback", 'id="dance-feedback"' in shell and "showDanceFeedback(kind" in game and "'PERFECT!'" in game)
require("wrong direction visibly restarts the full phrase", "showDanceFeedback('wrong','BAŞTAN!')" in game and "result==='wrong'" in game)
require("wrong direction also clears combo and entered-arrow visuals", "danceGame.combo=0" in game and "row.classList.add('resetting')" in game)
require("main menu offers continue, new game and settings", all(item in shell for item in ('id="continue-game"', 'id="new-game"', 'id="start-settings"')))
require("new profiles collect a name and avatar style", 'id="profile-form"' in shell and 'name="avatar"' in shell and "progressionStore.createProfile" in game)
require("front end blocks plaza movement until entry", "frontEndOpen&&!paused" in game and "function enterPlaza" in game)
require("legacy saves remain available through continue", "profile.created" in game and "id=\"continue-summary\"" in shell)
require("avatar choices create visibly different costume geometry", "avatar-style-costume" in game and all(color in game for color in ("#287f9d", "#33243f", "#6f493c")))
require("avatar picker previews each costume palette", all(palette in shell for palette in ('data-avatar="classic"', 'data-avatar="sport"', 'data-avatar="night"')) and ".avatar-swatch:before" in shell)
require("NPCs receive at least six deterministic visual variants", "const NPC_STYLE_PROFILES=[" in game and game.count("head:'") >= 8 and "applyNpcAppearance(root,styleIndex)" in game)
require("NPC labels shrink and fade with distance", "sprite.scale.set(.84,.21,1)" in game and "labelDistance<8" in game and "actor.label.material.opacity" in game)

print("ALL SCENE FOUNDATION CHECKS PASSED")
