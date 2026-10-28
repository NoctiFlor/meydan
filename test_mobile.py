import subprocess, time, json, urllib.request
from pathlib import Path
import websocket

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
user_data = r"C:\Users\Bahri\AppData\Local\Temp\meydan_mobile_test"
html_url = (Path(__file__).parent / "MEYDAN.html").resolve().as_uri()

proc = subprocess.Popen([
    chrome_path,
    "--remote-debugging-port=9339",
    "--remote-allow-origins=*",
    "--autoplay-policy=no-user-gesture-required",
    f"--user-data-dir={user_data}",
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    html_url
])

time.sleep(3)

try:
    with urllib.request.urlopen("http://localhost:9339/json") as resp:
        targets = json.loads(resp.read().decode())
        page_target = next(t for t in targets if t.get('type') == 'page')
        ws_url = page_target['webSocketDebuggerUrl']

    ws = websocket.create_connection(ws_url, timeout=10)
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

    send_cdp('Runtime.enable')
    send_cdp('Emulation.setDeviceMetricsOverride', {'width':915,'height':412,'deviceScaleFactor':1,'mobile':True})
    send_cdp('Emulation.setTouchEmulationEnabled', {'enabled':True,'maxTouchPoints':5})
    send_cdp('Page.reload');time.sleep(1)
    for _ in range(60):
        if eval_js("document.body.dataset.ready === 'true'"):break
        time.sleep(.25)
    assert eval_js('ready')
    assert eval_js("getComputedStyle(document.querySelector('.mobile-move')).display==='grid'")
    eval_js('player.position.set(0,.1,5);player.rotation.y=0;resetCamera()')
    def point(selector):
        return eval_js("(()=>{let r=document.querySelector("+json.dumps(selector)+").getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()")
    def touch(kind,points):
        send_cdp('Input.dispatchTouchEvent',{'type':kind,'touchPoints':points})
    def snap():return eval_js('({x:player.position.x,z:player.position.z,yaw:cameraYaw})')
    up=dict(point('.mobile-move .up'),id=1)
    touch('touchStart',[up]);time.sleep(.7)
    p=snap();assert p['z']>5.6,p
    # Keep walking while a second finger rotates the camera on the canvas.
    orbit={'x':430,'y':140,'id':2}
    touch('touchStart',[up,orbit])
    orbit['x']=540
    touch('touchMove',[up,orbit]);time.sleep(.4)
    assert abs(snap()['yaw']-p['yaw'])>.3,'Touch camera did not rotate'
    assert eval_js('keys.w'),'Second finger interrupted movement'
    touch('touchEnd',[orbit]);time.sleep(.2)
    assert eval_js('keys.w'),'Camera finger release stopped walking'
    touch('touchEnd',[]);time.sleep(.2)
    assert not eval_js('keys.w'),'Movement stuck after release'
    print('Mobile movement, two-finger walking + camera, and release passed',flush=True)
    # Two direction buttons can be held together and released separately.
    up=dict(point('.mobile-move .up'),id=3)
    right=dict(point('.mobile-move .right'),id=4)
    touch('touchStart',[up]);touch('touchStart',[up,right]);time.sleep(.2)
    assert eval_js('keys.w&&keys.d')
    touch('touchEnd',[right]);time.sleep(.1)
    assert eval_js('keys.w&&!keys.d')
    touch('touchCancel',[]);time.sleep(.1)
    assert not eval_js('keys.w||keys.d')
    print('Diagonal movement and touch cancel passed',flush=True)
    def tap(selector):
        p=dict(point(selector),id=5)
        touch('touchStart',[p]);touch('touchEnd',[])
    tap('#dance');time.sleep(.2)
    assert eval_js("!document.getElementById('songselect').hidden")
    tap('#song-start');time.sleep(.4)
    assert eval_js("danceState==='COUNTDOWN'")
    time.sleep(3)
    assert eval_js("danceState==='PLAYING'")
    tap('.key');time.sleep(.2)
    eval_js('finishDance(false)');tap('#closeresult');time.sleep(.2)
    assert eval_js("danceState==='IDLE'")
    up=dict(point('.mobile-move .up'),id=6)
    before=snap();touch('touchStart',[up]);time.sleep(.6);touch('touchEnd',[])
    after=snap()
    assert abs(after['x']-before['x'])+abs(after['z']-before['z'])>.5
    print('Touch dance selection, countdown, playing, results and walking passed',flush=True)
    import base64
    shot=send_cdp('Page.captureScreenshot',{'format':'png'})
    Path('android/mobile-test.png').write_bytes(base64.b64decode(shot['result']['data']))
    assert not browser_errors,browser_errors
    print('ALL MOBILE BROWSER TESTS PASSED',flush=True)
    ws.close()
finally:
    proc.terminate()
