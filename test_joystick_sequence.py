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
    adb('forward','tcp:9345','localabstract:webview_devtools_remote_'+pid)
    endpoint='http://127.0.0.1:9345/json'
else:
    proc=subprocess.Popen([chrome_path,'--remote-debugging-port=9344','--remote-allow-origins=*',
        '--autoplay-policy=no-user-gesture-required',f'--user-data-dir={user_data}_sequence',
        '--headless=new','--disable-gpu','--no-first-run',html_url])
    endpoint='http://127.0.0.1:9344/json'
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

    def check(label,condition):
        if not condition:
            print(eval_js("({state:danceState,position:phraseEngine?.position,dirs:phraseEngine?.directions,closed:phraseEngine?.closed,stats:danceGame.stats,time:typeof testTime==='undefined'?null:testTime,target:phraseEngine?.target,disabled:document.getElementById('confirm-beat').disabled,rect:document.getElementById('confirm-beat').getBoundingClientRect().toJSON()})"),flush=True)
        assert condition,label
        print('PASS: '+label,flush=True)
    def wait_js(code,seconds=40):
        until=time.time()+seconds
        while time.time()<until:
            if eval_js(code):return
            time.sleep(.2)
        raise AssertionError(code)
    if ANDROID:
        import xml.etree.ElementTree as ET,re
        adb('shell','uiautomator','dump','/sdcard/meydan-ui.xml')
        ui=ET.fromstring(adb('shell','cat','/sdcard/meydan-ui.xml'))
        for node in ui.iter('node'):
            if node.get('resource-id')=='com.android.systemui:id/ok':
                bounds=list(map(int,re.findall(r'\d+',node.get('bounds'))))
                adb('shell','input','tap',str((bounds[0]+bounds[2])//2),str((bounds[1]+bounds[3])//2))
        focus=adb('shell','dumpsys','window')
        check('Native Android app owns input focus',any('mCurrentFocus=' in line and 'com.bahri.meydan' in line for line in focus.splitlines()))
    send_cdp('Runtime.enable')
    if not ANDROID:
        send_cdp('Emulation.setDeviceMetricsOverride',{'width':915,'height':412,'deviceScaleFactor':1,'mobile':True})
        send_cdp('Emulation.setTouchEmulationEnabled',{'enabled':True,'maxTouchPoints':5})
        send_cdp('Network.enable');send_cdp('Network.emulateNetworkConditions',{'offline':True,'latency':0,'downloadThroughput':0,'uploadThroughput':0})
        send_cdp('Page.reload')
    wait_js("document.body?.dataset.ready==='true'")
    def at(selector):return eval_js("(()=>{let r=document.querySelector("+json.dumps(selector)+").getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()")
    def touch(kind,points):
        r=send_cdp('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points});assert 'error' not in r,r
    def tap(selector,id=7):
        touch('touchStart',[dict(at(selector),id=id)]);touch('touchEnd',[]);time.sleep(.15)
    def reset():eval_js('resetInput();player.position.set(0,.1,3);player.rotation.y=0;resetCamera()')
    def snap():return eval_js('({x:player.position.x,z:player.position.z,yaw:player.rotation.y,orbit:cameraYaw})')
    def joy(dx,dy,id=1):
        p=at('#joystick');p.update(x=p['x']+dx,y=p['y']+dy,id=id);touch('touchStart',[p]);return p
    reset();p=snap();held=joy(13,-45);time.sleep(.7);q=snap()
    dx=q['x']-p['x'];dz=q['z']-p['z']
    check('Joystick preserves arbitrary analog angle',dx<-.2 and dz>.5 and abs(dx/dz+13/45)<.02)
    orbit={'x':400,'y':110,'id':2};touch('touchStart',[held,orbit]);orbit['x']=500;touch('touchMove',[held,orbit]);time.sleep(.3)
    check('Second finger orbits while joystick stays held',eval_js('joystick.strength>.5&&Math.abs(cameraYaw-Math.PI)>.3'))
    touch('touchEnd',[orbit]);check('Camera release does not cancel joystick',eval_js('joystick.strength>.5'))
    touch('touchEnd',[]);check('Joystick release clears movement',eval_js('joystick.strength===0&&joystickPointer===null'))
    p=snap();time.sleep(.3);q=snap();check('No drift after release',math.hypot(q['x']-p['x'],q['z']-p['z'])<.01)
    reset();joy(0,-54);samples=[]
    for _ in range(22):time.sleep(.1);samples.append(snap())
    touch('touchEnd',[])
    check('Held forward never spirals',max(abs(s['x']) for s in samples)<.015 and max(abs(s['orbit']-math.pi) for s in samples)<1e-8 and samples[-1]['z']>5)
    reset();joy(0,-22);low=eval_js('joystick.strength');touch('touchEnd',[]);joy(0,-50);high=eval_js('joystick.strength')
    check('Stick distance changes speed continuously',0<low<high<1)
    touch('touchCancel',[]);check('Pointer cancel clears stick',eval_js('joystick.strength===0'))
    reset();held=joy(0,-40)
    if ANDROID:
        adb('shell','input','keyevent','3');time.sleep(.5);adb('shell','am','start','-W','-n','com.bahri.meydan/.MainActivity');time.sleep(.7)
    else:eval_js("window.dispatchEvent(new Event('blur'));meydanBackground();meydanForeground()")
    check('Background return clears stick and camera ownership',eval_js('joystick.strength===0&&joystickPointer===null&&orbitPointerId===null'))
    touch('touchEnd',[])
    tap('#dance');wait_js("!document.getElementById('songselect').hidden");tap('#song-start');wait_js("danceState==='PLAYING'",8)
    check('Horizontal sequence exists; no falling lane UI',eval_js("document.querySelectorAll('.phrase-arrow').length>=2&&!document.querySelector('.rhythm')"))
    check('Joystick is cleared and disabled in dance',eval_js('joystick.strength===0'))
    # Freeze only the scoring clock to prove event semantics, not network/frame timing.
    eval_js('window.savedClock=getGameTimeSec;window.testTime=0;getGameTimeSec=()=>danceGame.startSec+testTime')
    before=eval_js('danceGame.roundScore')
    tap('.key')
    check('Correct direction advances without scoring',eval_js('phraseEngine.position===1&&danceGame.roundScore==='+str(before)))
    wrong=eval_js('(phraseEngine.directions[phraseEngine.position]+1)%4')
    tap('.key:nth-child('+str(wrong+1)+')')
    check('Wrong arrow resets entire input sequence',eval_js('phraseEngine.position===0'))
    dirs=eval_js('phraseEngine.directions')
    for d in dirs:tap('.key:nth-child('+str(d+1)+')')
    check('Completed sequence still needs beat confirmation',eval_js('phraseEngine.position===phraseEngine.directions.length&&danceGame.roundScore==='+str(before)))
    import base64
    shot=send_cdp('Page.captureScreenshot',{'format':'png'})
    Path('android/dance-sequence-active-'+('emulator' if ANDROID else 'browser')+'.png').write_bytes(base64.b64decode(shot['result']['data']))
    eval_js('testTime=phraseEngine.target;syncDance(testTime)')
    touch('touchStart',[dict(at('#confirm-beat'),id=11)])
    check('Confirmation scores at pointerdown',eval_js('phraseEngine.closed&&danceGame.stats.perfect===1&&danceGame.roundScore>'+str(before)))
    score=eval_js('danceGame.roundScore');touch('touchEnd',[]);time.sleep(.2)
    check('Release/click does not score twice',eval_js('danceGame.roundScore==='+str(score)+'&&danceGame.stats.perfect===1'))
    eval_js('input("ArrowLeft");confirmDance()')
    check('Settled phrase rejects repeat confirm',eval_js('danceGame.roundScore==='+str(score)))
    eval_js('testTime=8*phraseEngine.beat;syncDance(testTime)')
    dirs=eval_js('phraseEngine.directions')
    for d in dirs:tap('.key:nth-child('+str(d+1)+')')
    # Keyboard space follows the same single confirmation rule.
    eval_js('testTime=phraseEngine.target')
    send_cdp('Input.dispatchKeyEvent',{'type':'keyDown','key':' ','code':'Space','windowsVirtualKeyCode':32})
    send_cdp('Input.dispatchKeyEvent',{'type':'keyUp','key':' ','code':'Space','windowsVirtualKeyCode':32})
    check('Desktop Space confirms and advances difficulty',eval_js('danceGame.stats.perfect===2&&phraseEngine.level===2'))
    eval_js('getGameTimeSec=savedClock;pauseDanceTur()')
    check('Dance pause retains phrase input',eval_js("danceState==='PAUSED'"))
    eval_js('meydanBack()');check('Back closes dance pause',eval_js("danceState==='IDLE'"))
    reset();joy(-19,-33);time.sleep(.4);touch('touchEnd',[])
    check('Joystick resumes after dance',eval_js('player.position.z>3.2'))
    tap('#dance');eval_js('meydanBack()');check('Back dismisses selector first',eval_js("document.getElementById('songselect').hidden&&!paused"))
    if ANDROID:check('Android airplane mode',adb('shell','settings','get','global','airplane_mode_on')=='1')
    check('No uncaught browser errors',not browser_errors)
    import base64
    shot=send_cdp('Page.captureScreenshot',{'format':'png'})
    Path('android/joystick-sequence-'+('emulator' if ANDROID else 'browser')+'.png').write_bytes(base64.b64decode(shot['result']['data']))
    print('ALL JOYSTICK / SEQUENCE INTEGRATION TESTS PASSED',flush=True)
    ws.close()
finally:
    if proc:proc.terminate()
