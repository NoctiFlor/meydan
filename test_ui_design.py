import subprocess, time, json, urllib.request
from pathlib import Path
import websocket

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data = r"C:\Users\Bahri\AppData\Local\Temp\meydan_mobile_test"
html_url = (Path(__file__).parent / "MEYDAN.html").resolve().as_uri()

import sys, os, math
ANDROID='--android' in sys.argv
ADB=Path(os.environ.get('ANDROID_SDK_ROOT',str(Path.home()/'AppData/Local/Android/Sdk')))/'platform-tools/adb.exe'
SERIAL='emulator-5554'
def adb(*args):
    return subprocess.check_output([str(ADB),'-s',SERIAL,*args],text=True, encoding='utf-8').strip()
proc=None
if ANDROID:
    adb('shell','am','force-stop','com.bahri.meydan')
    adb('shell','am','start','-W','-n','com.bahri.meydan/.MainActivity')
    pid=adb('shell','pidof','com.bahri.meydan')
    adb('forward','tcp:9349','localabstract:webview_devtools_remote_'+pid)
    endpoint='http://127.0.0.1:9349/json'
else:
    proc=subprocess.Popen([chrome_path,'--remote-debugging-port=9348','--remote-allow-origins=*',
        '--autoplay-policy=no-user-gesture-required',f'--user-data-dir={user_data}_ui_design',
        '--headless=new','--disable-gpu','--no-first-run',html_url])
    endpoint='http://127.0.0.1:9348/json'
    time.sleep(3)
try:
    for attempt in range(60):
        try:
            with urllib.request.urlopen(endpoint,timeout=3) as response: targets=json.load(response)
            if any(t.get('type')=='page' for t in targets):break
        except (OSError,ValueError):pass
        time.sleep(.5)
    else:raise RuntimeError('WebView debugging page unavailable; use --debug APK')
    target=next(t for t in targets if t.get('type')=='page')
    ws_url=target['webSocketDebuggerUrl']
    ws = websocket.create_connection(ws_url, timeout=10, suppress_origin=True)
    browser_errors=[]
    msg_counter = [0]
    def send_cdp(method, params=None):
        msg_counter[0] += 1
        curr_id = msg_counter[0]
        payload = {"id": curr_id, "method": method, "params": params or {}}
        ws.send(json.dumps(payload))
        while True:
            res = json.loads(ws.recv())
            if res.get('method') == 'Runtime.exceptionThrown': browser_errors.append(res['params'])
            if res.get('id') == curr_id:
                return res

    def eval_js(expr):
        r = send_cdp("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        if 'exceptionDetails' in r.get('result', {}):
            raise Exception(r['result']['exceptionDetails'])
        return r.get('result', {}).get('result', {}).get('value')

    import base64
    def check(label,ok):
        assert ok,label
        print('PASS: '+label,flush=True)
    def wait_js(code,timeout=35):
        until=time.time()+timeout
        while time.time()<until:
            if eval_js(code):return
            time.sleep(.15)
        raise AssertionError(code)
    send_cdp('Runtime.enable')
    send_cdp('Emulation.setDeviceMetricsOverride',{'width':915,'height':412,'deviceScaleFactor':1,'mobile':True})
    send_cdp('Emulation.setTouchEmulationEnabled',{'enabled':True,'maxTouchPoints':5})
    send_cdp('Page.reload')
    wait_js("document.body?.dataset.ready==='true'")
    time.sleep(.3)
    def at(selector):return eval_js("(()=>{let r=document.querySelector("+json.dumps(selector)+").getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()")
    def touch(kind,points):
        result=send_cdp('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points});assert 'error' not in result,result
    def tap(selector,id=8):
        touch('touchStart',[dict(at(selector),id=id)]);touch('touchEnd',[]);time.sleep(.15)
    def screenshot(name):
        shot=send_cdp('Page.captureScreenshot',{'format':'png'})
        Path('android/'+name+'.png').write_bytes(base64.b64decode(shot['result']['data']))
    check('Dance dock starts collapsed',eval_js("!dockOpen&&document.getElementById('dance-panel').hidden&&!document.getElementById('dock-open').hidden"))
    check('Map is circular and drawn from three scene buildings',eval_js("map.width===map.height&&map.dataset.buildingCount==='3'&&getComputedStyle(map).borderRadius==='50%'"))
    check('Map has real water and building footprints',eval_js("(()=>{let sea=mapPoint(0,19),roof=mapPoint(mapBuildings[0].x,mapBuildings[0].z);let a=atlas.getImageData(sea.x,sea.y,1,1).data,b=atlas.getImageData(roof.x,roof.y,1,1).data;return a[2]>a[0]&&b[0]>b[2]})()"))
    screenshot('ui-design-explore')
    tap('#dock-open')
    check('Dock opens without starting a round',eval_js("dockOpen&&danceState==='IDLE'&&!document.getElementById('confirm-beat').disabled"))
    tap('#dock-collapse');check('Collapse handle restores small tab',eval_js('!dockOpen'))
    for width,height in [(915,412),(844,390),(667,375),(568,320),(390,844),(1280,720)]:
        send_cdp('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':True})
        eval_js('setDancePanel(true)');time.sleep(.15)
        metrics=eval_js("(()=>{const names=['.identity','.map-shell','#joystick','.actions','#dance-panel'];let r=names.map(s=>{let a=document.querySelector(s).getBoundingClientRect();return {s,x:a.x,y:a.y,w:a.width,h:a.height}});let pairs=[];for(let i=0;i<r.length;i++)for(let j=i+1;j<r.length;j++)if(Math.min(r[i].x+r[i].w,r[j].x+r[j].w)>Math.max(r[i].x,r[j].x)+1&&Math.min(r[i].y+r[i].h,r[j].y+r[j].h)>Math.max(r[i].y,r[j].y)+1)pairs.push([r[i].s,r[j].s]);return {r,pairs,area:r.reduce((s,a)=>s+a.w*a.h,0)/(innerWidth*innerHeight)}})()")
        check(f'{width}x{height}: controls stay on-screen',all(r['x']>=-1 and r['y']>=-1 and r['x']+r['w']<=width+1 and r['y']+r['h']<=height+1 for r in metrics['r']))
        assert not metrics['pairs'],(width,height,metrics)
        check(f'{width}x{height}: no HUD overlaps',not metrics['pairs'])
        check(f'{width}x{height}: most of world stays visible',metrics['area']<(.31 if width<600 else .28))
    send_cdp('Emulation.setDeviceMetricsOverride',{'width':915,'height':412,'deviceScaleFactor':1,'mobile':True})
    eval_js('setDancePanel(false);resetInput();player.position.set(0,.1,3);player.rotation.y=0;resetCamera()');time.sleep(.15)
    center=at('#joystick');held=dict(x=center['x']+9,y=center['y']-25,id=1)
    touch('touchStart',[held]);time.sleep(.5)
    check('Smaller joystick retains analog movement',eval_js('player.position.z>3.3&&joystick.strength>0'))
    orbit={'x':400,'y':120,'id':2};touch('touchStart',[held,orbit]);orbit['x']=490;touch('touchMove',[held,orbit]);time.sleep(.2)
    check('Second finger still orbits independently',eval_js('Math.abs(cameraYaw-Math.PI)>.3&&joystick.strength>0'))
    touch('touchEnd',[orbit]);touch('touchEnd',[])
    check('Release clears pointer ownership',eval_js('joystickPointer===null&&joystick.strength===0'))
    time.sleep(.15)
    check('Player position updates the map',eval_js('Math.abs(Number(map.dataset.playerZ)-player.position.z)<.03'))
    tap('#dock-open');tap('#confirm-beat');wait_js("!document.getElementById('songselect').hidden")
    eval_js('meydanBack()');check('Back closes selector before dock',eval_js("document.getElementById('songselect').hidden&&dockOpen&&!paused"))
    tap('#confirm-beat');tap('#song-start');wait_js("danceState==='PLAYING'",8)
    check('Dance start opens complete golden dock',eval_js('dockOpen&&phraseEngine&&document.querySelectorAll(".phrase-arrow").length>=2'))
    eval_js('window.savedClock=getGameTimeSec;window.testTime=0;getGameTimeSec=()=>danceGame.startSec+testTime')
    dirs=eval_js('phraseEngine.directions')
    for direction in dirs:tap('.key:nth-child('+str(direction+1)+')')
    check('Direction touches do not score',eval_js('danceGame.roundScore===0&&phraseEngine.position===phraseEngine.directions.length'))
    eval_js('testTime=2;syncDance(testTime)');wait_js('stageFraming>.98');time.sleep(.2);screenshot('ui-design-dance')
    eval_js('testTime=phraseEngine.target;syncDance(testTime)')
    touch('touchStart',[dict(at('#confirm-beat'),id=9)]);time.sleep(.1)
    check('Compact confirmation scores on pointerdown',eval_js('danceGame.stats.perfect===1&&danceGame.roundScore>0'))
    score=eval_js('danceGame.roundScore');touch('touchEnd',[]);time.sleep(.1)
    check('Compatibility click never doubles score',eval_js('danceGame.roundScore==='+str(score)))
    tap('#dock-collapse');check('Collapse preserves active phrase and score',eval_js("!dockOpen&&danceState==='PLAYING'&&danceGame.roundScore==="+str(score)))
    tap('#dock-open');check('Reopening preserves progress',eval_js('dockOpen&&phraseEngine.closed&&danceGame.roundScore==='+str(score)))
    eval_js('getGameTimeSec=savedClock;finishDance(true)')
    tap('#dock-collapse');tap('#help');check('Small settings icon opens settings',eval_js('paused'))
    eval_js('meydanBack()');check('Back closes settings',eval_js('!paused'))
    check('Action icons survive state updates',eval_js("!!document.querySelector('#dance svg')&&document.getElementById('dance').getAttribute('aria-label').includes('Dans')"))
    check('No uncaught browser errors',not browser_errors)
    print('ALL LOCAL UI DESIGN CHECKS PASSED',flush=True)
    ws.close()
finally:
    if proc:proc.terminate()
