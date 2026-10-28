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
    adb('forward','tcp:9341','localabstract:webview_devtools_remote_'+pid)
    endpoint='http://127.0.0.1:9341/json'
else:
    proc=subprocess.Popen([chrome_path,'--remote-debugging-port=9340','--remote-allow-origins=*',
        '--autoplay-policy=no-user-gesture-required',f'--user-data-dir={user_data}_acceptance',
        '--headless=new','--disable-gpu','--no-first-run',html_url])
    endpoint='http://127.0.0.1:9340/json'
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
        assert condition,label
        print('PASS: '+label,flush=True)
    def wait_js(expr,timeout=20):
        end=time.time()+timeout
        while time.time()<end:
            if eval_js(expr):return
            time.sleep(.2)
        raise AssertionError('Timed out: '+expr+' '+str(eval_js("({danceState,paused,song:document.getElementById('songselect').hidden})")))
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
        send_cdp('Network.enable')
        send_cdp('Network.emulateNetworkConditions',{'offline':True,'latency':0,'downloadThroughput':0,'uploadThroughput':0})
        send_cdp('Page.reload');time.sleep(.3)
    wait_js("document.body.dataset.ready==='true'",60)
    check('Cold load with offline assets',eval_js('ready&&Object.keys(EMBEDDED_ASSETS).length>0&&Object.keys(EMBEDDED_BEATMAPS).length>0'))
    if ANDROID:check('Android airplane mode enabled',adb('shell','settings','get','global','airplane_mode_on')=='1')
    def point(selector):
        return eval_js("(()=>{let r=document.querySelector("+json.dumps(selector)+").getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()")
    def touch(kind,points):
        result=send_cdp('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points})
        assert 'error' not in result,result
    def finger(selector,id=1):return dict(point(selector),id=id)
    def tap(selector):
        touch('touchStart',[finger(selector,8)]);touch('touchEnd',[]);time.sleep(.2)
    def reset():
        eval_js('resetInput();player.position.set(0,.1,3);player.rotation.y=0;resetCamera()')
    def snap():return eval_js('({x:player.position.x,z:player.position.z,yaw:player.rotation.y,orbit:cameraYaw})')
    def back():
        if ANDROID:adb('shell','input','keyevent','4')
        else:eval_js('window.meydanBack()')
        time.sleep(.25)
    reset();up=finger('.mobile-move .up');start=snap()
    touch('touchStart',[up]);samples=[]
    for _ in range(30):time.sleep(.1);samples.append(snap())
    touch('touchEnd',[])
    check('Held forward stays straight without camera feedback',max(abs(p['x']-start['x']) for p in samples)<.015 and samples[-1]['z']>start['z']+2 and max(abs(p['orbit']-start['orbit']) for p in samples)<1e-8 and abs(samples[-1]['yaw'])<.04)
    # A second finger controls orbit independently of the held movement finger.
    reset();up=finger('.mobile-move .up',2);touch('touchStart',[up])
    orbit={'x':400,'y':120,'id':3};touch('touchStart',[up,orbit])
    orbit['x']=510;touch('touchMove',[up,orbit]);time.sleep(.3)
    check('Second finger rotates while walking',eval_js('keys.w&&Math.abs(cameraYaw-Math.PI)>.3'))
    touch('touchEnd',[orbit]);check('Camera finger release preserves walk',eval_js('keys.w'))
    touch('touchEnd',[]);check('Last finger release clears walk',not eval_js('keys.w||isMouseDown'))
    up=finger('.mobile-move .up',4);right=finger('.mobile-move .right',5)
    touch('touchStart',[up]);touch('touchStart',[up,right]);check('Diagonal multi-touch',eval_js('keys.w&&keys.d'))
    touch('touchEnd',[right]);check('Independent direction release',eval_js('keys.w&&!keys.d'))
    touch('touchCancel',[]);check('Cancelled pointer clears input',not eval_js('keys.w||keys.d'))
    reset();up=finger('.mobile-move .up',6);touch('touchStart',[up]);time.sleep(.25)
    if ANDROID:
        adb('shell','input','keyevent','3');time.sleep(.5)
        adb('shell','am','start','-n','com.bahri.meydan/.MainActivity');time.sleep(.7)
    else:eval_js("window.dispatchEvent(new Event('blur'));window.meydanBackground();window.meydanForeground()")
    check('Background/foreground clears all held sources',eval_js('!keys.w&&!isMouseDown&&movePointers.size===0&&goal===null'))
    p=snap();time.sleep(.4);q=snap()
    check('No movement after returning to app',math.hypot(q['x']-p['x'],q['z']-p['z'])<.015)
    touch('touchEnd',[])
    # Focus loss / visibility loss clear input without relying on a pointerup.
    touch('touchStart',[finger('.mobile-move .up',7)])
    eval_js("window.dispatchEvent(new Event('blur'))")
    check('Blur cancels stale pointers',not eval_js('keys.w'))
    touch('touchEnd',[])
    tap('#dance');wait_js("!document.getElementById('songselect').hidden")
    back();check('Back closes song selector first',eval_js("document.getElementById('songselect').hidden&&!paused"))
    tap('#help');back();check('Back closes controls menu',eval_js("document.getElementById('pausemenu').hidden&&!paused"))
    tap('#dance');wait_js("!document.getElementById('songselect').hidden");time.sleep(.2);tap('#song-start');wait_js("danceState==='COUNTDOWN'")
    back();check('Back pauses active dance',eval_js("danceState==='PAUSED'&&!document.getElementById('dancepause').hidden"))
    back();check('Back closes dance pause without opening another menu',eval_js("danceState==='IDLE'&&document.getElementById('dancepause').hidden&&!paused"))
    tap('#dance');wait_js("!document.getElementById('songselect').hidden");time.sleep(.2);tap('#song-start');wait_js("danceState==='PLAYING'",8)
    # Freeze the game clock to test only dispatch/deduplication, with two hittable notes.
    eval_js("window.savedClock=getGameTimeSec;getGameTimeSec=()=>100;danceGame.startSec=100;danceGame.index=0;danceGame.notes=[0,0,100].map(t=>({dir:0,timeSec:t,hit:false,missed:false,el:null}));window.savedInput=input;window.scoreCalls=0;input=k=>{scoreCalls++;savedInput(k)}")
    before=eval_js('danceGame.roundScore')
    touch('touchStart',[finger('.key',9)])
    check('Dance scores on pointerdown before release',eval_js('scoreCalls===1&&danceGame.index===1&&danceGame.roundScore>'+str(before)))
    score=eval_js('danceGame.roundScore');touch('touchEnd',[]);time.sleep(.1)
    check('One touch gives one score despite compatibility click',eval_js('scoreCalls===1&&danceGame.roundScore==='+str(score)))
    eval_js('input=savedInput;getGameTimeSec=savedClock;finishDance(false)')
    back();check('Back closes result first',eval_js("danceState==='IDLE'&&document.getElementById('result').hidden&&!paused"))
    up=finger('.mobile-move .up',10);p=snap();touch('touchStart',[up]);time.sleep(.6);touch('touchEnd',[]);q=snap()
    check('Walking immediately after dance',math.hypot(q['x']-p['x'],q['z']-p['z'])>.5)
    back();check('Back without a menu opens pause',eval_js('paused'))
    back();check('Next Back dismisses pause',not eval_js('paused'))
    # Repeat offline loading after all flows, rather than relying on cached initial state.
    send_cdp('Page.reload');time.sleep(.4);wait_js("document.body.dataset.ready==='true'",60)
    check('Offline reload still loads model',eval_js('ready'))
    import base64
    name='emulator' if ANDROID else 'mobile-browser'
    wait_js("!!document.body.dataset.position");time.sleep(.5)
    shot=send_cdp('Page.captureScreenshot',{'format':'png'})
    Path('android/'+name+'-acceptance.png').write_bytes(base64.b64decode(shot['result']['data']))
    check('No uncaught JavaScript errors',not browser_errors)
    print('ALL ACCEPTANCE TESTS PASSED: '+name,flush=True)
    ws.close()
finally:
    if proc:proc.terminate()
